"""Create a local review handoff from rechecked records; never execute a model."""
import argparse
import hashlib
from html import escape
from pathlib import Path

from propylene import NAMES, compare_runs, reporting_bound, require
from qualify import case_hash


LABEL = 'Recorded research outputs - applicability pending'
LIMITS = ('Not field validated. Not operational guidance. Propylene qualification and '
          'dashboard physics remain disabled. No model is executed by this exporter. '
          'Human evidence, source-state and applicability review remain required.')


def text(value):
    return escape(str(value), quote=True)


def table(headers, rows):
    head = ''.join(f'<th scope="col">{text(value)}</th>' for value in headers)
    body = ''.join('<tr>' + ''.join(f'<td>{text(value)}</td>' for value in row) + '</tr>' for row in rows)
    return f'<div class="table"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def listing(values, empty='None recorded'):
    return '<ul>' + ''.join(f'<li>{text(value)}</li>' for value in (values or [empty])) + '</ul>'


def reading(value, reason=None, bound=None):
    parts = ['Unavailable' if value is None else str(value)]
    if bound:
        symbol = {'gt': '>', 'ge': '>=', 'lt': '<', 'le': '<='}[bound['relation']]
        parts.append(f"Reported bound: {symbol} {bound['bound_value']} {bound['unit']}")
    if reason:
        parts.append(reason)
    return '\n'.join(parts)


def comparison_table(rows, key, unit):
    return table([key, f'Baseline ({unit})', f'Variant ({unit})', f'Variant - baseline ({unit})', 'Variant / baseline'], [
        [row[key], reading(row[f'baseline_{unit}'], row['baseline_unavailable_reason'], row['baseline_reporting_bound']),
         reading(row[f'variant_{unit}'], row['variant_unavailable_reason'], row['variant_reporting_bound']),
         reading(row[f'difference_{unit}'], row['difference_unavailable_reason']),
         reading(row['ratio'], row['ratio_unavailable_reason'])] for row in rows])


def render_handoff(comparison):
    # This is presentation only. The public export entry point below always
    # reconstructs this comparison from the original observations and evidence.
    require(all(comparison.get(flag) is False for flag in
                ('propylene_qualified', 'field_validated', 'dashboard_adapter_enabled')),
            'Review handoff must not claim qualification')
    parts = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width, initial-scale=1">',
             '<title>Propylene sensitivity review - applicability pending</title>',
             '<style>body{font:16px/1.5 system-ui,sans-serif;max-width:1200px;margin:2rem auto;padding:0 1rem;color:#17202a}h1,h2,h3{line-height:1.2}.notice{border:2px solid #9c6500;padding:1rem;background:#fff8e5}.table{overflow-x:auto;margin:1rem 0}table{border-collapse:collapse;width:100%}th,td{border:1px solid #bbc4cc;padding:.55rem;text-align:left;vertical-align:top;white-space:pre-wrap;overflow-wrap:anywhere}th{background:#edf1f4}section{border-top:1px solid #bbc4cc;margin-top:2rem}code{overflow-wrap:anywhere}@media print{body{max-width:none;margin:0}thead{display:table-header-group}tr{break-inside:avoid}.table{overflow:visible}}</style>',
             '</head><body><h1>Propylene sensitivity review handoff</h1>',
             f'<div class="notice"><strong>{text(LABEL)}</strong><p>{text(LIMITS)}</p>',
             '<p>Local review copy. Transcribed text and evidence names require content and redistribution review before sharing. Raw evidence is not embedded.</p></div>',
             '<h2>Traceability</h2>',
             table(['Item', 'Value'], [
                 ['Checked comparison SHA-256 (canonical JSON)', case_hash(comparison)],
                 ['Handoff tool SHA-256 (LF-normalized UTF-8)', hashlib.sha256(Path(__file__).read_text(encoding='utf-8').encode()).hexdigest()],
                 ['Propylene qualified', 'false'], ['Field validated', 'false'], ['Dashboard adapter enabled', 'false']]),
             '<p>The comparison hash identifies the checked JSON content, not authenticity or physical validity. Re-run compare-runs on the same unchanged records to reproduce it.</p>',
             '<h2>Baseline and sensitivity comparisons</h2>',
             '<p>Differences are variant minus baseline; ratios are variant divided by baseline. Diagnostic thresholds confer no health or evacuation authority. No monotonic trend is assumed; unavailable or bounded values are not zero.</p>']
    for item in comparison['comparisons']:
        parts += [f'<section><h3>{text(item["variant"])}</h3>',
                  table(['Changed input', 'Unit', 'Baseline', 'Variant'], [[v['field'], v['unit'], v['baseline'], v['variant']] for v in item['changed_inputs']]),
                  f'<p>{text(item["reason"])}</p>']
        if item['comparison_blockers']:
            parts += ['<p>Numerical comparison withheld:</p>', listing(item['comparison_blockers'])]
        else:
            parts += ['<h4>Receptor concentrations</h4>', comparison_table(item['receptor_changes'], 'downwind_m', 'ppm'),
                      '<h4>Diagnostic contour distances</h4>', comparison_table(item['contour_changes'], 'level_ppm', 'm')]
        parts += ['</section>']
    parts += ['<h2>Checked run records and outstanding review</h2>']
    for name in NAMES:
        run = comparison['runs'][name]
        parts += [f'<section><h3>{text(name)} - {text(run["case_id"])}</h3>',
                  table(['Record', 'Value'], [['Case SHA-256', run['case_sha256']], ['Recorded UTC run time', run['run_at_utc']],
                        ['Engine', f"{run['engine']['name']} {run['engine']['version']}"],
                        ['Executable SHA-256', run['engine']['executable_sha256']], ['Selected dispersion method', run['dispersion_method']],
                        ['Airborne mass (kg)', run['source_summary']['airborne_mass_kg']], ['Duration (s)', run['source_summary']['duration_s']]]),
                  '<h4>Output basis</h4>', table(['Field', 'Recorded value'], run['basis'].items()),
                  '<h4>Output review status</h4>', table(['Review', 'Status'], [
                      ['Structured output semantics', run['output_semantics_review']['status']],
                      ['Exact averaging interval verified', str(run['output_semantics_review']['exact_averaging_interval_verified']).lower()],
                      ['Raw-unit transcription', run['unit_transcription_review']['status']]]),
                  '<h4>Recorded receptors</h4>']
        parts += [table(['Downwind (m)', 'Crosswind (m)', 'Concentration (ppm)'], [
            [row['downwind_m'], row['crosswind_m'], reading(row['value_ppm'], row.get('unavailable_reason'),
             reporting_bound(run, f"receptor.{row['downwind_m']:g}.value_ppm"))] for row in run['receptors']]),
                  '<h4>Recorded diagnostic contours</h4>', table(['Threshold (ppm)', 'Downwind distance (m)'], [
            [row['level_ppm'], reading(row['downwind_m'], row.get('unavailable_reason'),
             reporting_bound(run, f"contour.{row['level_ppm']:g}.downwind_m"))] for row in run['contours']]),
                  '<h4>Model warnings</h4>', listing(run['warnings'], 'No warnings recorded'),
                  '<h4>Open mapping gates</h4>', listing(run['open_mapping_gates']),
                  '<h4>Operator notes</h4>', f'<p>{text(run["operator_notes"])}</p>',
                  '<h4>Mapping review</h4>', f'<p>{text(run["mapping_review"])}</p>',
                  '<h4>Evidence inventory (raw files retained locally)</h4>',
                  table(['Evidence name', 'SHA-256'], [[entry['name'], entry['sha256']] for entry in run['evidence_files']]), '</section>']
    parts += [f'<footer><p>{text(LABEL)}. {text(LIMITS)}</p></footer></body></html>']
    return '\n'.join(parts) + '\n'


def export_handoff(runs_dir, output):
    output = Path(output)
    require(output.suffix.lower() == '.html', 'Use an .html destination for the local review handoff')
    require(not output.exists() and not output.is_symlink(), 'Choose a fresh output path; overwrite is refused')
    comparison = compare_runs(runs_dir)
    document = render_handoff(comparison)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as stream:
        stream.write(document)
    return {'status': 'local_review_handoff_created_applicability_pending',
            'checked_comparison_sha256': case_hash(comparison),
            'model_calculation_performed': False, 'propylene_qualified': False,
            'field_validated': False, 'dashboard_adapter_enabled': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs-dir', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        result = export_handoff(args.runs_dir, args.output)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'Review handoff failed: {error}\n')
    print(f"Wrote {args.output}; {result['status']}")


if __name__ == '__main__':
    main()
