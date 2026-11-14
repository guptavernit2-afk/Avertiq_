"""Synthetic tests exercise gates; they are not model results."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from qualify import ROOT, case_hash, check_input, compare_reference, read_json


class QualificationTests(unittest.TestCase):
    def setUp(self):
        self.reference = read_json(ROOT / 'cases/aloha-reference-propane-v1.json')
        self.case = read_json(ROOT / 'cases/propylene-direct-v1.json')

    def test_frozen_case_checks_are_arithmetic_only(self):
        result = check_input(self.case)
        self.assertEqual(result['arithmetic_only']['airborne_mass_kg'], 60)
        self.assertEqual(result['arithmetic_only']['wind_towards_degrees_true'], 90)
        self.assertFalse(result['model_calculation_performed'])
        self.assertFalse(result['dashboard_adapter_enabled'])
        self.assertTrue(result['open_gates'])

    def test_phase_duration_and_nonfinite_inputs_are_rejected(self):
        for field, value in [('phase', 'two_phase'), ('duration_s', 3601), ('duration_s', 30), ('rate_kg_s', float('nan')), ('rate_kg_s', True)]:
            case = copy.deepcopy(self.case); case['source'][field] = value
            with self.assertRaises(ValueError): check_input(case)

    def test_hash_survives_formatting_and_detects_changed_inputs(self):
        clone = json.loads(json.dumps(self.case, sort_keys=True))
        self.assertEqual(case_hash(clone), case_hash(self.case))
        clone['source']['rate_kg_s'] = .2
        self.assertNotEqual(case_hash(clone), case_hash(self.case))

    def observed(self, folder):
        # Fabricated only within a test temporary directory; never published.
        path = Path(folder) / 'synthetic-test-evidence.txt'; path.write_text('Synthetic test, not an ALOHA run')
        return {'case_id': self.reference['id'], 'case_sha256': case_hash(self.reference), 'engine': {'name': 'ALOHA', 'version': '5.4.7', 'executable_sha256': read_json(ROOT / 'engine-manifest.json')['runtime_files']['ALOHA.EXE']}, 'run_completed': True, 'synthetic_test_data': False, 'run_at_utc': '2026-11-11T00:00:00Z', 'dispersion_method': 'test-only', 'evidence_files': [{'path': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}], 'values': copy.deepcopy(self.reference['expected'])}

    def test_comparison_retains_errors_and_does_not_qualify_propylene(self):
        with tempfile.TemporaryDirectory() as folder:
            observed = self.observed(folder)
            result = compare_reference(self.reference, observed, Path(folder))
            self.assertEqual(result['status'], 'reference_reproduced')
            self.assertFalse(result['propylene_qualified']); self.assertFalse(result['field_validated'])
            observed['values']['red_downwind_yd'] += 20
            result = compare_reference(self.reference, observed, Path(folder))
            self.assertEqual(result['status'], 'reference_mismatch')
            self.assertEqual(result['comparisons']['red_downwind_yd']['absolute_difference'], 20)

    def test_wrong_version_changed_case_missing_evidence_or_synthetic_flag_blocks_claim(self):
        with tempfile.TemporaryDirectory() as folder:
            original = self.observed(folder)
            variants = []
            for key,value in [('case_sha256','wrong'),('run_completed',False),('synthetic_test_data',True),('evidence_files',[])]:
                observed=copy.deepcopy(original); observed[key]=value; variants.append(observed)
            observed=copy.deepcopy(original); observed['engine']['version']='5.4.4'; variants.append(observed)
            observed=copy.deepcopy(original); observed['evidence_files'][0]['sha256']='wrong'; variants.append(observed)
            for observed in variants:
                with self.assertRaises(ValueError): compare_reference(self.reference,observed,Path(folder))

    def test_unrun_template_values_cannot_become_results(self):
        with tempfile.TemporaryDirectory() as folder:
            observed=self.observed(folder); observed['values']['red_downwind_yd']=None
            with self.assertRaises(ValueError): compare_reference(self.reference,observed,Path(folder))


if __name__ == '__main__': unittest.main()
