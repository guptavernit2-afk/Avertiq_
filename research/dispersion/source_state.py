"""Bounded declared-state screening, not a flash, tank or dispersion model."""
import math
from qualify import ROOT, case_hash, read_json


def finite_positive(value, field):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError(f'{field} must be a finite positive number')
    return value


def screen_source_state(case):
    evidence = read_json(ROOT / 'propylene-state-evidence.json')
    chemical, source = case['chemical'], case['source']
    temperature = finite_positive(source['temperature_K'], 'temperature_K')
    pressure = finite_positive(source['pressure_Pa'], 'pressure_Pa')
    composition = finite_positive(chemical['composition_mole_fraction'], 'composition_mole_fraction')
    if composition > 1:
        raise ValueError('Mole fraction cannot exceed one')
    supported = False
    reason = 'This screen is restricted to pure propylene at exactly one standard atmosphere.'
    if chemical['CAS'] == evidence['chemical_CAS'] and composition == 1 and pressure == evidence['normal_pressure_Pa']:
        lower = evidence['normal_boiling_temperature_K'] + evidence['reported_boiling_spread_K']
        upper = evidence['critical_temperature_K'] - evidence['reported_critical_spread_K']
        supported = lower < temperature < upper
        reason = ('Declared temperature is above the normal-boiling screening band and below the critical screening band; equilibrium gas is consistent.' if supported else 'Declared temperature is outside this bounded gas-state screen; no phase conclusion is made.')
    if source.get('phase') != 'gas_only' or source.get('droplets') is not False:
        supported = False
        reason = 'Droplets or another declared phase require a different source assessment; equilibrium temperature does not resolve a release transient.'
    limits = evidence['antoine_supported_temperature_K']
    return {
        'case_id': case['id'], 'case_sha256': case_hash(case),
        'evidence_id': evidence['id'], 'evidence_sha256': case_hash(evidence),
        'status': 'declared_equilibrium_gas_consistent' if supported else 'declared_gas_state_not_established',
        'reason': reason,
        'declared_temperature_K': temperature, 'declared_pressure_Pa': pressure,
        'declared_equilibrium_gas_consistent': supported,
        'antoine_temperature_in_published_range': limits[0] <= temperature <= limits[1],
        'vapor_pressure_calculated': False,
        'actual_release_phase_known': False, 'actual_release_temperature_known': False,
        'aloha_internal_source_state_verified': False,
        'model_calculation_performed': False, 'propylene_qualified': False,
        'field_validated': False, 'dashboard_adapter_enabled': False,
        'label': 'Declared equilibrium-state screen only; no source-path or model-execution result',
    }
