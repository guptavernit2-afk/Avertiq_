"""Bounded output-meaning checks; no concentrations are calculated or inferred."""
from qualify import ROOT, case_hash, read_json

# This is the capture policy for the frozen scalar receptor suite, not an
# assertion that any output has been observed. Exact averaging seconds stay unknown.
EXPECTED = {
    'receptor_statistic': 'reported_maximum_of_time_averaged_concentration',
    'receptor_environment': 'outdoor',
    'receptor_coordinates': 'relative_downwind_crosswind',
    'receptor_height_m': 0,
    'window_start_s': 0,
    'window_end_s': 3600,
    'averaging_basis': 'aloha_toxic_minutes_exact_interval_unresolved',
    'averaging_seconds': None,
    'contour_statistic': 'threshold_exceeded_at_some_time',
    'threshold_use': 'numerical_diagnostic_no_health_authority',
}
BASIS_DESCRIPTIONS = {
    'statistic': EXPECTED['receptor_statistic'],
    'averaging_description': 'Toxic display: few minutes; exact interval unresolved',
    'time_window_description': 'First hour after release start (0-3600 s)',
}


def semantics_template():
    return {'schema_version': 1, 'status': 'unconfirmed',
            **{key: None for key in EXPECTED}, 'evidence_sha256': [], 'capture_notes': None}


def review_output_semantics(observed):
    evidence = read_json(ROOT / 'output-semantics-evidence.json')
    result = {
        'documentation_sha256': case_hash(evidence),
        'status': 'structured_output_semantics_missing',
        'same_engine_comparison_eligible': False, 'comparison_signature': None,
        'exact_averaging_interval_verified': False,
        'instantaneous_peak_available': False, 'time_animation_supported': False,
        'human_evidence_review_required': True,
        'label': 'Recorded output meaning checked only; no model execution or physics qualification',
    }
    if 'output_semantics' not in observed:
        return result
    values = observed['output_semantics']
    if not isinstance(values, dict) or set(values) != set(semantics_template()):
        raise ValueError('Output semantics must use the complete schema; do not infer omitted fields')
    if type(values['schema_version']) is not int or values['schema_version'] != 1 or values['status'] != 'recorded_from_output':
        raise ValueError('Unconfirmed/unsupported output semantics cannot support comparison')
    for key, expected in EXPECTED.items():
        actual = values[key]
        valid = (type(actual) in (int, float) and actual == expected) if type(expected) is int else (actual == expected and type(actual) is type(expected))
        if not valid:
            raise ValueError(f'Unsupported output meaning: {key}; retain the evidence and review a separate output contract')
    if any(observed['basis'].get(key) != value for key, value in BASIS_DESCRIPTIONS.items()):
        raise ValueError('Legacy basis descriptions must match the structured output contract')
    refs = values['evidence_sha256']
    available = {item['sha256'] for item in observed['evidence_files']}
    if (not isinstance(refs, list) or not refs or any(not isinstance(ref, str) for ref in refs)
            or len(refs) != len(set(refs)) or not set(refs).issubset(available)):
        raise ValueError('Output semantics must reference unique hashes of checked raw run evidence')
    if not isinstance(values['capture_notes'], str) or not values['capture_notes'].strip():
        raise ValueError('Record where the outdoor maxima, coordinates and time basis were read')
    result.update(status='recorded_output_semantics_consistent', same_engine_comparison_eligible=True,
                  comparison_signature=case_hash(EXPECTED), recorded={key: values[key] for key in EXPECTED},
                  evidence_sha256=list(refs), capture_notes=values['capture_notes'])
    return result
