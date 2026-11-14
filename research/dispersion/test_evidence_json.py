"""Strict JSON intake tests use disposable synthetic records, never model output."""
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import archive
import test_propylene as propylene_fixtures
import test_qualify as reference_fixtures
import test_transcription as transcription_fixtures
from qualify import ROOT, case_hash, read_json
from propylene import NAMES


class EvidenceJsonTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='SYNTHETIC-JSON-')
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.source = self.base / 'record.json'

    def assert_rejected_by_both_readers(self, text, message):
        self.source.write_text(text, encoding='utf-8')
        before = self.source.read_bytes()
        with self.assertRaisesRegex(ValueError, message):
            read_json(self.source)
        with self.assertRaisesRegex(ValueError, message):
            archive.decode(before)
        self.assertEqual(self.source.read_bytes(), before)

    def test_duplicate_fields_including_nested_and_escaped_names_rejected(self):
        for text in [
            '{"synthetic_test_data": true, "synthetic_test_data": false}',
            '{"engine": {"version": "wrong", "version": "5.4.7"}}',
            '{"rows": [{"value_ppm": null, "value_ppm": 0}]}',
            r'{"run_completed": false, "run_\u0063ompleted": true}',
            '{"value_ppm": 1, "value_ppm": 1}',
        ]:
            with self.subTest(text=text):
                self.assert_rejected_by_both_readers(text, 'Duplicate JSON key')

    def test_nonfinite_and_overflow_tokens_rejected_even_in_unused_metadata(self):
        for token in ['NaN', 'Infinity', '-Infinity', '1e309', '-1e999']:
            with self.subTest(token=token):
                self.assert_rejected_by_both_readers('{"metadata": [{"value": ' + token + '}]}', 'Non-finite JSON')

    def test_nonzero_underflow_cannot_silently_become_zero(self):
        for token in ['1e-999', '-1e-999', '0.0001e-999', '2e-324']:
            with self.subTest(token=token):
                self.assert_rejected_by_both_readers('{"value_ppm": ' + token + '}', 'underflow')

    def test_valid_values_and_repeated_names_in_separate_objects_remain_supported(self):
        text = '{"rows":[{"value":0},{"value":0.0},{"value":-0.0},{"value":0e-999},{"value":5e-324}],"large":1e308,"missing":null,"note":"NaN 1e-999","flag":false}'
        self.source.write_text(text, encoding='utf-8')
        result = read_json(self.source)
        self.assertEqual(result, archive.decode(text.encode()))
        self.assertGreater(result['rows'][-1]['value'], 0)
        self.assertTrue(math.isfinite(result['large']))
        self.assertEqual(case_hash(result), case_hash(json.loads(text)))
        self.assertIs(result['missing'], None)
        self.assertIs(result['flag'], False)

    def test_invalid_roots_and_malformed_json_rejected(self):
        for text in ['[]', 'null', 'true', '0', '"text"']:
            self.assert_rejected_by_both_readers(text, 'Expected a JSON object')
        for text in ['{"x":1,}', '{"x":01}', '{"x":1} trailing']:
            self.assert_rejected_by_both_readers(text, '.')

    def run_rejected_cli(self, module, args, output, error):
        before = self.source.read_bytes()
        result = subprocess.run([sys.executable, str(ROOT / module), *args, '--output', str(output)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(error, result.stderr)
        self.assertFalse(output.exists())
        self.assertEqual(self.source.read_bytes(), before)

    def test_duplicate_synthetic_flag_rejected_by_all_observation_commands(self):
        fixture = transcription_fixtures.TranscriptionTests()
        fixture.base = self.base
        record = fixture.record()
        ambiguous = json.dumps(record).replace('"synthetic_test_data": false', '"synthetic_test_data": true, "synthetic_test_data": false')
        self.source.write_text(ambiguous, encoding='utf-8')
        for command in ['inspect-run', 'normalize-run']:
            self.run_rejected_cli('propylene.py', [command, '--observed', str(self.source)], self.base / (command + '.json'), 'Duplicate JSON key')
        self.run_rejected_cli('archive.py', ['archive-run', '--case', 'baseline', '--observed', str(self.source)], self.base / 'bad.avertiq-evidence.zip', 'Duplicate JSON key')
        for name in NAMES:
            value = propylene_fixtures.PropyleneTests().observed(self.base, name)
            text = ambiguous if name == 'baseline' else json.dumps(value)
            (self.base / (name + '.json')).write_text(text, encoding='utf-8')
        self.run_rejected_cli('propylene.py', ['compare-runs', '--runs-dir', str(self.base)], self.base / 'comparison.json', 'Duplicate JSON key')
        reference = reference_fixtures.QualificationTests()
        reference.setUp()
        text = json.dumps(reference.observed(self.base)).replace('"synthetic_test_data": false', '"synthetic_test_data": true, "synthetic_test_data": false')
        self.source.write_text(text, encoding='utf-8')
        self.run_rejected_cli('qualify.py', ['compare-reference', '--observed', str(self.source)], self.base / 'reference.json', 'Duplicate JSON key')

    def test_underflow_receptor_rejected_before_report_creation(self):
        record = propylene_fixtures.PropyleneTests().observed(self.base)
        text = json.dumps(record).replace('"value_ppm": 1', '"value_ppm": 1e-999', 1)
        self.source.write_text(text, encoding='utf-8')
        self.run_rejected_cli('propylene.py', ['inspect-run', '--observed', str(self.source)], self.base / 'inspection.json', 'underflow')


if __name__ == '__main__':
    unittest.main()
