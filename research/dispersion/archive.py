"""Local propylene evidence archives. Never executes ALOHA or grants qualification."""
import argparse
import copy
import hashlib
import io
import json
import os
import re
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from propylene import NAMES, inspect_run, registered_case, require, utc
from qualify import ROOT, case_hash, read_json

MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_ARCHIVE_BYTES = 256 * 1024 * 1024
MAX_EVIDENCE_FILES = 64
FIXED_MEMBERS = {'observed-original.json', 'observed.json', 'case.json', 'inspection.json', 'provenance.json'}
CONFIGS = ('engine-manifest.json', 'mapping-evidence.json', 'propylene-state-evidence.json', 'source-treatment-evidence.json')
TOOLS = ('archive.py', 'propylene.py', 'qualify.py', 'source_state.py', 'source_treatment.py')
FLAGS = {'propylene_qualified': False, 'field_validated': False, 'dashboard_adapter_enabled': False}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, indent=2, allow_nan=False) + '\n').encode('utf-8')


def decode(data):
    def invalid(value):
        raise ValueError(f'Non-finite JSON: {value}')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f'Duplicate JSON key: {key}')
            result[key] = value
        return result
    value = json.loads(data.decode('utf-8'), parse_constant=invalid, object_pairs_hook=unique)
    require(isinstance(value, dict), 'Expected a JSON object')
    return value


def bounded_read(path, limit=MAX_FILE_BYTES):
    with Path(path).open('rb') as stream:
        data = stream.read(limit + 1)
    require(len(data) <= limit, 'File exceeds archive size limit')
    return data


def local_evidence_path(base, name):
    require(isinstance(name, str) and bool(name), 'Evidence path required')
    # Accept Windows separators, but no drive, ADS, root, traversal or aliases.
    parts = name.replace('\\', '/').split('/')
    require(all(p and p not in ('.', '..') and ':' not in p for p in parts), 'Evidence path must be a plain relative path')
    path = base
    for part in parts:
        path = path / part
        require(not path.is_symlink() and not getattr(path, 'is_junction', lambda: False)(), 'Linked evidence paths are unsupported')
    require(path.resolve().is_relative_to(base) and path.is_file(), 'Evidence must stay within its record directory')
    return path


def provenance():
    return {
        'configuration_snapshots': {name: read_json(ROOT / name) for name in CONFIGS},
        # Normalize line endings so Git checkout conventions do not imply code drift.
        'tool_sha256_lf_utf8': {name: digest((ROOT / name).read_text(encoding='utf-8').encode('utf-8')) for name in TOOLS},
    }


def inspect_captured(case, observed, payloads):
    # Write only internally generated names into a disposable directory; never extract a ZIP.
    with tempfile.TemporaryDirectory(prefix='avertiq-evidence-check-') as folder:
        base = Path(folder)
        (base / 'evidence').mkdir()
        for name, data in payloads.items():
            require(re.fullmatch(r'evidence/[0-9]{4}\.bin', name) is not None, 'Invalid internal evidence name')
            (base / name).write_bytes(data)
        return inspect_run(case, observed, base)


def archive_run(variant, observed_path, output):
    output = Path(output)
    require(output.name.endswith('.avertiq-evidence.zip'), 'Use the ignored .avertiq-evidence.zip suffix for private raw evidence')
    require(not output.exists() and not output.is_symlink(), 'Choose a new archive path; overwrite is refused')
    case = registered_case(variant)
    observed_path = Path(observed_path).resolve()
    original_bytes = bounded_read(observed_path)
    original = decode(original_bytes)
    evidence = original.get('evidence_files')
    require(isinstance(evidence, list) and 0 < len(evidence) <= MAX_EVIDENCE_FILES, 'Supply 1 to 64 evidence files')
    normalized = copy.deepcopy(original)
    normalized['evidence_files'] = []
    payloads, seen = {}, set()
    total = len(original_bytes)
    for index, item in enumerate(evidence):
        path = local_evidence_path(observed_path.parent, item['path'])
        require(path.resolve() not in seen, 'Duplicate evidence path')
        seen.add(path.resolve())
        data = bounded_read(path)
        total += len(data)
        require(total <= MAX_ARCHIVE_BYTES, 'Evidence exceeds total archive limit')
        require(digest(data) == item['sha256'], 'Evidence hash mismatch during capture')
        name = f'evidence/{index:04d}.bin'
        payloads[name] = data
        normalized['evidence_files'].append({'path': name, 'sha256': digest(data)})
    report = inspect_captured(case, normalized, payloads)
    members = {**payloads, 'observed-original.json': original_bytes,
               'observed.json': encode(normalized), 'case.json': encode(case),
               'inspection.json': encode(report), 'provenance.json': encode(provenance())}
    manifest = {
        'schema_version': 1, 'variant': variant, 'case_sha256': case_hash(case),
        'archived_at_utc': datetime.now(timezone.utc).isoformat(),
        'files': {name: {'sha256': digest(data), 'bytes': len(data)} for name, data in members.items()},
        'label': 'Private evidence archive; record consistency only; applicability pending', **FLAGS,
    }
    # Fully assemble and check before touching the requested destination.
    with io.BytesIO() as buffer:
        with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_STORED) as archive:
            for name, data in members.items():
                archive.writestr(name, data)
            archive.writestr('manifest.json', encode(manifest))
        data = buffer.getvalue()
    require(len(data) <= MAX_ARCHIVE_BYTES, 'Archive exceeds total size limit')
    result = verify_bytes(data)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation preserves any competing/existing archive. A disk failure
    # may leave a partial file; verification rejects it and retries need a new path.
    with output.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    require(digest(bounded_read(output, MAX_ARCHIVE_BYTES)) == result['archive_sha256'], 'Written archive differs from checked bytes')
    return result


def verify_bytes(data, expected_sha256=None):
    require(len(data) <= MAX_ARCHIVE_BYTES, 'Archive exceeds total size limit')
    archive_hash = digest(data)
    if expected_sha256 is not None:
        require(re.fullmatch(r'[0-9a-f]{64}', expected_sha256) is not None, 'Expected SHA-256 must be 64 lowercase hex characters')
        require(archive_hash == expected_sha256, 'Archive differs from independently retained SHA-256')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        require(len(entries) <= MAX_EVIDENCE_FILES + len(FIXED_MEMBERS) + 1, 'Too many archive members')
        require(len(names) == len(set(n.casefold() for n in names)), 'Duplicate archive members')
        require(set(names) >= FIXED_MEMBERS | {'manifest.json'}, 'Incomplete archive')
        require(all(name in FIXED_MEMBERS | {'manifest.json'} or re.fullmatch(r'evidence/[0-9]{4}\.bin', name) for name in names), 'Unexpected archive path')
        require(all(e.compress_type == zipfile.ZIP_STORED and not e.flag_bits & 1 and 0 <= e.file_size <= MAX_FILE_BYTES for e in entries), 'Unsupported compression, encryption or member size')
        require(sum(e.file_size for e in entries) <= MAX_ARCHIVE_BYTES, 'Expanded archive exceeds limit')
        contents = {name: archive.read(name) for name in names}
    manifest = decode(contents.pop('manifest.json'))
    require(type(manifest.get('schema_version')) is int and manifest['schema_version'] == 1, 'Unknown archive schema')
    require(manifest.get('variant') in NAMES, 'Unknown case variant')
    utc(manifest.get('archived_at_utc'))
    require(all(manifest.get(flag) is False for flag in FLAGS), 'Archive must not claim qualification')
    expected_files = {name: {'sha256': digest(payload), 'bytes': len(payload)} for name, payload in contents.items()}
    require(manifest.get('files') == expected_files, 'Archive member hash, size or inventory mismatch')
    original = decode(contents['observed-original.json'])
    observed = decode(contents['observed.json'])
    case = decode(contents['case.json'])
    report = decode(contents['inspection.json'])
    captured_provenance = decode(contents['provenance.json'])
    require(case_hash(case) == manifest.get('case_sha256') == original.get('case_sha256'), 'Archive case identity mismatch')
    source_files = original.get('evidence_files')
    require(isinstance(source_files, list) and 0 < len(source_files) <= MAX_EVIDENCE_FILES, 'Missing original evidence inventory')
    normalized = copy.deepcopy(original)
    normalized['evidence_files'] = [{'path': f'evidence/{i:04d}.bin', 'sha256': item['sha256']} for i, item in enumerate(source_files)]
    require(observed == normalized, 'Archived observation changed beyond evidence path remapping')
    payloads = {name: value for name, value in contents.items() if name.startswith('evidence/')}
    require(set(payloads) == {item['path'] for item in normalized['evidence_files']}, 'Evidence inventory differs from observation')
    require(all(digest(payloads[item['path']]) == item['sha256'] for item in normalized['evidence_files']), 'Captured evidence differs from original hashes')
    require(all(report.get(flag) is False for flag in FLAGS), 'Inspection must not claim qualification')
    current = captured_provenance == provenance() and case_hash(case) == case_hash(registered_case(manifest['variant']))
    if current:
        require(inspect_captured(case, observed, payloads) == report, 'Archived inspection differs from current checks')
    return {
        'status': 'archive_verified_applicability_pending' if current else 'archive_integrity_verified_reinspection_pending',
        'archive_sha256': archive_hash, 'external_hash_matched': expected_sha256 is not None,
        'case_id': case['id'], 'case_sha256': case_hash(case), 'evidence_file_count': len(payloads),
        'integrity_checks_passed': True, 'current_provenance_matches': current, 'record_reinspection_passed': current,
        'model_executed_by_archive_tool': False, **FLAGS,
        'label': 'File integrity and optional record reinspection only; not authenticity or physics validation',
    }


def verify_archive(path, expected_sha256=None):
    return verify_bytes(bounded_read(path, MAX_ARCHIVE_BYTES), expected_sha256)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    create = commands.add_parser('archive-run')
    create.add_argument('--case', choices=NAMES, required=True)
    create.add_argument('--observed', type=Path, required=True)
    create.add_argument('--output', type=Path, required=True)
    verify = commands.add_parser('verify-archive')
    verify.add_argument('--archive', type=Path, required=True)
    verify.add_argument('--expected-sha256')
    args = parser.parse_args()
    try:
        result = (archive_run(args.case, args.observed, args.output) if args.command == 'archive-run'
                  else verify_archive(args.archive, args.expected_sha256))
    except (ValueError, OSError, KeyError, TypeError, zipfile.BadZipFile) as error:
        parser.exit(1, f'Archive check failed: {error}\n')
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
