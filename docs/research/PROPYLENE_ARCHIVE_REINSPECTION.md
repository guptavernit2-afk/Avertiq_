# Explicit archived-record reinspection plan

Planned 15 November 2026 before implementation. This extends the evidence-retention and traceability work in [first physics qualification](FIRST_PHYSICS_QUALIFICATION.md) and [local archives](PROPYLENE_EVIDENCE_ARCHIVE.md). Existing verification deliberately leaves record reinspection pending when checking-code/configuration provenance changes. Add an explicit, auditable way to perform that current check while preserving historical evidence.

## Scope and acceptance

1. Add `reinspect-archive` to the existing archive CLI. First validate the archive format, inventory, hashes and optional independently retained SHA-256 using the existing verifier.
2. Require the archived case to match the current registered variant exactly. Reconstruct only generated numbered evidence files in temporary space; invoke the current record inspector without running archived code or executing a model.
3. Write a new JSON receipt containing archive identity, historical inspection/provenance hashes, current inspection/provenance, whether provenance and report content changed, and unchanged false qualification/field/dashboard flags. State that this is current record consistency, not historical authenticity, model rerun or scientific approval.
4. Preserve archive bytes and historical inspection unchanged. Serialize before exclusive output creation; reject existing output files, wrong independent hashes, incompatible frozen cases and records rejected by current rules. No successful receipt for an incomplete/failed reinspection.
5. Test unchanged and drifted archives, failed current checks, changed case/configuration, corrupt evidence, overwrite protection, archive preservation and CLI behaviour using disposable synthetic archives. Run full qualification tests and Windows/Linux CI before PR merge.

## Delivery and limits

Plan commit first on `codex/archive-reinspection`, then implement, test, open a PR, review diff/checks and merge. All work is CLI-only. No actual archive, model run, physics result, dashboard adapter or deployment is created. Hashes establish identity/consistency, not authenticity; an explicit reinspection never modifies or upgrades the historical archive.

## Completion

Implemented on the planned feature branch. All 90 qualification-tool tests pass locally, including eight new reinspection tests. Synthetic tests cover all registered variants, code/configuration drift, changed historical report wording, failed current record rules, changed frozen cases, corrupt evidence, wrong external hashes, existing receipts, provenance changing during a check, CLI operation and unchanged archive bytes.

Only disposable synthetic archives/receipts were used. Submit the branch as a PR and merge after diff review and successful Windows/Linux CI. Actual ALOHA runs and physical qualification remain pending.


## Future local workflow

Use ordinary verification first. If it reports `archive_integrity_verified_reinspection_pending`, preserve that status as a description of the historical archive. To request a separate current check explicitly:

```powershell
python research/dispersion/archive.py reinspect-archive --archive outputs/propylene/archives/baseline-01.avertiq-evidence.zip --expected-sha256 HASH_FROM_THE_SEPARATELY_SAVED_RECEIPT --output outputs/propylene/reinspection/baseline-01-current.json
```

The hash is a placeholder; use the real independently retained SHA-256 or omit the optional argument. Without it, the receipt explicitly records `external_hash_matched: false`; internal consistency cannot establish that the archive was not replaced. Keep the new receipt local because it includes current inspection metadata and notes.

An unchanged archive can also be explicitly reinspected. The command accepts only the current registered version of its variant, reconstructs numbered raw-evidence files in temporary space, and runs current record checks. It does not use the old inspection as a substitute for checking the observation, nor execute archived code. Tool/configuration provenance must stay stable during the current check.

The receipt contains the archive byte hash, canonical historical inspection/provenance hashes, full current inspection/provenance with their canonical hashes, the reinspection timestamp, and separate indicators of provenance/report changes. `record_reinspection_passed` describes current software checks only. `propylene_qualified`, `field_validated`, `dashboard_adapter_enabled`, `model_executed_by_archive_tool` and `historical_archive_modified` remain false. No run timestamp or original evidence is changed.

The old archive remains unchanged, including its original inspection and provenance. Ordinary verification can therefore still report historical reinspection pending; the separate receipt records the explicit new check. Retain both artifacts and the repository revision. A later checker change requires another explicit check, not editing this receipt.

Wrong hashes, corrupt members, changed case identity and records failing current rules produce no successful receipt. Existing output paths are never overwritten. Validation and serialization finish before destination creation; a storage interruption during writing can still leave an incomplete file. Preserve it for diagnosis and retry with a fresh `.json` path. A receipt is not an authenticated signature or physics-approval artifact.
