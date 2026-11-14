"""Blank capture-folder tests; no ALOHA execution or observed results."""
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import prepare_capture
from output_semantics import semantics_template
from propylene import NAMES, ROOT, SUITE, inspect_run, registered_case, template
from qualify import case_hash, read_json
from transcription import apply_transcription, transcription_template


class CaptureFolderTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='UNRUN-CAPTURE-TEST-')
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.output = self.base / 'capture folder'

    def test_all_four_records_have_blank_observations_and_unconfirmed_supplements(self):
        prepare_capture.prepare_folder(self.output)
        for name in NAMES:
            case = registered_case(name)
            record = read_json(self.output / f'{name}-capture.json')
            expected = template(case)
            for key, value in expected.items():
                if key != 'label':
                    self.assertEqual(record[key], value)
            self.assertEqual(record['output_semantics'], semantics_template())
            self.assertEqual(record['transcription'], transcription_template(case))
            self.assertFalse(record['run_completed'])
            for field in ['observed_inputs', 'run_at_utc', 'dispersion_method', 'warnings', 'operator_notes', 'mapping_review']:
                self.assertIsNone(record[field])
            self.assertEqual(record['evidence_files'], [])
            self.assertIsNone(record['engine']['executable_sha256'])
            for flag in ['propylene_qualified', 'field_validated', 'dashboard_adapter_enabled']:
                self.assertIs(record[flag], False)
            self.assertIn('UNRUN', record['label'])

    def test_manifest_covers_initial_bytes_and_separate_frozen_inputs(self):
        source_paths = [SUITE / f'{name}.json' for name in NAMES]
        before = {path: path.read_bytes() for path in source_paths}
        result = prepare_capture.prepare_folder(self.output)
        manifest = read_json(self.output / prepare_capture.MANIFEST)
        self.assertEqual(result, manifest)
        self.assertEqual(manifest['status'], 'prepared_unrun')
        self.assertEqual(len(manifest['initial_files']), 9)
        actual = {p.relative_to(self.output).as_posix() for p in self.output.rglob('*') if p.is_file()}
        self.assertEqual(actual, set(manifest['initial_files']) | {prepare_capture.MANIFEST})
        for name, info in manifest['initial_files'].items():
            content = (self.output / name).read_bytes()
            self.assertEqual(info, {'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)})
        for item in manifest['cases']:
            self.assertEqual(case_hash(read_json(self.output / item['input_snapshot'])), item['case_sha256'])
            self.assertEqual(read_json(self.output / item['capture_record'])['case_sha256'], item['case_sha256'])
            self.assertEqual(list((self.output / item['evidence_directory']).iterdir()), [])
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)
        for flag in prepare_capture.FLAGS:
            self.assertIs(manifest[flag], False)

    def test_generated_records_cannot_pass_inspection_or_normalization(self):
        prepare_capture.prepare_folder(self.output)
        for name in NAMES:
            case = registered_case(name)
            record = read_json(self.output / f'{name}-capture.json')
            with self.assertRaisesRegex(ValueError, 'Completed actual run'):
                inspect_run(case, record, self.output)
            with self.assertRaisesRegex(ValueError, 'Unconfirmed'):
                apply_transcription(case, record)
        rejected = self.output / 'baseline.json'
        command = [sys.executable, str(ROOT / 'propylene.py'), 'normalize-run', '--observed', str(self.output / 'baseline-capture.json'), '--output', str(rejected)]
        result = subprocess.run(command, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(rejected.exists())

    def test_existing_directories_and_files_are_never_modified(self):
        for kind in ['empty', 'populated', 'file']:
            destination = self.base / kind
            if kind == 'file':
                destination.write_text('KEEP FILE', encoding='utf-8')
            else:
                destination.mkdir()
                if kind == 'populated':
                    (destination / 'user.txt').write_text('KEEP CONTENT', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'existing destinations'):
                prepare_capture.prepare_folder(destination)
            if kind == 'file':
                self.assertEqual(destination.read_text(), 'KEEP FILE')
            elif kind == 'populated':
                self.assertEqual((destination / 'user.txt').read_text(), 'KEEP CONTENT')
                self.assertEqual(len(list(destination.iterdir())), 1)
            else:
                self.assertEqual(list(destination.iterdir()), [])

    def test_invalid_registry_fails_before_creating_destination(self):
        destination = self.base / 'new-parent' / 'capture'
        with patch('prepare_capture.registered_case', side_effect=ValueError('SYNTHETIC registry mismatch')):
            with self.assertRaisesRegex(ValueError, 'registry mismatch'):
                prepare_capture.prepare_folder(destination)
        self.assertFalse(destination.parent.exists())

    def test_interrupted_file_write_leaves_partial_setup_without_manifest_and_refuses_retry(self):
        original_open = Path.open
        def interrupted(path, *args, **kwargs):
            if path == self.output / 'baseline-capture.json':
                raise OSError('SYNTHETIC interrupted write')
            return original_open(path, *args, **kwargs)
        with patch.object(Path, 'open', interrupted):
            with self.assertRaisesRegex(OSError, 'interrupted write'):
                prepare_capture.prepare_folder(self.output)
        self.assertTrue((self.output / 'README.txt').exists())
        self.assertFalse((self.output / prepare_capture.MANIFEST).exists())
        before = {p: p.read_bytes() for p in self.output.rglob('*') if p.is_file()}
        with self.assertRaisesRegex(ValueError, 'existing destinations'):
            prepare_capture.prepare_folder(self.output)
        self.assertEqual(before, {p: p.read_bytes() for p in self.output.rglob('*') if p.is_file()})

    def test_cli_creates_unrun_folder_with_guide_and_refuses_overwrite(self):
        command = [sys.executable, str(ROOT / 'prepare_capture.py'), '--output', str(self.output)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('prepared_unrun', result.stdout)
        guide = (self.output / 'README.txt').read_text(encoding='utf-8')
        for phrase in ['NOT observed', 'normalize-run', 'compare-runs', 'review_handoff.py', 'evidence/baseline/summary.txt', 'initial hashes are expected to differ', 'fresh folder']:
            self.assertIn(phrase, guide)
        manifest = (self.output / prepare_capture.MANIFEST).read_bytes()
        failed = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn('existing destinations', failed.stderr)
        self.assertEqual((self.output / prepare_capture.MANIFEST).read_bytes(), manifest)

    def test_partial_final_manifest_is_invalid_and_never_reported_as_complete(self):
        original_open = Path.open
        class InterruptedManifest:
            def __init__(self, stream):
                self.stream = stream
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self.stream.close()
            def write(self, data):
                self.stream.write(data[:20])
                raise OSError('SYNTHETIC manifest interruption')
        def interrupted(path, *args, **kwargs):
            stream = original_open(path, *args, **kwargs)
            if path == self.output / prepare_capture.MANIFEST and args == ('xb',):
                return InterruptedManifest(stream)
            return stream
        with patch.object(Path, 'open', interrupted):
            with self.assertRaisesRegex(OSError, 'manifest interruption'):
                prepare_capture.prepare_folder(self.output)
        with self.assertRaises(ValueError):
            read_json(self.output / prepare_capture.MANIFEST)
        with self.assertRaisesRegex(ValueError, 'existing destinations'):
            prepare_capture.prepare_folder(self.output)


if __name__ == '__main__':
    unittest.main()
