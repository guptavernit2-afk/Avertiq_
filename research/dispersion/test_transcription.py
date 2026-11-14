"""Synthetic unit and censoring checks; no actual ALOHA run or observation."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
import test_propylene as fixtures
from transcription import normalize_reading, transcription_template, apply_transcription, review_transcription
from propylene import NAMES, registered_case, inspect_run, compare_runs
from qualify import ROOT, read_json
from archive import archive_run, verify_archive, provenance


class TranscriptionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='SYNTHETIC-UNITS-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def record(self, name='baseline'):
        case = registered_case(name)
        record = fixtures.PropyleneTests().observed(self.base, name)
        block = transcription_template(case)
        block['status'] = 'recorded_from_output'
        for item in block['items']:
            target = item['target']
            if target == 'source_summary.airborne_mass_kg':
                value, unit = str(case['source']['rate_kg_s'] * 600 * 1000), 'g'
            elif target == 'source_summary.duration_s': value, unit = '10.0', 'min'
            elif target.startswith('receptor'): value, unit = '1.00', 'ppm'
            else: value, unit = None, None
            item.update(value_text=value, unit=unit, relation='reported' if value is not None else 'unavailable',
                        reason=None if value is not None else 'SYNTHETIC unavailable contour',
                        evidence_sha256=record['evidence_files'][0]['sha256'], evidence_location='SYNTHETIC fixture line; not observed output')
        record['transcription'] = block
        return record

    def item(self, record, target):
        return next(row for row in record['transcription']['items'] if row['target'] == target)

    def test_known_conversions_and_no_added_precision_claim(self):
        for quantity, token, unit, expected in [('length', '166', 'yd', 151.7904), ('length', '1.00', 'mi', 1609.344),
                                                ('length', '1', 'ft', .3048), ('mass', '2', 'lb', .90718474),
                                                ('mass', '60000', 'g', 60), ('time', '10', 'min', 600),
                                                ('time', '1', 'h', 3600), ('concentration', '1e3', 'ppm', 1000)]:
            item = {'value_text': token, 'unit': unit, 'relation': 'reported', 'reason': None}
            result = normalize_reading(quantity, item)
            self.assertEqual(result['value'], expected)
            self.assertIn('does not increase', result['precision_note'])
            self.assertEqual(item['value_text'], token)

    def test_all_cases_normalize_without_mutating_source_or_closing_gates(self):
        for name in NAMES:
            case = registered_case(name)
            record = self.record(name)
            record.update(propylene_qualified=True, field_validated=True, dashboard_adapter_enabled=True)
            before = copy.deepcopy(record)
            result = apply_transcription(case, record)
            checked = inspect_run(case, result, self.base)
            self.assertEqual(record, before)
            self.assertEqual(result['source_summary']['duration_s'], 600)
            self.assertEqual(result['source_summary']['airborne_mass_kg'], case['source']['rate_kg_s'] * 600)
            self.assertEqual(checked['unit_transcription_review']['status'], 'raw_unit_transcription_consistent')
            self.assertFalse(checked['propylene_qualified'])
            self.assertFalse(checked['dashboard_adapter_enabled'])
            for flag in ('propylene_qualified', 'field_validated', 'dashboard_adapter_enabled'):
                self.assertIs(result[flag], False)

    def test_bounds_are_preserved_as_bounds_not_scalar_values(self):
        for relation in ('gt', 'ge', 'lt', 'le'):
            record = self.record()
            self.item(record, 'contour.1000.downwind_m').update(value_text='10', unit='km', relation=relation, reason='SYNTHETIC reporting limit')
            result = apply_transcription(registered_case('baseline'), record)
            report = inspect_run(registered_case('baseline'), result, self.base)
            row = report['unit_transcription_review']['conversions']['contour.1000.downwind_m']
            self.assertIsNone(result['contours'][0]['downwind_m'])
            self.assertEqual(row['bound_value'], 10000)
            self.assertEqual(row['relation'], relation)
            self.assertIn('reporting limit', result['contours'][0]['unavailable_reason'])

    def test_bound_to_exact_or_zero_substitution_is_rejected(self):
        record = self.record()
        self.item(record, 'receptor.50.value_ppm').update(value_text='10', relation='lt', reason='SYNTHETIC lower display limit')
        result = apply_transcription(registered_case('baseline'), record)
        for value in (0, 10):
            altered = copy.deepcopy(result)
            altered['receptors'][0].update(value_ppm=value, unavailable_reason=None)
            with self.assertRaises(ValueError): inspect_run(registered_case('baseline'), altered, self.base)
        altered = copy.deepcopy(result)
        altered['receptors'][0]['unavailable_reason'] = 'Changed reason'
        with self.assertRaises(ValueError): inspect_run(registered_case('baseline'), altered, self.base)

    def test_censored_receptors_never_produce_ratios(self):
        for name in NAMES:
            record = self.record(name)
            self.item(record, 'receptor.50.value_ppm').update(value_text='10', relation='lt', reason='SYNTHETIC below reporting bound')
            result = apply_transcription(registered_case(name), record)
            (self.base / f'{name}.json').write_text(json.dumps(result), encoding='utf-8')
        for comparison in compare_runs(self.base)['comparisons']:
            self.assertTrue(comparison['comparable_basis'])
            self.assertIsNone(comparison['receptor_changes'][0]['difference_ppm'])
            self.assertIsNone(comparison['receptor_changes'][0]['ratio'])

    def test_units_tokens_and_nonfinite_or_ambiguous_values_rejected(self):
        for unit in ('mg/m3', '%LEL', '%', 'ppb', 'kg', 'unknown'):
            with self.assertRaises(ValueError):
                normalize_reading('concentration', {'value_text': '1', 'unit': unit, 'relation': 'reported', 'reason': None})
        for token in (True, 1, None, '-1', 'NaN', 'Infinity', '>10', '1,000', '10 km', '1e999', '1e-999', '0' * 81):
            with self.assertRaises(ValueError):
                normalize_reading('length', {'value_text': token, 'unit': 'm', 'relation': 'reported', 'reason': None})
        for unit in ('ton', 'lb_troy', 'ft_survey'):
            with self.assertRaises(ValueError):
                normalize_reading('mass', {'value_text': '1', 'unit': unit, 'relation': 'reported', 'reason': None})

    def test_missing_qualifiers_reasons_or_impossible_ppm_are_rejected(self):
        for relation, value, reason in [(None, '1', None), ('unavailable', '1', 'reason'),
                                        ('unavailable', None, ''), ('gt', '1', None), ('reported', '1', 'contradiction'),
                                        ('reported', '1000001', None), ('gt', '1000000', 'reason'), ('lt', '0', 'reason')]:
            with self.assertRaises(ValueError):
                normalize_reading('concentration', {'value_text': value, 'unit': 'ppm', 'relation': relation, 'reason': reason})

    def test_complete_unique_evidence_linked_inventory_required(self):
        for mutation in ('duplicate', 'missing', 'unknown_target', 'bad_hash', 'missing_locator', 'source_bound', 'unconfirmed'):
            record = self.record()
            items = record['transcription']['items']
            if mutation == 'duplicate': items[1] = copy.deepcopy(items[0])
            if mutation == 'missing': items.pop()
            if mutation == 'unknown_target': items[0]['target'] = 'arbitrary.path'
            if mutation == 'bad_hash': items[0]['evidence_sha256'] = 'unknown'
            if mutation == 'missing_locator': items[0]['evidence_location'] = ''
            if mutation == 'source_bound': items[0].update(relation='gt', reason='SYNTHETIC limit')
            if mutation == 'unconfirmed': record['transcription']['status'] = 'unconfirmed'
            with self.assertRaises(ValueError): apply_transcription(registered_case('baseline'), record)

    def test_legacy_records_remain_explicitly_unreviewed_for_raw_units(self):
        record = fixtures.PropyleneTests().observed(self.base)
        result = inspect_run(registered_case('baseline'), record, self.base)
        self.assertEqual(result['unit_transcription_review']['status'], 'raw_unit_transcription_not_supplied')
        self.assertIsNone(result['raw_unit_transcription'])
        self.assertFalse(result['propylene_qualified'])

    def test_normalization_cli_verifies_evidence_and_refuses_overwrite_or_relocation(self):
        record = self.record()
        source, output = self.base / 'source.json', self.base / 'normalized.json'
        source.write_text(json.dumps(record), encoding='utf-8')
        original = source.read_bytes()
        command = [sys.executable, str(ROOT / 'propylene.py'), 'normalize-run', '--observed', str(source), '--output', str(output)]
        run = subprocess.run(command, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(source.read_bytes(), original)
        before = output.read_bytes()
        self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
        self.assertEqual(output.read_bytes(), before)
        elsewhere = self.base / 'other/normalized.json'
        self.assertNotEqual(subprocess.run(command[:-1] + [str(elsewhere)], capture_output=True).returncode, 0)
        self.assertFalse(elsewhere.exists())
        source.write_text(json.dumps({**record, 'run_completed': False}), encoding='utf-8')
        rejected = self.base / 'rejected.json'
        self.assertNotEqual(subprocess.run(command[:-1] + [str(rejected)], capture_output=True).returncode, 0)
        self.assertFalse(rejected.exists())

    def test_archive_retains_raw_tokens_qualifiers_and_conversion_provenance(self):
        record = self.record()
        self.item(record, 'contour.1000.downwind_m').update(value_text='10.0', unit='km', relation='gt', reason='SYNTHETIC range limit')
        normalized = apply_transcription(registered_case('baseline'), record)
        source, output = self.base / 'normalized.json', self.base / 'bundle.avertiq-evidence.zip'
        source.write_text(json.dumps(normalized), encoding='utf-8')
        receipt = archive_run('baseline', source, output)
        self.assertTrue(verify_archive(output, receipt['archive_sha256'])['record_reinspection_passed'])
        with zipfile.ZipFile(output) as z:
            saved = json.loads(z.read('inspection.json'))
        self.assertEqual(saved['raw_unit_transcription'], record['transcription'])
        self.assertEqual(saved['unit_transcription_review']['conversions']['contour.1000.downwind_m']['bound_value'], 10000)
        self.assertIn('transcription.py', provenance()['tool_sha256_lf_utf8'])
        self.assertIn('unit-conversion-evidence.json', provenance()['configuration_snapshots'])

    def test_unconfirmed_template_contains_no_observed_values(self):
        case = registered_case('baseline')
        expected = transcription_template(case)
        self.assertEqual(expected['status'], 'unconfirmed')
        self.assertEqual(len(expected['items']), 9)
        self.assertTrue(all(item['value_text'] is None and item['relation'] is None for item in expected['items']))
        output = self.base / 'template.json'
        command = [sys.executable, str(ROOT / 'propylene.py'), 'transcription-template', '--output', str(output)]
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
        self.assertEqual(read_json(output), expected)


if __name__ == '__main__':
    unittest.main()
