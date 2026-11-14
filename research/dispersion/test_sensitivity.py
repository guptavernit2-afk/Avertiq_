"""Sensitivity report tests use synthetic temporary records, never ALOHA results."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import test_propylene as fixtures
import test_transcription as transcription_fixtures
from propylene import NAMES, ROOT, compare_runs, registered_case, template
from transcription import apply_transcription


class SensitivityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='SYNTHETIC-SENSITIVITY-')
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.records = {name: fixtures.PropyleneTests().observed(self.base, name) for name in NAMES}
        for index, record in enumerate(self.records.values(), start=1):
            record['warnings'] = ['SYNTHETIC warning retained; not model evidence']
            for row in record['receptors']:
                row['value_ppm'] = index * 10
            for row in record['contours']:
                row.update(downwind_m=index * row['level_ppm'], unavailable_reason=None)

    def save(self):
        for name, record in self.records.items():
            (self.base / f'{name}.json').write_text(json.dumps(record), encoding='utf-8')

    def compare(self):
        self.save()
        return compare_runs(self.base)

    def test_declared_input_changes_and_units_for_all_variants(self):
        result = self.compare()
        expected = [('rate_kg_s', 'kg/s', .1, .05), ('rate_kg_s', 'kg/s', .1, .2), ('wind_m_s', 'm/s', 2., 4.)]
        for comparison, (field, unit, baseline, variant) in zip(result['comparisons'], expected):
            self.assertEqual(comparison['changed_inputs'], [{'field': field, 'unit': unit, 'baseline': baseline, 'variant': variant}])
            self.assertEqual(comparison['comparison_blockers'], [])
        for flag in ['propylene_qualified', 'field_validated', 'dashboard_adapter_enabled']:
            self.assertIs(result[flag], False)
        for name in NAMES:
            self.assertEqual(result['runs'][name]['warnings'], self.records[name]['warnings'])
            self.assertEqual(result['runs'][name]['case_sha256'], self.records[name]['case_sha256'])

    def test_receptors_and_contours_match_by_identifier_not_row_position(self):
        # Existing inspection accepts omitted reasons for available scalars.
        for record in self.records.values():
            for group in ('receptors', 'contours'):
                for row in record[group]:
                    row.pop('unavailable_reason')
        self.records['rate-half']['receptors'].reverse()
        self.records['rate-half']['contours'].reverse()
        first = self.compare()['comparisons'][0]
        for row in first['receptor_changes']:
            self.assertEqual((row['baseline_ppm'], row['variant_ppm'], row['difference_ppm'], row['ratio']), (10, 20, 10, 2))
        for row in first['contour_changes']:
            level = row['level_ppm']
            self.assertEqual((row['baseline_m'], row['variant_m'], row['difference_m'], row['ratio']), (level, 2 * level, level, 2))
            self.assertIsNone(row['difference_unavailable_reason'])
            self.assertIsNone(row['ratio_unavailable_reason'])
        # Falling values are reported as differences, not a failed physics test.
        self.records['rate-half']['receptors'][0]['value_ppm'] = 5
        row = self.compare()['comparisons'][0]['receptor_changes'][-1]
        self.assertEqual(row['difference_ppm'], -5)
        self.assertEqual(row['ratio'], .5)

    def test_specific_blockers_withhold_both_output_groups(self):
        self.records['rate-half']['dispersion_method'] = 'Heavy Gas'
        self.records['rate-double'].pop('output_semantics')
        self.records['rate-double']['basis']['averaging_description'] = 'SYNTHETIC different averaging'
        comparisons = self.compare()['comparisons']
        self.assertEqual(comparisons[0]['comparison_blockers'], ['dispersion_method_mismatch'])
        self.assertEqual(comparisons[1]['comparison_blockers'], ['output_basis_mismatch', 'variant_output_semantics_missing'])
        for item in comparisons[:2]:
            self.assertFalse(item['comparable_basis'])
            self.assertEqual(item['receptor_changes'], [])
            self.assertEqual(item['contour_changes'], [])
            self.assertTrue(item['changed_inputs'])
        self.records['baseline'].pop('output_semantics')
        for item in self.compare()['comparisons']:
            self.assertIn('baseline_output_semantics_missing', item['comparison_blockers'])
            self.assertEqual(item['contour_changes'], [])

    def test_missing_outputs_keep_each_side_reason_and_never_become_zero(self):
        for group, field in [('receptors', 'value_ppm'), ('contours', 'downwind_m')]:
            for index, sides in enumerate([('baseline',), ('rate-half',), ('baseline', 'rate-half')]):
                for side in sides:
                    self.records[side][group][index].update({field: None, 'unavailable_reason': f'SYNTHETIC {side} unavailable'})
        result = self.compare()['comparisons'][0]
        for group, unit in [('receptor_changes', 'ppm'), ('contour_changes', 'm')]:
            for row, reason in zip(result[group], ['baseline_unavailable', 'variant_unavailable', 'baseline_and_variant_unavailable']):
                self.assertIsNone(row[f'difference_{unit}'])
                self.assertIsNone(row['ratio'])
                self.assertEqual(row['difference_unavailable_reason'], reason)
                self.assertEqual(row['ratio_unavailable_reason'], reason)
                self.assertTrue(row['baseline_unavailable_reason'] or row['variant_unavailable_reason'])

    def test_transcribed_bounds_remain_visible_without_point_estimates(self):
        factory = transcription_fixtures.TranscriptionTests()
        factory.base = self.base
        for name in NAMES:
            record = factory.record(name)
            factory.item(record, 'receptor.50.value_ppm').update(value_text='10', relation='lt', reason='SYNTHETIC reporting bound')
            factory.item(record, 'contour.1000.downwind_m').update(value_text='10', unit='km', relation='gt', reason='SYNTHETIC distance limit')
            self.records[name] = apply_transcription(registered_case(name), record)
            # Equivalent float identifiers must still locate the transcription.
            self.records[name]['contours'][0]['level_ppm'] = 1000.0
        for item in self.compare()['comparisons']:
            receptor, contour = item['receptor_changes'][0], item['contour_changes'][0]
            for side in ['baseline', 'variant']:
                self.assertEqual(receptor[f'{side}_reporting_bound'], {'relation': 'lt', 'bound_value': 10., 'unit': 'ppm'})
                self.assertEqual(contour[f'{side}_reporting_bound'], {'relation': 'gt', 'bound_value': 10000., 'unit': 'm'})
                self.assertIsNone(contour[f'{side}_m'])
            self.assertIsNone(contour['difference_m'])
            self.assertIsNone(contour['ratio'])

    def test_zero_baselines_and_zero_variants_are_distinct(self):
        for group, value_key in [('receptors', 'value_ppm'), ('contours', 'downwind_m')]:
            self.records['baseline'][group][0][value_key] = 0
            self.records['rate-half'][group][1][value_key] = 0
        result = self.compare()['comparisons'][0]
        for group, unit in [('receptor_changes', 'ppm'), ('contour_changes', 'm')]:
            zero_base, zero_variant = result[group][:2]
            self.assertIsNone(zero_base['ratio'])
            self.assertEqual(zero_base['ratio_unavailable_reason'], 'zero_baseline')
            self.assertGreater(zero_base[f'difference_{unit}'], 0)
            self.assertEqual(zero_variant['ratio'], 0)
            self.assertIsNone(zero_variant['ratio_unavailable_reason'])

    def test_extreme_ratios_are_null_with_reason_and_json_stays_finite(self):
        for group, value_key in [('receptors', 'value_ppm'), ('contours', 'downwind_m')]:
            self.records['baseline'][group][0][value_key] = 5e-324
            self.records['rate-half'][group][0][value_key] = 1e6
            self.records['baseline'][group][1][value_key] = 1e6
            self.records['rate-half'][group][1][value_key] = 5e-324
        result = self.compare()
        json.dumps(result, allow_nan=False)
        for group in ['receptor_changes', 'contour_changes']:
            for row in result['comparisons'][0][group][:2]:
                self.assertIsNone(row['ratio'])
                self.assertEqual(row['ratio_unavailable_reason'], 'ratio_outside_float_range')

    def test_cli_report_is_additive_preserves_inputs_and_rejects_unrun(self):
        self.save()
        before = {p: p.read_bytes() for p in self.base.iterdir() if p.is_file()}
        output = self.base / 'comparison.json'
        command = [sys.executable, str(ROOT / 'propylene.py'), 'compare-runs', '--runs-dir', str(self.base), '--output', str(output)]
        run = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(output.read_text(encoding='utf-8'))
        self.assertEqual(len(result['comparisons'][0]['contour_changes']), 3)
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)
        first = output.read_bytes()
        self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
        self.assertEqual(output.read_bytes(), first)
        self.records['baseline'] = template(registered_case('baseline'))
        self.save()
        rejected = self.base / 'rejected.json'
        self.assertNotEqual(subprocess.run(command[:-1] + [str(rejected)], capture_output=True).returncode, 0)
        self.assertFalse(rejected.exists())


if __name__ == '__main__':
    unittest.main()
