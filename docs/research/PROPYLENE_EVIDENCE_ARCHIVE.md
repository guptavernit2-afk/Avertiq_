# Local propylene run evidence archives

The archive milestone prepares the evidence-retention step of the [physics qualification plan](FIRST_PHYSICS_QUALIFICATION.md). It does not run ALOHA. Actual propylene results and source-state applicability remain pending. Only disposable synthetic test archives have been created for verification.

## What this solves

After a future supervised run, manually transcribed values need to stay attached to their raw evidence and exact case. An archive now keeps these together and checks for missing or changed files. There is no automatic collection from ALOHA and no connection to the dashboard.

Each private archive contains:

- The original observation JSON bytes, including original evidence filenames.
- A copy of the observation with only evidence paths remapped to numbered internal files, preserving warnings, unavailable values and their reasons.
- Byte-for-byte raw evidence, the frozen case and the inspection report.
- Snapshots of public engine/mapping/property-review manifests, and hashes of the Python checking code, with line endings normalized.
- An inventory with SHA-256 and byte length for every member, plus a separate archive timestamp. The original run timestamp is unchanged.

Internal numbered names prevent two different source folders' identically named files from colliding. Raw summaries may contain licensed chemical properties: archives are local/private, require the `.avertiq-evidence.zip` suffix, and that suffix is ignored by Git. Keep them under `outputs/`; do not publish them as a public result export.

## Commands after an actual run exists

First complete the [observed record](PROPYLENE_PREPARATION.md) from actual output, with raw files beside it and their hashes recorded. Evidence paths must be relative to the observation's directory; absolute paths, traversal, duplicate paths and linked evidence files/directories are rejected. The original record and files are not edited.

From the Avertiq root:

```powershell
python research/dispersion/archive.py archive-run --case baseline --observed outputs/propylene/baseline.json --output outputs/propylene/archives/baseline-01.avertiq-evidence.zip
python research/dispersion/archive.py verify-archive --archive outputs/propylene/archives/baseline-01.avertiq-evidence.zip
```

The command checks the captured bytes using the existing record inspector before creating the destination. Unrun templates, explicitly synthetic records, inconsistent inputs and changed raw evidence are rejected. Passing inspection means record consistency, not proof of authenticity or model applicability.

Creation prints a receipt containing `archive_sha256`. Retain that hash separately from the archive. To check against it later, supply the actual 64-character lowercase hash:

```powershell
python research/dispersion/archive.py verify-archive --archive outputs/propylene/archives/baseline-01.avertiq-evidence.zip --expected-sha256 HASH_FROM_THE_SEPARATELY_SAVED_RECEIPT
```

The placeholder is not a real hash. Without an independently retained hash, an internal manifest detects accidental inconsistencies but cannot prove that nobody replaced both the data and its hashes. Even a matching external hash establishes byte identity, not that the model run occurred or that its physics is suitable.

## Verification and failure behaviour

| Condition | Behaviour |
|---|---|
| Complete archive, matching current case/configuration/checking code | Verify member inventory and hashes, reconstruct only numbered evidence files in a temporary directory, rerun record inspection and compare the saved report |
| Changed checking code or review configuration | Report `archive_integrity_verified_reinspection_pending`; do not silently reinterpret the historical report or claim current record checks passed |
| Missing/changed members, invalid record, unsupported schema, unsafe member name, duplicate members or wrong independent hash | Fail verification |
| Destination already exists, including a partial earlier file | Refuse overwrite; choose a new archive name |
| Failure while assembling/checking | No destination archive is created |
| Disk failure/interruption during the final exclusive write | A partial destination may remain; it is not a successful archive and verification rejects incomplete ZIPs. Keep original evidence and retry to a new path |

The tool builds and checks the archive before exclusive destination creation, flushes/syncs the completed file, then checks its byte hash. This is not a power-loss-proof storage system or a replacement for an independently stored backup. It never deletes an existing or partially written destination. A failure after a complete write may leave a valid archive; verify it explicitly before relying on it.

Archives use uncompressed ZIP storage, at most 64 raw evidence files, at most 64 MiB per member and 256 MiB for the full archive. Verification accepts only the defined members and writes only generated names into disposable scratch space; it never extracts arbitrary ZIP paths. It does not execute saved files or archived code. Code hashes identify the checking implementation but do not bundle that implementation; retain the repository revision for historical review. If the current frozen-case registry itself is inconsistent, reinspection fails rather than accepting it.

All successful receipts retain `propylene_qualified`, `field_validated` and `dashboard_adapter_enabled` as false. Source-state equivalence and other open mapping gates remain in the saved inspection. The archive is an evidence-preservation step, not a public/operational export or an adapter activation.

## Verification performed

```powershell
python -m unittest discover -s research/dispersion -p 'test_*.py' -v
```

The package has 39 passing tests, including 13 new archive tests. Disposable synthetic cases cover all four variants, original-byte preservation, warnings/nulls, same-named evidence files, changed/missing data, path restrictions, overwritten reports, provenance drift, interrupted writes, existing-file protection, size/format limits and CLI success/failure. No actual propylene run or archive is claimed.
