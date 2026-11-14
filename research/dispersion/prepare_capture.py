"""Prepare blank four-case capture records. Never execute ALOHA or fill results."""
import argparse
import hashlib
import json
from pathlib import Path

from output_semantics import semantics_template
from propylene import NAMES, registered_case, require, template
from qualify import case_hash
from transcription import transcription_template


FLAGS = {'model_calculation_performed': False, 'propylene_qualified': False,
         'field_validated': False, 'dashboard_adapter_enabled': False}
MANIFEST = 'capture-manifest.json'
GUIDE = '''UNRUN PROPYLENE CAPTURE FOLDER

This folder contains blank records, not model results or evidence of applicability.
Actual ALOHA source-state compatibility and physical acceptance remain pending.
The inputs/ files are assumed frozen case snapshots, NOT observed model entries.
Do not copy their values into observed_inputs as a substitute for observation.

Before any supervised run, review the repository's first physics qualification
and source-treatment gates. If the source cannot be represented, reject or
explicitly revise the case; never silently substitute another chemical/model.

For each case, after actual output exists:
1. Save raw evidence in evidence/CASE/ and retain its actual SHA-256 hashes.
2. Fill CASE-capture.json from observed inputs, engine identity, UTC run time,
   selected method, source summary, warnings and mapping/operator review.
   Reference raw files with paths such as evidence/baseline/summary.txt.
3. Fill output_semantics from the actual output and set recorded_from_output
   only when supported. Exact averaging remains unresolved under this contract.
4. Fill the transcription supplement with original tokens, units, relations,
   reasons, evidence hashes and locations. Bounds/missing readings are not zero.
   Mark the supplement recorded_from_output only after capture.
5. Set run_completed=true only for a completed actual run. Leave all physical
   qualification and dashboard flags false. Never use test/expected answers.

From the repository root (replace CAPTURE_FOLDER and CASE; quote paths):
python research/dispersion/propylene.py normalize-run --case CASE --observed "CAPTURE_FOLDER/CASE-capture.json" --output "CAPTURE_FOLDER/CASE.json"
python research/dispersion/propylene.py inspect-run --case CASE --observed "CAPTURE_FOLDER/CASE.json" --output "CAPTURE_FOLDER/CASE-checked.json"

After all four observations exist and pass their record checks:
python research/dispersion/propylene.py compare-runs --runs-dir "CAPTURE_FOLDER" --output "CAPTURE_FOLDER/comparison.json"
python research/dispersion/review_handoff.py --runs-dir "CAPTURE_FOLDER" --output "CAPTURE_FOLDER/review-handoff.html"

Existing output paths are refused. Archives and raw evidence stay local under
outputs/; see docs/research/PROPYLENE_EVIDENCE_ARCHIVE.md for preservation.
This tool does not launch ALOHA, close gates, enable physics or publish files.

capture-manifest.json records INITIAL generated files/hashes, not completed
observations. After manual edits those initial hashes are expected to differ;
use the existing observation/evidence checks, not this manifest, for run review.
A missing, malformed or incomplete manifest means setup is incomplete. Preserve
partial files and retry with a fresh folder; do not merge a retry into this one.
'''


def encode(value):
    return (json.dumps(value, indent=2, allow_nan=False) + '\n').encode('utf-8')


def package():
    files = {'README.txt': GUIDE.encode('utf-8')}
    cases = []
    for name in NAMES:
        case = registered_case(name)
        capture = template(case)
        capture['output_semantics'] = semantics_template()
        capture['transcription'] = transcription_template(case)
        capture.update({key: False for key in ('propylene_qualified', 'field_validated', 'dashboard_adapter_enabled')})
        capture['label'] = 'UNRUN capture template; supplements unconfirmed; no observed output or physics qualification'
        files[f'inputs/{name}.json'] = encode(case)
        files[f'{name}-capture.json'] = encode(capture)
        cases.append({'variant': name, 'case_id': case['id'], 'case_sha256': case_hash(case),
                      'input_snapshot': f'inputs/{name}.json', 'capture_record': f'{name}-capture.json',
                      'evidence_directory': f'evidence/{name}'})
    manifest = {'schema_version': 1, 'status': 'prepared_unrun', **FLAGS, 'cases': cases,
                'initial_files': {name: {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
                                  for name, data in files.items()},
                'label': 'Initial blank capture setup only; not observed evidence or physical validation'}
    return files, manifest


def prepare_folder(output):
    output = Path(output)
    require(not output.exists() and not output.is_symlink(), 'Choose a fresh capture folder; existing destinations are refused')
    files, manifest = package()
    manifest_bytes = encode(manifest)
    # All case validation and serialization precedes destination creation.
    output.mkdir(parents=True, exist_ok=False)
    (output / 'inputs').mkdir()
    for name in NAMES:
        (output / 'evidence' / name).mkdir(parents=True)
    for name, data in files.items():
        with (output / name).open('xb') as stream:
            stream.write(data)
    # A valid complete manifest is the final setup marker. Never delete partial
    # output on failure; it must be diagnosed and a fresh destination chosen.
    with (output / MANIFEST).open('xb') as stream:
        stream.write(manifest_bytes)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        manifest = prepare_folder(args.output)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'Capture preparation failed: {error}\n')
    print(f"Prepared {args.output}; {manifest['status']}; four blank records; no model execution")


if __name__ == '__main__':
    main()
