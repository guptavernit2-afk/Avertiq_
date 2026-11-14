"""Synthetic capture metadata tests; no actual model output or physics results."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import test_propylene as fixtures
from output_semantics import EXPECTED, semantics_template, review_output_semantics
from propylene import inspect_run, compare_runs, registered_case, NAMES
from qualify import ROOT, read_json
from archive import archive_run, verify_archive, provenance


class OutputSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='SYNTHETIC-SEMANTICS-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def record(self, name='baseline'):
        return fixtures.PropyleneTests().observed(self.base, name)

    def test_supported_metadata_keeps_exact_interval_and_physics_pending(self):
        for name in NAMES:
            result = inspect_run(registered_case(name), self.record(name), self.base)
            review = result['output_semantics_review']
            self.assertTrue(review['same_engine_comparison_eligible'])
            self.assertIsNone(review['recorded']['averaging_seconds'])
            for field in ('exact_averaging_interval_verified', 'instantaneous_peak_available', 'time_animation_supported'):
                self.assertIs(review[field], False)
            self.assertTrue(review['human_evidence_review_required'])
            self.assertFalse(result['propylene_qualified'])
            self.assertFalse(result['dashboard_adapter_enabled'])
            self.assertIn('output_height_and_time_basis', result['open_mapping_gates'])

    def test_legacy_records_inspect_but_cannot_supply_numeric_comparisons(self):
        for name in NAMES:
            record = self.record(name)
            record.pop('output_semantics')
            result = inspect_run(registered_case(name), record, self.base)
            self.assertEqual(result['output_semantics_review']['status'], 'structured_output_semantics_missing')
            (self.base / f'{name}.json').write_text(json.dumps(record), encoding='utf-8')
        result = compare_runs(self.base)
        self.assertTrue(all(not c['comparable_basis'] and not c['receptor_changes'] for c in result['comparisons']))

    def test_first_hour_is_not_release_duration_and_point_maximum_is_not_instantaneous(self):
        edits = [('window_end_s', 600), ('window_start_s', 600),
                 ('receptor_statistic', 'instantaneous_peak'), ('receptor_statistic', 'mean_over_first_hour'),
                 ('receptor_environment', 'indoor'), ('receptor_coordinates', 'fixed_east_north'),
                 ('receptor_height_m', 2), ('contour_statistic', 'snapshot_at_600_s'),
                 ('threshold_use', 'evacuation_limit'), ('averaging_basis', 'flammable_10_seconds'),
                 ('averaging_seconds', 300)]
        for key, value in edits:
            with self.subTest(key=key, value=value):
                record = self.record()
                record['output_semantics'][key] = value
                with self.assertRaises(ValueError): inspect_run(registered_case('baseline'), record, self.base)

    def test_schema_missing_invalid_numeric_and_contradictory_text_are_rejected(self):
        for key, value in [('schema_version', True), ('schema_version', 2), ('window_start_s', False),
                           ('window_end_s', '3600'), ('window_end_s', float('nan')), ('status', 'unconfirmed'),
                           ('capture_notes', ''), ('averaging_seconds', 0)]:
            record = self.record()
            record['output_semantics'][key] = value
            with self.assertRaises(ValueError): inspect_run(registered_case('baseline'), record, self.base)
        for key in EXPECTED:
            record = self.record()
            del record['output_semantics'][key]
            with self.assertRaises(ValueError): review_output_semantics(record)
        for key in ('statistic', 'averaging_description', 'time_window_description'):
            record = self.record()
            record['basis'][key] = 'Contradictory synthetic description'
            with self.assertRaises(ValueError): inspect_run(registered_case('baseline'), record, self.base)

    def test_raw_evidence_reference_is_required_and_must_be_checked(self):
        for refs in ([], ['unknown'], [True], ['x', 'x']):
            record = self.record()
            record['output_semantics']['evidence_sha256'] = refs
            with self.assertRaises(ValueError): inspect_run(registered_case('baseline'), record, self.base)
        record = self.record()
        record['evidence_files'][0]['sha256'] = 'changed'
        record['output_semantics']['evidence_sha256'] = ['changed']
        with self.assertRaises(ValueError): inspect_run(registered_case('baseline'), record, self.base)

    def test_semantics_comparisons_ignore_capture_notes_but_not_missing_metadata(self):
        for name in NAMES:
            record = self.record(name)
            record['output_semantics']['capture_notes'] += f' Different synthetic capture for {name}'
            if name == 'rate-double': record.pop('output_semantics')
            (self.base / f'{name}.json').write_text(json.dumps(record), encoding='utf-8')
        results = compare_runs(self.base)['comparisons']
        self.assertEqual([r['comparable_basis'] for r in results], [True, False, True])
        self.assertEqual(results[1]['receptor_changes'], [])

    def test_unrun_supplement_is_null_and_not_accepted_as_observed(self):
        template = read_json(ROOT / 'templates/output-semantics-unrun.json')
        self.assertEqual(template, semantics_template())
        self.assertTrue(all(template[key] is None for key in EXPECTED))
        record = self.record()
        record['output_semantics'] = template
        with self.assertRaises(ValueError): inspect_run(registered_case('baseline'), record, self.base)
        output = self.base / 'template.json'
        command = [sys.executable, str(ROOT / 'propylene.py'), 'output-semantics-template', '--output', str(output)]
        run = subprocess.run(command, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(read_json(output), template)
        before = output.read_bytes()
        self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
        self.assertEqual(output.read_bytes(), before)

    def test_archive_preserves_and_pins_semantics_review_dependencies(self):
        original = self.record()
        before = copy.deepcopy(original)
        path = self.base / 'record.json'
        path.write_text(json.dumps(original), encoding='utf-8')
        output = self.base / 'test.avertiq-evidence.zip'
        receipt = archive_run('baseline', path, output)
        self.assertTrue(verify_archive(output, receipt['archive_sha256'])['record_reinspection_passed'])
        self.assertEqual(original, before)
        self.assertIn('output_semantics.py', provenance()['tool_sha256_lf_utf8'])
        self.assertIn('output-semantics-evidence.json', provenance()['configuration_snapshots'])


if __name__ == '__main__':
    unittest.main()
