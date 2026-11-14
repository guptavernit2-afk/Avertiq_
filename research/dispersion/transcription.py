"""Convert recorded output units; preserve bounds, never infer model results."""
import copy
import math
import re
from decimal import Decimal, localcontext
from qualify import ROOT, case_hash, read_json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def targets(case):
    result = {'source_summary.airborne_mass_kg': ('mass', 'source_summary', None, 'airborne_mass_kg'),
              'source_summary.duration_s': ('time', 'source_summary', None, 'duration_s')}
    for x in case['requested_outputs']['centerline_downwind_m']:
        result[f'receptor.{x}.value_ppm'] = ('concentration', 'receptors', x, 'value_ppm')
    for x in case['requested_outputs']['diagnostic_contours_ppm']:
        result[f'contour.{x}.downwind_m'] = ('length', 'contours', x, 'downwind_m')
    return result


def transcription_template(case):
    return {'schema_version': 1, 'status': 'unconfirmed', 'items': [
        {'target': target, 'value_text': None, 'unit': None, 'relation': None,
         'reason': None, 'evidence_sha256': None, 'evidence_location': None}
        for target in targets(case)]}


def normalize_reading(quantity, item):
    policy = read_json(ROOT / 'unit-conversion-evidence.json')['quantities'][quantity]
    unit, relation, token, reason = (item.get(k) for k in ('unit', 'relation', 'value_text', 'reason'))
    require(relation in ('reported', 'gt', 'ge', 'lt', 'le', 'unavailable'), 'Explicit supported reporting relation required')
    require(isinstance(unit, str) and unit in policy['factors'] or unit is None and relation == 'unavailable', 'Unsupported or dimensionally incompatible unit')
    value = None
    if relation == 'unavailable':
        require(token is None and isinstance(reason, str) and reason.strip(), 'Unavailable output needs no number and an observed reason')
    else:
        require(isinstance(token, str) and len(token) <= 80 and re.fullmatch(r'[+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]{1,3})?', token), 'Use an unambiguous nonnegative decimal token; keep qualifiers and units separate')
        with localcontext() as context:
            context.prec = 100
            converted = Decimal(token) * Decimal(policy['factors'][unit])
            require(converted.is_finite() and (converted == 0 or -100 <= converted.adjusted() <= 100), 'Numeric value is outside transcription bounds')
            value = float(converted)
        require(math.isfinite(value), 'Converted value must be finite')
        if quantity == 'concentration':
            require(value <= 1e6 and not (relation == 'gt' and value == 1e6), 'Gas-volume ppm exceeds supported fraction range')
        require(not (relation == 'lt' and value == 0), 'Strictly negative output is unsupported')
        if relation == 'reported':
            require(reason is None, 'Reported scalar cannot also have an unavailable reason')
        else:
            require(isinstance(reason, str) and reason.strip(), 'Bounded output needs the observed limiting reason')
    scalar = value if relation == 'reported' else None
    normalized_reason = reason if relation == 'unavailable' else None
    if relation in ('gt', 'ge', 'lt', 'le'):
        symbol = {'gt': '>', 'ge': '>=', 'lt': '<', 'le': '<='}[relation]
        normalized_reason = f'Reported {symbol} {token} {unit}; {reason}'
    return {'unit': policy['unit'], 'relation': relation, 'value': scalar,
            'bound_value': value if relation not in ('reported', 'unavailable') else None,
            'unavailable_reason': normalized_reason,
            'factor': policy['factors'].get(unit),
            'precision_note': 'Unit conversion does not increase the precision of the displayed value'}


def converted_items(case, observed):
    block = observed.get('transcription')
    require(isinstance(block, dict) and set(block) == {'schema_version', 'status', 'items'}, 'Complete transcription object required')
    require(type(block['schema_version']) is int and block['schema_version'] == 1 and block['status'] == 'recorded_from_output', 'Unconfirmed/unsupported transcription cannot be normalized')
    entries = block['items']
    expected = targets(case)
    require(isinstance(entries, list) and len(entries) == len(expected), 'Transcription must cover every source summary, receptor and contour value')
    available = {item['sha256'] for item in observed['evidence_files']}
    result = {}
    keys = set(transcription_template(case)['items'][0])
    for item in entries:
        require(isinstance(item, dict) and set(item) == keys, 'Complete transcription item required')
        name = item['target']
        require(isinstance(name, str) and name in expected and name not in result, 'Unknown or duplicate transcription target')
        require(isinstance(item['evidence_sha256'], str) and item['evidence_sha256'] in available, 'Transcription must reference raw run evidence')
        require(isinstance(item['evidence_location'], str) and item['evidence_location'].strip(), 'Record the page, section or graph label for each transcribed value')
        result[name] = normalize_reading(expected[name][0], item)
        if expected[name][1] == 'source_summary':
            require(result[name]['relation'] == 'reported', 'Source mass and duration need reported scalars for this qualification contract')
    return result


def row_for(observed, spec):
    _, group, identifier, field = spec
    if group == 'source_summary':
        return observed[group], field
    key = 'downwind_m' if group == 'receptors' else 'level_ppm'
    matches = [row for row in observed[group] if type(row.get(key)) in (int, float) and row[key] == identifier]
    require(len(matches) == 1, 'Missing or duplicate output location/threshold')
    return matches[0], field


def apply_transcription(case, observed):
    values = converted_items(case, observed)
    result = copy.deepcopy(observed)
    for name, spec in targets(case).items():
        row, field = row_for(result, spec)
        row[field] = values[name]['value']
        if spec[1] != 'source_summary':
            row['unavailable_reason'] = values[name]['unavailable_reason']
    result.update(propylene_qualified=False, field_validated=False, dashboard_adapter_enabled=False,
                  label='Normalized recorded outputs only; applicability and physics qualification pending')
    return result


def review_transcription(case, observed):
    evidence = read_json(ROOT / 'unit-conversion-evidence.json')
    result = {'status': 'raw_unit_transcription_not_supplied', 'conversion_evidence_sha256': case_hash(evidence),
              'human_transcription_review_required': True, 'model_calculation_performed': False}
    if 'transcription' not in observed:
        return result
    values = converted_items(case, observed)
    for name, spec in targets(case).items():
        row, field = row_for(observed, spec)
        expected = values[name]['value']
        actual = row[field]
        require(actual is None if expected is None else type(actual) in (int, float) and actual == expected, 'Normalized output differs from raw transcription')
        if spec[1] != 'source_summary':
            require(row.get('unavailable_reason') == values[name]['unavailable_reason'], 'Reporting bound/unavailable reason was changed or lost')
    result.update(status='raw_unit_transcription_consistent', conversions=values)
    return result
