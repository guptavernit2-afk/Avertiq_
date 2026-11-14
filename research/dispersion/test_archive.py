"""Disposable synthetic archives only; never real ALOHA evidence."""
import copy
import io
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import archive
import test_propylene as fixtures
from propylene import NAMES, registered_case, template
from qualify import ROOT


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='SYNTHETIC-ARCHIVE-TEST-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / 'capture'
        self.source.mkdir()
        self.observed = self.source / 'record.json'
        self.output = self.base / 'bundle.avertiq-evidence.zip'

    def record(self, variant='baseline'):
        record = fixtures.PropyleneTests().observed(self.source, variant)
        record['warnings'] = ['SYNTHETIC warning retained for validator testing']
        record['receptors'][0].update(value_ppm=None, unavailable_reason='SYNTHETIC unavailable receptor')
        self.observed.write_bytes(archive.encode(record))
        return record

    def create(self, variant='baseline'):
        self.record(variant)
        return archive.archive_run(variant, self.observed, self.output)

    def rewrite(self, mutate, update_hashes=False):
        with zipfile.ZipFile(self.output) as z:
            contents = {name: z.read(name) for name in z.namelist()}
        mutate(contents)
        if update_hashes:
            manifest = archive.decode(contents['manifest.json'])
            manifest['files'] = {name: {'sha256': archive.digest(data), 'bytes': len(data)} for name, data in contents.items() if name != 'manifest.json'}
            contents['manifest.json'] = archive.encode(manifest)
        with zipfile.ZipFile(self.output, 'w') as z:
            for name, data in contents.items():
                z.writestr(name, data)

    def test_all_variants_roundtrip_without_qualification(self):
        for variant in NAMES:
            self.output = self.base / f'{variant}.avertiq-evidence.zip'
            result = self.create(variant)
            verified = archive.verify_archive(self.output, result['archive_sha256'])
            self.assertTrue(verified['external_hash_matched'])
            self.assertTrue(verified['record_reinspection_passed'])
            self.assertEqual(verified['case_id'], registered_case(variant)['id'])
            for flag in (*archive.FLAGS, 'model_executed_by_archive_tool'):
                self.assertIs(verified[flag], False)

    def test_original_bytes_nulls_warnings_and_same_named_evidence_preserved(self):
        record = self.record()
        for name in ['one', 'two']:
            folder = self.source / name
            folder.mkdir()
            data = f'SYNTHETIC {name}'.encode()
            (folder / 'same.txt').write_bytes(data)
            record['evidence_files'].append({'path': f'{name}/same.txt', 'sha256': archive.digest(data)})
        original = json.dumps(record, ensure_ascii=False, indent=4).encode() + b'\r\n'
        self.observed.write_bytes(original)
        before = {str(p): p.read_bytes() for p in self.source.rglob('*') if p.is_file()}
        archive.archive_run('baseline', self.observed, self.output)
        with zipfile.ZipFile(self.output) as z:
            self.assertEqual(z.read('observed-original.json'), original)
            captured = archive.decode(z.read('observed.json'))
            self.assertEqual(captured['warnings'], record['warnings'])
            self.assertIsNone(captured['receptors'][0]['value_ppm'])
            self.assertNotEqual(z.read('evidence/0001.bin'), z.read('evidence/0002.bin'))
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.source.rglob('*') if p.is_file()})

    def test_templates_synthetic_flags_and_wrong_case_leave_no_archive(self):
        valid = self.record()
        rejected = [template(registered_case('baseline')), {**valid, 'synthetic_test_data': True}, {**valid, 'case_id': 'wrong'}]
        for record in rejected:
            self.observed.write_bytes(archive.encode(record))
            with self.assertRaises(ValueError):
                archive.archive_run('baseline', self.observed, self.output)
            self.assertFalse(self.output.exists())

    def test_changed_or_missing_raw_evidence_rejected_before_output(self):
        record = self.record()
        path = self.source / record['evidence_files'][0]['path']
        path.write_text('changed', encoding='utf-8')
        with self.assertRaises(ValueError):
            archive.archive_run('baseline', self.observed, self.output)
        path.unlink()
        with self.assertRaises(ValueError):
            archive.archive_run('baseline', self.observed, self.output)
        self.assertFalse(self.output.exists())

    def test_unsafe_and_duplicate_source_paths_rejected(self):
        valid = self.record()
        for name in ['../outside', '/absolute', 'C:\\outside', 'C:relative', 'file:stream', './SYNTHETIC-TEST-ONLY.txt', 'one//file']:
            record = copy.deepcopy(valid)
            record['evidence_files'][0]['path'] = name
            self.observed.write_bytes(archive.encode(record))
            with self.assertRaises(ValueError):
                archive.archive_run('baseline', self.observed, self.output)
        record = copy.deepcopy(valid)
        record['evidence_files'].append(record['evidence_files'][0])
        self.observed.write_bytes(archive.encode(record))
        with self.assertRaises(ValueError):
            archive.archive_run('baseline', self.observed, self.output)
        self.assertFalse(self.output.exists())

    def test_member_change_missing_extra_and_external_hash_mismatch(self):
        receipt = self.create()
        pristine = self.output.read_bytes()
        mutations = [lambda c: c.__setitem__('evidence/0000.bin', b'changed'),
                     lambda c: c.pop('case.json'),
                     lambda c: c.__setitem__('../outside.txt', b'traversal')]
        for mutate in mutations:
            self.output.write_bytes(pristine)
            self.rewrite(mutate)
            with self.assertRaises(ValueError):
                archive.verify_archive(self.output)
        self.output.write_bytes(pristine)
        with self.assertRaises(ValueError):
            archive.verify_archive(self.output, '0' * 64)
        self.assertTrue(archive.verify_archive(self.output, receipt['archive_sha256'])['external_hash_matched'])

    def test_report_forgery_rejected_even_if_member_hashes_updated(self):
        self.create()
        def mutate(contents):
            report = archive.decode(contents['inspection.json'])
            report['warnings'] = []
            contents['inspection.json'] = archive.encode(report)
        self.rewrite(mutate, update_hashes=True)
        with self.assertRaisesRegex(ValueError, 'inspection differs'):
            archive.verify_archive(self.output)

    def test_tooling_drift_reports_integrity_only_without_promoting_results(self):
        receipt = self.create()
        changed = copy.deepcopy(archive.provenance())
        changed['tool_sha256_lf_utf8']['qualify.py'] = 'different revision'
        with patch('archive.provenance', return_value=changed):
            result = archive.verify_archive(self.output, receipt['archive_sha256'])
        self.assertEqual(result['status'], 'archive_integrity_verified_reinspection_pending')
        self.assertTrue(result['integrity_checks_passed'])
        self.assertFalse(result['record_reinspection_passed'])
        self.assertFalse(result['dashboard_adapter_enabled'])

    def test_existing_archive_and_wrong_suffix_never_overwritten(self):
        self.create()
        before = self.output.read_bytes()
        with self.assertRaises(ValueError):
            archive.archive_run('baseline', self.observed, self.output)
        self.assertEqual(self.output.read_bytes(), before)
        wrong = self.base / 'publish.zip'
        with self.assertRaises(ValueError):
            archive.archive_run('baseline', self.observed, wrong)
        self.assertFalse(wrong.exists())

    def test_interrupted_write_is_not_accepted_or_overwritten(self):
        self.record()
        original_open = Path.open
        class BrokenWriter:
            def __init__(self, stream): self.stream = stream
            def __enter__(self): return self
            def __exit__(self, *args): self.stream.close()
            def write(self, data):
                self.stream.write(data[:20])
                raise OSError('SYNTHETIC disk interruption')
        def fail_write(path, mode='r', *args, **kwargs):
            stream = original_open(path, mode, *args, **kwargs)
            return BrokenWriter(stream) if mode == 'xb' else stream
        with patch.object(Path, 'open', fail_write):
            with self.assertRaises(OSError):
                archive.archive_run('baseline', self.observed, self.output)
        before = self.output.read_bytes()
        with self.assertRaises(zipfile.BadZipFile): archive.verify_archive(self.output)
        with self.assertRaises(ValueError): archive.archive_run('baseline', self.observed, self.output)
        self.assertEqual(self.output.read_bytes(), before)

    def test_duplicate_members_json_keys_and_compressed_files_rejected(self):
        self.create()
        with zipfile.ZipFile(self.output) as z:
            contents = {name: z.read(name) for name in z.namelist()}
        for duplicate, compression in [(True, zipfile.ZIP_STORED), (False, zipfile.ZIP_DEFLATED)]:
            with io.BytesIO() as buffer:
                with zipfile.ZipFile(buffer, 'w', compression=compression) as z:
                    for name, data in contents.items(): z.writestr(name, data)
                    if duplicate: z.writestr('CASE.JSON', contents['case.json'])
                with self.assertRaises(ValueError): archive.verify_bytes(buffer.getvalue())
        with self.assertRaises(ValueError): archive.decode(b'{"field":1,"field":2}')

    def test_size_limits_and_linked_paths_rejected(self):
        self.record()
        with patch('archive.MAX_FILE_BYTES', 1):
            # Default function argument is fixed; ZIP member limit is checked independently.
            with self.assertRaises(ValueError): archive.archive_run('baseline', self.observed, self.output)
        self.assertFalse(self.output.exists())
        with patch.object(Path, 'is_symlink', return_value=True):
            with self.assertRaises(ValueError): archive.local_evidence_path(self.source, 'SYNTHETIC-TEST-ONLY.txt')
        with patch('archive.MAX_ARCHIVE_BYTES', 10):
            with self.assertRaises(ValueError): archive.archive_run('baseline', self.observed, self.output)

    def test_cli_archive_verify_and_reject_incomplete(self):
        self.record()
        command = [sys.executable, str(ROOT / 'archive.py'), 'archive-run', '--case', 'baseline', '--observed', str(self.observed), '--output', str(self.output)]
        run = subprocess.run(command, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        receipt = json.loads(run.stdout)
        verify = [sys.executable, str(ROOT / 'archive.py'), 'verify-archive', '--archive', str(self.output), '--expected-sha256', receipt['archive_sha256']]
        run = subprocess.run(verify, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertFalse(json.loads(run.stdout)['propylene_qualified'])
        self.output.write_bytes(b'incomplete')
        self.assertNotEqual(subprocess.run(verify, capture_output=True).returncode, 0)


if __name__ == '__main__':
    unittest.main()
