"""Check the documented input subset, without inferring engine source state."""
import math
from qualify import ROOT, case_hash, read_json
from source_state import screen_source_state


def finite(value, field):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f'{field} must be a finite number')
    return value


def review_source_treatment(case):
    evidence = read_json(ROOT / 'source-treatment-evidence.json')
    mapping = read_json(ROOT / evidence['installed_help_manifest'])
    source, inputs = case['source'], case['model_inputs']
    rate = finite(source['rate_kg_s'], 'rate_kg_s')
    duration = finite(source['duration_s'], 'duration_s')
    height = finite(source['height_m'], 'height_m')
    entered_rate = finite(inputs['rate_kg_s'], 'model rate_kg_s')
    entered_minutes = finite(inputs['duration_min'], 'model duration_min')
    entered_height = finite(inputs['source_height_m'], 'model source_height_m')
    declared_state = screen_source_state(case)
    checks = {
        'prescribed_airborne_gas_rate': source.get('type') == 'prescribed_airborne_mass_rate_not_tank_discharge',
        'direct_continuous_entry': inputs.get('source_option') == 'Direct' and inputs.get('release_type') == 'continuous',
        'pure_propylene_identity': case['chemical']['CAS'] == inputs.get('chemical_CAS') == '115-07-1' and case['chemical']['composition_mole_fraction'] == 1,
        'gas_only_without_droplets_declared': source.get('phase') == 'gas_only' and source.get('droplets') is False,
        'mass_rate_matches': 0 < rate == entered_rate <= 1e9,
        # Exact normalized entries, not a tolerance for accepting observed output.
        'continuous_duration_matches': 1 < entered_minutes <= 60 and duration / 60 == entered_minutes,
        'ground_level_matches': height == entered_height == 0,
        'no_jet_calculation_declared': source.get('momentum') == 'neglected; no pressurized jet or hole calculation',
        'declared_equilibrium_screen_supported': declared_state['declared_equilibrium_gas_consistent'],
    }
    conflicts = [name for name, passed in checks.items() if not passed]
    return {
        'case_id': case['id'], 'case_sha256': case_hash(case),
        'review_id': evidence['id'], 'review_sha256': case_hash(evidence),
        'help_manifest_sha256': case_hash(mapping),
        'engine': {'name': 'ALOHA', 'version': evidence['installed_version']},
        'status': 'documented_input_subset_matches_internal_state_pending' if not conflicts else 'source_contract_conflict',
        'documented_input_subset_matches': not conflicts,
        'checks': checks, 'conflicts': conflicts,
        'declared_source_state': {'temperature_K': source['temperature_K'], 'pressure_Pa': source['pressure_Pa'], 'phase': source['phase'], 'droplets': source['droplets']},
        'effective_model_source_state': {field: None for field in evidence['unknown_effective_source_fields']},
        'effective_state_reason': 'Not established for installed 5.4.7 mass-unit Direct Source by reviewed documentation; no values inferred from air or storage-conversion fields.',
        'source_state_equivalence_established': False,
        'tank_discharge_calculated': False, 'model_calculation_performed': False,
        'propylene_qualified': False, 'field_validated': False, 'dashboard_adapter_enabled': False,
        'label': 'Source input contract review only; internal thermodynamics and actual propylene results pending',
    }
