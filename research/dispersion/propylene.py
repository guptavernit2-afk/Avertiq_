"""Propylene preparation and observed-record checks. Never executes a model."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from qualify import ROOT, case_hash, check_input, read_json
from source_state import screen_source_state
from source_treatment import review_source_treatment
from output_semantics import review_output_semantics, semantics_template
from transcription import transcription_template, apply_transcription, review_transcription

NAMES = ('baseline', 'rate-half', 'rate-double', 'wind-higher')
SUITE = ROOT / 'cases/propylene-v2'

def require(condition, message):
    if not condition:
        raise ValueError(message)

def number(value, label, maximum=None):
    require(type(value) in (int, float) and math.isfinite(value) and value >= 0, f'{label}: finite nonnegative number required')
    require(maximum is None or value <= maximum, f'{label}: exceeds allowed bound')
    return value

def utc(value):
    require(isinstance(value, str), 'UTC timestamp required')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(parsed.utcoffset() is not None and parsed.utcoffset().total_seconds() == 0, 'Timestamp must explicitly be UTC')

def prepared_cases():
    original = read_json(ROOT / 'cases/propylene-direct-v1.json')
    cases = {}
    for name in NAMES:
        case = copy.deepcopy(original)
        case['id'] = f'D-001-PHYS-002-{name}'
        case['schema_version'] = 2
        case['status'] = 'prepared_unrun_applicability_pending'
        case['parent_case_sha256'] = case_hash(original)
        case['variant'] = name
        reference = read_json(ROOT.parent.parent / 'data/public/dispersion-qualification-v1/reference-comparison.json')
        require(reference['status'] == 'reference_reproduced', 'Separate propane reference must be reproduced')
        case['reference_control_sha256'] = case_hash(reference)
        case['gates']['reference_reproduction_passed'] = True
        case.pop('variations')
        case['site']['latitude_deg'] = 18 + 45.8 / 60
        case['site']['longitude_deg'] = 73 + 20.7 / 60
        case['site']['entry_dms'] = {'latitude': '18 deg 45.8 min N', 'longitude': '73 deg 20.7 min E'}
        case['revision_reason'] = 'Preserve v1; use the minute precision observed in earlier unsaved desktop setup. Model-entry fields are separated from unverified source/ground assumptions. No outputs informed this revision.'
        if name == 'rate-half': case['source']['rate_kg_s'] = .05
        if name == 'rate-double': case['source']['rate_kg_s'] = .2
        if name == 'wind-higher': case['weather']['wind_speed_m_s'] = 4.0
        case['model_inputs'] = {
            'chemical_CAS': '115-07-1', 'source_option': 'Direct', 'release_type': 'continuous',
            'rate_kg_s': case['source']['rate_kg_s'], 'duration_min': 10.0, 'source_height_m': 0.0,
            'wind_m_s': case['weather']['wind_speed_m_s'], 'wind_height_m': 10.0, 'wind_from_deg_true': 270.0,
            'air_temperature_C': 25.0, 'humidity_percent': 50.0, 'stability_class': 'D', 'cloud_tenths': 10,
            'inversion': 'none', 'roughness_choice': 'Open Country', 'calculation_option': 'Let ALOHA decide',
            'latitude_deg': case['site']['latitude_deg'], 'longitude_deg': case['site']['longitude_deg'],
            'elevation_m': 0.0, 'time_local': original['site']['time_local'],
            'display_mode': 'toxic-concentration diagnostic only', 'diagnostic_levels_ppm': [1000, 100, 10],
        }
        case['mapping_pending'] = ['source_temperature_pressure_phase', 'ground_temperature', 'installed_roughness_value', 'installed_chemical_identity_and_properties', 'output_height_and_time_basis']
        case['source_summary_tolerance'] = {'relative': .01, 'absolute_mass_kg': .01, 'absolute_duration_s': .01}
        case['label'] = 'UNRUN assumed research case; applicability pending; no physical result'
        cases[name] = case
    return cases

def registered_case(name):
    case = read_json(SUITE / f'{name}.json')
    require(case_hash(case) == case_hash(prepared_cases()[name]), 'Frozen case differs from registered preparation; create/review a new suite version')
    check_input(case)
    return case

def template(case):
    return {
        'case_id': case['id'], 'case_sha256': case_hash(case), 'run_completed': False, 'synthetic_test_data': False,
        'run_at_utc': None, 'engine': {'name': 'ALOHA', 'version': '5.4.7', 'executable_sha256': None},
        'observed_inputs': None, 'dispersion_method': None,
        'basis': {'concentration_unit': 'ppm', 'concentration_basis': 'gas_volume_fraction', 'receptor_height_m': None, 'statistic': None, 'averaging_description': None, 'time_window_description': None, 'display_mode': None},
        'source_summary': {'airborne_mass_kg': None, 'duration_s': None},
        'receptors': [{'downwind_m': x, 'crosswind_m': 0, 'value_ppm': None, 'unavailable_reason': None} for x in case['requested_outputs']['centerline_downwind_m']],
        'contours': [{'level_ppm': x, 'downwind_m': None, 'unavailable_reason': None} for x in case['requested_outputs']['diagnostic_contours_ppm']],
        'warnings': None, 'operator_notes': None, 'mapping_review': None, 'evidence_files': [],
        'label': 'UNRUN TEMPLATE. Copy observed values only; unavailable values need the actual model reason. No expected concentrations supplied.',
    }

def inspect_run(case, observed, evidence_base):
    require(observed.get('case_id') == case['id'] and observed.get('case_sha256') == case_hash(case), 'Wrong case identity/hash')
    require(observed.get('run_completed') is True and observed.get('synthetic_test_data') is False, 'Completed actual run required; templates/synthetic fixtures are not evidence')
    utc(observed.get('run_at_utc'))
    expected_engine = {'name': 'ALOHA', 'version': '5.4.7', 'executable_sha256': read_json(ROOT / 'engine-manifest.json')['runtime_files']['ALOHA.EXE']}
    require(observed.get('engine') == expected_engine, 'Engine/version/binary mismatch')
    require(case_hash(observed.get('observed_inputs')) == case_hash(case['model_inputs']), 'Observed input mapping differs from frozen case (normalize documented units first)')
    require(observed.get('dispersion_method') in ('Gaussian', 'Heavy Gas'), 'Record actual selected dispersion method')
    basis = observed.get('basis', {})
    require(basis.get('concentration_unit') == 'ppm' and basis.get('concentration_basis') == 'gas_volume_fraction', 'Unsupported concentration units/basis')
    require(type(basis.get('receptor_height_m')) in (int, float) and basis['receptor_height_m'] == 0, 'Ground-level receptor required')
    require(basis.get('display_mode') == case['model_inputs']['display_mode'], 'Do not mix toxic and flammable display outputs')
    for field in ('statistic', 'averaging_description', 'time_window_description'):
        require(isinstance(basis.get(field), str) and basis[field].strip(), f'Missing output semantics: {field}')
    for field in ('operator_notes', 'mapping_review'):
        require(isinstance(observed.get(field), str) and observed[field].strip(), f'Missing {field}')
    warnings = observed.get('warnings')
    require(isinstance(warnings, list) and all(isinstance(w, str) and w.strip() for w in warnings), 'Record warnings explicitly (empty list only if none observed)')
    base = Path(evidence_base).resolve()
    evidence = observed.get('evidence_files')
    require(isinstance(evidence, list) and len(evidence) > 0, 'Raw local evidence is required')
    files = []
    for item in evidence:
        path = (base / item['path']).resolve()
        require(path.is_relative_to(base) and path.is_file(), 'Evidence must be a file within the observed-record directory')
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == item['sha256'], 'Evidence hash mismatch')
        files.append({'name': path.name, 'sha256': digest})
    summary = observed.get('source_summary', {})
    for field, expected, absolute in [('airborne_mass_kg', case['source']['rate_kg_s'] * case['source']['duration_s'], case['source_summary_tolerance']['absolute_mass_kg']), ('duration_s', case['source']['duration_s'], case['source_summary_tolerance']['absolute_duration_s'])]:
        value = number(summary.get(field), field)
        tolerance = max(absolute, expected * case['source_summary_tolerance']['relative'])
        require(abs(value - expected) <= tolerance, f'{field} differs from prescribed source beyond registered tolerance')
    for group, key, value_key, requested in [('receptors', 'downwind_m', 'value_ppm', case['requested_outputs']['centerline_downwind_m']), ('contours', 'level_ppm', 'downwind_m', case['requested_outputs']['diagnostic_contours_ppm'])]:
        rows = observed.get(group)
        require(isinstance(rows, list) and len(rows) == len(requested), f'Incomplete {group}')
        values = [number(row.get(key), key) for row in rows]
        require(sorted(values) == sorted(requested), f'Duplicate or mismatched {group}')
        for row in rows:
            if group == 'receptors':
                require(type(row.get('crosswind_m')) in (int, float) and row['crosswind_m'] == 0, 'Centerline receptor required')
            if row.get(value_key) is None:
                require(isinstance(row.get('unavailable_reason'), str) and row['unavailable_reason'].strip(), 'Missing/censored value requires observed reason; never substitute zero')
            else:
                number(row[value_key], value_key, 1e6 if value_key == 'value_ppm' else None)
                require(row.get('unavailable_reason') is None, 'Numeric value cannot also be unavailable')
    return {
        'case_id': case['id'], 'case_sha256': case_hash(case), 'status': 'record_consistent_applicability_review_pending',
        'record_checks_passed': True, 'engine': observed['engine'], 'run_at_utc': observed['run_at_utc'],
        'dispersion_method': observed['dispersion_method'], 'basis': basis, 'source_summary': summary,
        'receptors': observed['receptors'], 'contours': observed['contours'], 'warnings': warnings,
        'operator_notes': observed['operator_notes'], 'mapping_review': observed['mapping_review'], 'evidence_files': files,
        'declared_source_state_screen': screen_source_state(case),
        'source_treatment_review': review_source_treatment(case),
        'output_semantics_review': review_output_semantics(observed),
        'unit_transcription_review': review_transcription(case, observed),
        'raw_unit_transcription': observed.get('transcription'),
        'open_mapping_gates': case['mapping_pending'], 'propylene_qualified': False, 'field_validated': False,
        'dashboard_adapter_enabled': False, 'label': 'Observed record checked for consistency only; human applicability review still required',
    }

def preparation_report():
    cases = {name: registered_case(name) for name in NAMES}
    return {'status': 'prepared_unrun', 'cases': [{
        'variant': name, 'case_id': case['id'], 'sha256': case_hash(case),
        'arithmetic_only': check_input(case)['arithmetic_only'], 'open_mapping_gates': case['mapping_pending'],
    } for name, case in cases.items()], 'model_calculation_performed': False, 'propylene_qualified': False, 'dashboard_adapter_enabled': False}

def compare_runs(runs_dir):
    reports = {}
    for name in NAMES:
        path = Path(runs_dir) / f'{name}.json'
        reports[name] = inspect_run(registered_case(name), read_json(path), path.parent)
    baseline = reports['baseline']
    comparisons = []
    for name in NAMES[1:]:
        report = reports[name]
        base_semantics = baseline['output_semantics_review']
        run_semantics = report['output_semantics_review']
        comparable = (report['dispersion_method'] == baseline['dispersion_method']
                      and case_hash(report['basis']) == case_hash(baseline['basis'])
                      and base_semantics['same_engine_comparison_eligible']
                      and run_semantics['same_engine_comparison_eligible']
                      and base_semantics['comparison_signature'] == run_semantics['comparison_signature'])
        changes = []
        if comparable:
            lookup = {r['downwind_m']: r for r in report['receptors']}
            for point in baseline['receptors']:
                a, b = point['value_ppm'], lookup[point['downwind_m']]['value_ppm']
                changes.append({'downwind_m': point['downwind_m'], 'baseline_ppm': a, 'variant_ppm': b,
                                'difference_ppm': None if a is None or b is None else b - a,
                                'ratio': None if a in (None, 0) or b is None else b / a})
        comparisons.append({'variant': name, 'comparable_basis': comparable,
                            'reason': 'Matched method, basis and structured output meaning for same-engine diagnostics only; no monotonic trend assumed' if comparable else 'Method/basis differs or structured output meaning is missing; numerical comparison withheld',
                            'receptor_changes': changes})
    return {'status': 'observed_records_compared_review_pending', 'runs': reports, 'comparisons': comparisons,
            'propylene_qualified': False, 'field_validated': False, 'dashboard_adapter_enabled': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare-check', 'template', 'inspect-run', 'compare-runs', 'source-state-check', 'source-treatment-check', 'output-semantics-template', 'transcription-template', 'normalize-run'])
    parser.add_argument('--case', choices=NAMES, default='baseline')
    parser.add_argument('--observed', type=Path)
    parser.add_argument('--runs-dir', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'prepare-check': result = preparation_report()
    elif args.command == 'output-semantics-template': result = semantics_template()
    elif args.command == 'transcription-template': result = transcription_template(registered_case(args.case))
    elif args.command == 'normalize-run':
        if args.observed is None: parser.error('--observed is required')
        case = registered_case(args.case)
        result = apply_transcription(case, read_json(args.observed))
        inspect_run(case, result, args.observed.parent)
        # Relative evidence paths must still refer to the same raw files.
        require(args.output.parent.resolve() == args.observed.parent.resolve(), 'Normalized run must stay beside the original observation and raw evidence')
    elif args.command == 'source-state-check': result = screen_source_state(registered_case(args.case))
    elif args.command == 'source-treatment-check': result = review_source_treatment(registered_case(args.case))
    elif args.command == 'compare-runs':
        if args.runs_dir is None: parser.error('--runs-dir is required')
        result = compare_runs(args.runs_dir)
    elif args.command == 'template': result = template(registered_case(args.case))
    else:
        if args.observed is None: parser.error('--observed is required')
        result = inspect_run(registered_case(args.case), read_json(args.observed), args.observed.parent)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    status = 'normalized observation; applicability pending' if args.command == 'normalize-run' else result.get('status', 'unrun template')
    print(f'Wrote {args.output}; {status}')

if __name__ == '__main__': main()
