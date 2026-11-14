"""Explicit reinspection tests use disposable synthetic archives only."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import archive
import test_propylene as fixtures
from propylene import NAMES, registered_case
from qualify import ROOT, case_hash


class ReinspectionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='SYNTHETIC-REINSPECTION-')
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.source = self.base / 'record.json'
        self.bundle = self.base / 'run.avertiq-evidence.zip'
        self.output = self.base / 'receipt.json'

    def create(self, variant='baseline', old=False):
        record = fixtures.PropyleneTests().observed(self.base, variant)
        record['warnings'] = ['SYNTHETIC warning preserved']
        record['receptors'][0].update(value_ppm=None, unavailable_reason='SYNTHETIC unavailable')
        self.source.write_bytes(archive.encode(record))
        if old:
            historical = copy.deepcopy(archive.provenance())
            historical['tool_sha256_lf_utf8']['qualify.py'] = '0' * 64
            historical['configuration_snapshots']['mapping-evidence.json']['synthetic_old_review_note'] = 'SYNTHETIC old configuration'
            with patch('archive.provenance', return_value=historical):
                return archive.archive_run(variant, self.source, self.bundle)
        return archive.archive_run(variant, self.source, self.bundle)

    def members(self):
        with zipfile.ZipFile(self.bundle) as stream:
            return {name: stream.read(name) for name in stream.namelist()}

    def rewrite(self, mutate, update_hashes=True):
        members = self.members()
        mutate(members)
        if update_hashes:
            manifest = archive.decode(members['manifest.json'])
            manifest['files'] = {name: {'sha256': archive.digest(data), 'bytes': len(data)} for name, data in members.items() if name != 'manifest.json'}
            members['manifest.json'] = archive.encode(manifest)
        with zipfile.ZipFile(self.bundle, 'w', compression=zipfile.ZIP_STORED) as stream:
            for name, data in members.items():
                stream.writestr(name, data)

    def test_current_archives_all_variants_get_separate_receipts_without_promotion(self):
        for variant in NAMES:
            self.bundle = self.base / f'{variant}.avertiq-evidence.zip'
            self.output = self.base / f'{variant}-receipt.json'
            created = self.create(variant)
            before = self.bundle.read_bytes()
            result = archive.reinspect_archive(self.bundle, self.output, created['archive_sha256'])
            self.assertEqual(self.bundle.read_bytes(), before)
            self.assertEqual(result, archive.decode(self.output.read_bytes()))
            self.assertTrue(result['external_hash_matched'])
            self.assertTrue(result['historical_provenance_matches_current'])
            self.assertFalse(result['inspection_changed'])
            self.assertEqual(result['current_inspection_sha256'], result['historical_inspection_sha256'])
            self.assertEqual(result['case_sha256'], case_hash(registered_case(variant)))
            for flag in [*archive.FLAGS, 'model_executed_by_archive_tool', 'historical_archive_modified']:
                self.assertIs(result[flag], False)

    def test_drifted_code_configuration_and_report_are_rechecked_without_rewriting_history(self):
        self.create(old=True)
        def historical_label(members):
            report = archive.decode(members['inspection.json'])
            report['label'] = 'SYNTHETIC previous checker wording'
            members['inspection.json'] = archive.encode(report)
        self.rewrite(historical_label)
        before = self.bundle.read_bytes()
        members = self.members()
        self.assertFalse(archive.verify_archive(self.bundle)['record_reinspection_passed'])
        result = archive.reinspect_archive(self.bundle, self.output)
        self.assertTrue(result['record_reinspection_passed'])
        self.assertTrue(result['inspection_changed'])
        self.assertFalse(result['historical_provenance_matches_current'])
        self.assertFalse(result['external_hash_matched'])
        self.assertEqual(result['historical_inspection_sha256'], case_hash(archive.decode(members['inspection.json'])))
        self.assertEqual(result['historical_provenance_sha256'], case_hash(archive.decode(members['provenance.json'])))
        self.assertEqual(result['current_provenance_sha256'], case_hash(archive.provenance()))
        self.assertEqual(result['current_inspection_sha256'], case_hash(result['current_inspection']))
        self.assertEqual(result['current_inspection']['warnings'], ['SYNTHETIC warning preserved'])
        self.assertIsNone(result['current_inspection']['receptors'][0]['value_ppm'])
        self.assertEqual(self.bundle.read_bytes(), before)
        # Explicit reinspection does not silently upgrade ordinary verification.
        self.assertFalse(archive.verify_archive(self.bundle)['record_reinspection_passed'])

    def test_record_rejected_by_current_rules_cannot_get_success_receipt(self):
        self.create(old=True)
        def remove_warnings(members):
            for name in ['observed-original.json', 'observed.json']:
                record = archive.decode(members[name])
                record['warnings'] = None
                members[name] = archive.encode(record)
        self.rewrite(remove_warnings)
        before = self.bundle.read_bytes()
        self.assertTrue(archive.verify_archive(self.bundle)['integrity_checks_passed'])
        destination = self.base / 'new' / 'rejected.json'
        with self.assertRaisesRegex(ValueError, 'warnings'):
            archive.reinspect_archive(self.bundle, destination)
        self.assertFalse(destination.parent.exists())
        self.assertEqual(self.bundle.read_bytes(), before)

    def test_changed_frozen_case_is_not_silently_remapped(self):
        self.create(old=True)
        changed = copy.deepcopy(registered_case('baseline'))
        changed['source']['rate_kg_s'] = .9
        with patch('archive.registered_case', return_value=changed):
            with self.assertRaisesRegex(ValueError, 'Archived case differs'):
                archive.reinspect_archive(self.bundle, self.output)
        self.assertFalse(self.output.exists())

    def test_corruption_and_wrong_independent_hash_are_rejected(self):
        self.create(old=True)
        with self.assertRaisesRegex(ValueError, 'independently retained'):
            archive.reinspect_archive(self.bundle, self.output, '0' * 64)
        self.assertFalse(self.output.exists())
        self.rewrite(lambda members: members.__setitem__('evidence/0000.bin', b'SYNTHETIC tamper'), update_hashes=False)
        with self.assertRaisesRegex(ValueError, 'inventory mismatch'):
            archive.reinspect_archive(self.bundle, self.output)
        self.assertFalse(self.output.exists())

    def test_existing_receipt_and_wrong_suffix_are_refused(self):
        self.create(old=True)
        self.output.write_text('KEEP RECEIPT', encoding='utf-8')
        before = self.bundle.read_bytes()
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            archive.reinspect_archive(self.bundle, self.output)
        self.assertEqual(self.output.read_text(), 'KEEP RECEIPT')
        with self.assertRaisesRegex(ValueError, '.json destination'):
            archive.reinspect_archive(self.bundle, self.base / 'wrong.zip')
        self.assertFalse((self.base / 'wrong.zip').exists())
        self.assertEqual(self.bundle.read_bytes(), before)

    def test_provenance_change_during_check_leaves_no_receipt(self):
        self.create(old=True)
        current = archive.provenance()
        changed = copy.deepcopy(current)
        changed['tool_sha256_lf_utf8']['qualify.py'] = '1' * 64
        with patch('archive.provenance', side_effect=[current, current, changed]):
            with self.assertRaisesRegex(ValueError, 'changed during reinspection'):
                archive.reinspect_archive(self.bundle, self.output)
        self.assertFalse(self.output.exists())

    def test_cli_writes_receipt_and_keeps_archive_and_existing_output_intact(self):
        created = self.create(old=True)
        before = self.bundle.read_bytes()
        command = [sys.executable, str(ROOT / 'archive.py'), 'reinspect-archive', '--archive', str(self.bundle), '--expected-sha256', created['archive_sha256'], '--output', str(self.output)]
        run = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result['status'], 'archive_reinspected_applicability_pending')
        self.assertTrue(result['record_reinspection_passed'])
        self.assertFalse(result['propylene_qualified'])
        receipt = self.output.read_bytes()
        self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
        self.assertEqual(self.output.read_bytes(), receipt)
        self.assertEqual(self.bundle.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
