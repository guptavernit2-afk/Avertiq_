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

Pending implementation and verification.
