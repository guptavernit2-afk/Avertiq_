"""Synthetic input mutations only; no ALOHA model execution."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from propylene import NAMES, registered_case
from qualify import ROOT, case_hash, read_json
from source_treatment import review_source_treatment


class SourceTreatmentTests(unittest.TestCase):
    def test_all_cases_match_only_documented_subset_without_mutation(self):
        for name in NAMES:
            case = registered_case(name)
            before = copy.deepcopy(case)
            result = review_source_treatment(case)
            self.assertEqual(case, before)
            self.assertTrue(result['documented_input_subset_matches'])
            self.assertEqual(result['conflicts'], [])
            self.assertTrue(all(v is None for v in result['effective_model_source_state'].values()))
            for field in ('source_state_equivalence_established', 'tank_discharge_calculated', 'model_calculation_performed', 'propylene_qualified', 'field_validated', 'dashboard_adapter_enabled'):
                self.assertIs(result[field], False)

    def test_tank_liquid_volume_and_jet_changes_are_conflicts(self):
        edits = [('source', 'type', 'tank_liquid_loss_rate'), ('source', 'phase', 'two_phase'),
                 ('source', 'droplets', True), ('source', 'momentum', 'pressurized jet'),
                 ('model_inputs', 'source_option', 'Tank'), ('model_inputs', 'release_type', 'instantaneous'),
                 ('model_inputs', 'chemical_CAS', '74-98-6')]
        for section, key, value in edits:
            with self.subTest(key=key):
                case = registered_case('baseline')
                case[section][key] = value
                result = review_source_treatment(case)
                self.assertEqual(result['status'], 'source_contract_conflict')
                self.assertTrue(result['conflicts'])

    def test_rate_duration_and_height_must_match_declarations(self):
        for key, value in [('rate_kg_s', .2), ('duration_min', 600), ('source_height_m', 1)]:
            case = registered_case('baseline')
            case['model_inputs'][key] = value
            self.assertFalse(review_source_treatment(case)['documented_input_subset_matches'])
        case = registered_case('baseline')
        case['source']['height_m'] = case['model_inputs']['source_height_m'] = 1
        self.assertFalse(review_source_treatment(case)['checks']['ground_level_matches'])

    def test_continuous_duration_boundary_and_mass_rate_bounds(self):
        for minutes, expected in [(0, False), (1, False), (1.5, True), (60, True), (61, False)]:
            case = registered_case('baseline')
            case['source']['duration_s'] = minutes * 60
            case['model_inputs']['duration_min'] = minutes
            self.assertEqual(review_source_treatment(case)['checks']['continuous_duration_matches'], expected)
        for rate, expected in [(0, False), (-1, False), (1e9, True), (1e9 + 1, False)]:
            case = registered_case('baseline')
            case['source']['rate_kg_s'] = case['model_inputs']['rate_kg_s'] = rate
            self.assertEqual(review_source_treatment(case)['checks']['mass_rate_matches'], expected)

    def test_invalid_numeric_fields_rejected(self):
        for section, keys in [('source', ('rate_kg_s', 'duration_s', 'height_m')), ('model_inputs', ('rate_kg_s', 'duration_min', 'source_height_m'))]:
            for key in keys:
                for value in (True, None, '1', float('nan'), float('inf')):
                    case = registered_case('baseline')
                    case[section][key] = value
                    with self.assertRaises(ValueError):
                        review_source_treatment(case)

    def test_supported_declarations_never_become_effective_state(self):
        case = registered_case('baseline')
        case['source']['temperature_K'] = 300
        result = review_source_treatment(case)
        self.assertTrue(result['documented_input_subset_matches'])
        self.assertEqual(result['declared_source_state']['temperature_K'], 300)
        self.assertIsNone(result['effective_model_source_state']['temperature_K'])
        case['source']['pressure_Pa'] = 2 * 101325
        self.assertFalse(review_source_treatment(case)['checks']['declared_equilibrium_screen_supported'])

    def test_review_provenance_and_saved_report_are_reproducible(self):
        result = review_source_treatment(registered_case('baseline'))
        self.assertEqual(result['review_sha256'], case_hash(read_json(ROOT / 'source-treatment-evidence.json')))
        self.assertEqual(result['help_manifest_sha256'], case_hash(read_json(ROOT / 'mapping-evidence.json')))
        saved = read_json(ROOT.parent.parent / 'data/public/dispersion-qualification-v1/propylene-source-treatment.json')
        self.assertEqual(saved, result)

    def test_cli_outputs_review_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'review.json'
            command = [sys.executable, str(ROOT / 'propylene.py'), 'source-treatment-check', '--case', 'rate-half', '--output', str(path)]
            run = subprocess.run(command, capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(path.read_text(encoding='utf-8')), review_source_treatment(registered_case('rate-half')))
            before = path.read_bytes()
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
