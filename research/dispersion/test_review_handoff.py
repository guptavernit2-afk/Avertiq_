"""Disposable synthetic handoff checks; no actual model output or browser use."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import test_propylene as fixtures
import test_transcription as unit_fixtures
from propylene import NAMES, ROOT, compare_runs, registered_case, template
from qualify import case_hash
from review_handoff import export_handoff, render_handoff
from transcription import apply_transcription


class ParsedHtml(HTMLParser):
    def __init__(self, document):
        super().__init__()
        self.tags = []
        self.attributes = []
        self.content = []
        self.feed(document)
        self.close()

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attributes.extend(attrs)

    def handle_data(self, data):
        self.content.append(data)

    @property
    def text(self):
        return ' '.join(self.content)


class ReviewHandoffTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='SYNTHETIC-HANDOFF-')
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.runs = self.base / 'runs'
        self.runs.mkdir()
        self.output = self.base / 'handoff.html'
        self.records = {name: fixtures.PropyleneTests().observed(self.runs, name) for name in NAMES}
        for index, record in enumerate(self.records.values(), start=1):
            record['warnings'] = [f'SYNTHETIC warning {index}']
            for row in record['receptors']:
                row['value_ppm'] = index * 10
        self.save()

    def save(self):
        for name, record in self.records.items():
            (self.runs / f'{name}.json').write_text(json.dumps(record), encoding='utf-8')

    def export(self):
        result = export_handoff(self.runs, self.output)
        document = self.output.read_text(encoding='utf-8')
        return result, document, ParsedHtml(document)

    def test_complete_handoff_has_provenance_units_limits_and_no_raw_evidence(self):
        before = {p: p.read_bytes() for p in self.runs.iterdir()}
        result, document, parsed = self.export()
        expected = case_hash(compare_runs(self.runs))
        self.assertEqual(result['checked_comparison_sha256'], expected)
        self.assertIn(expected, parsed.text)
        tool_hash = hashlib.sha256((ROOT / 'review_handoff.py').read_text(encoding='utf-8').encode()).hexdigest()
        self.assertIn(tool_hash, parsed.text)
        for name, record in self.records.items():
            for value in [record['case_id'], record['case_sha256'], record['engine']['executable_sha256'], record['run_at_utc'], record['warnings'][0], record['operator_notes'], record['mapping_review'], record['evidence_files'][0]['sha256']]:
                self.assertIn(value, parsed.text)
        for phrase in ['kg/s', 'm/s', 'Concentration (ppm)', 'Downwind distance (m)', 'applicability pending', 'Not field validated', 'Not operational guidance', 'source_temperature_pressure_phase', 'Exact averaging interval verified', 'false']:
            self.assertIn(phrase, parsed.text)
        self.assertEqual(parsed.tags.count('section'), 7)
        self.assertNotIn('Fabricated validator fixture; not physical evidence', document)
        self.assertNotIn(str(self.runs), document)
        for flag in ['model_calculation_performed', 'propylene_qualified', 'field_validated', 'dashboard_adapter_enabled']:
            self.assertIs(result[flag], False)
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)

    def test_method_and_semantics_blockers_remain_visible(self):
        self.records['rate-half']['dispersion_method'] = 'Heavy Gas'
        self.records['rate-double'].pop('output_semantics')
        self.save()
        _, document, parsed = self.export()
        self.assertIn('dispersion_method_mismatch', parsed.text)
        self.assertIn('variant_output_semantics_missing', parsed.text)
        self.assertEqual(document.count('Numerical comparison withheld:'), 2)
        self.assertEqual(document.count('<h4>Receptor concentrations</h4>'), 1)
        self.assertEqual(document.count('<h4>Recorded receptors</h4>'), 4)

    def test_bound_missing_and_zero_values_keep_distinct_meanings(self):
        factory = unit_fixtures.TranscriptionTests()
        factory.base = self.runs
        for name in NAMES:
            record = factory.record(name)
            factory.item(record, 'receptor.50.value_ppm').update(value_text='10', relation='lt', reason='SYNTHETIC concentration bound')
            factory.item(record, 'contour.1000.downwind_m').update(value_text='10', unit='km', relation='gt', reason='SYNTHETIC distance bound')
            factory.item(record, 'receptor.100.value_ppm').update(value_text='0')
            self.records[name] = apply_transcription(registered_case(name), record)
        self.save()
        _, _, parsed = self.export()
        for phrase in ['Reported bound: < 10.0 ppm', 'Reported bound: > 10000.0 m', 'SYNTHETIC concentration bound', 'SYNTHETIC distance bound', 'Unavailable', 'zero_baseline', 'baseline_and_variant_unavailable']:
            self.assertIn(phrase, parsed.text)

    def test_transcribed_markup_is_text_without_scripts_links_or_external_assets(self):
        hostile = '<script>alert("x")</script><img src="https://invalid.example/x" onerror="alert(1)"><a href="file:///secret">link</a>&'
        for record in self.records.values():
            record['warnings'] = [hostile]
            record['operator_notes'] = hostile
            record['mapping_review'] = hostile
            record['contours'][0]['unavailable_reason'] = hostile
        self.save()
        _, document, parsed = self.export()
        self.assertIn(hostile, parsed.text)
        self.assertIn('&lt;script&gt;', document)
        self.assertFalse({'script', 'img', 'a', 'iframe', 'link', 'object', 'embed'} & set(parsed.tags))
        self.assertFalse(any(key in ('src', 'href') or key.startswith('on') for key, value in parsed.attributes))

    def test_existing_output_and_wrong_suffix_are_refused_without_changes(self):
        self.output.write_text('KEEP EXISTING', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            export_handoff(self.runs, self.output)
        self.assertEqual(self.output.read_text(), 'KEEP EXISTING')
        wrong = self.base / 'report.json'
        with self.assertRaisesRegex(ValueError, '.html'):
            export_handoff(self.runs, wrong)
        self.assertFalse(wrong.exists())

    def test_unrun_malformed_missing_and_tampered_evidence_create_no_report(self):
        baseline = self.records['baseline']
        for failure in ['unrun', 'malformed', 'missing', 'tampered']:
            with self.subTest(failure=failure):
                self.records['baseline'] = baseline
                self.save()
                evidence = self.runs / baseline['evidence_files'][0]['path']
                evidence.write_text('Fabricated validator fixture; not physical evidence', encoding='utf-8')
                path = self.runs / 'baseline.json'
                if failure == 'unrun':
                    path.write_text(json.dumps(template(registered_case('baseline'))), encoding='utf-8')
                elif failure == 'malformed':
                    path.write_text('{"run_completed":true,"run_completed":false}', encoding='utf-8')
                elif failure == 'missing':
                    path.unlink()
                else:
                    evidence.write_text('SYNTHETIC altered evidence', encoding='utf-8')
                destination = self.base / failure / 'report.html'
                with self.assertRaises((ValueError, OSError)):
                    export_handoff(self.runs, destination)
                self.assertFalse(destination.parent.exists())

    def test_cli_checks_original_runs_not_supplied_comparison_json(self):
        command = [sys.executable, str(ROOT / 'review_handoff.py'), '--runs-dir', str(self.runs), '--output', str(self.output)]
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn('applicability_pending', completed.stdout)
        original = self.output.read_bytes()
        self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
        self.assertEqual(self.output.read_bytes(), original)
        bogus = self.base / 'comparison.json'
        bogus.write_text(json.dumps(compare_runs(self.runs)), encoding='utf-8')
        rejected = self.base / 'rejected.html'
        result = subprocess.run(command[:3] + [str(bogus), '--output', str(rejected)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(rejected.exists())

    def test_rendering_refuses_promoted_qualification_flags(self):
        comparison = compare_runs(self.runs)
        for flag in ['propylene_qualified', 'field_validated', 'dashboard_adapter_enabled']:
            altered = {**comparison, flag: True}
            with self.assertRaisesRegex(ValueError, 'must not claim qualification'):
                render_handoff(altered)


if __name__ == '__main__':
    unittest.main()
