# Backend handoff — 14 November 2026

The bounded D-001 local backend plan is complete and CLI-verified. The system saves incident inputs, runs labelled illustrative assessments, retains history, recovers interrupted work, exports traceable handovers and creates verified local recovery artifacts. Physical predictions remain a separate unfinished milestone.

## Plan completion

| Planned task | Delivered behaviour | Implementation commit |
|---|---|---|
| Input boundaries | Streaming byte limit, JSON envelope/media-type checks before storage changes; unsupported inputs cannot produce results | `8eac0aa` |
| Duplicate requests and retries | Starting incident version identifies the accepted job; concurrent retries reuse it and preserve newer revisions | `8ff7a7b` |
| Interrupted jobs and storage failures | 60-second request-driven lease, bounded recovery conflicts, reconciliation of writes with lost acknowledgements, truthful unavailable responses | `054407f` |
| Export provenance and stale results | Shared JSON/HTML status; saved revision/job/adapter/time/unit evidence; unavailable geometry and mismatched captures suppressed | `094ec91` |
| Local backup and restore | Inspect/backup/verify/restore CLI; checksums and history validation; exclusive fresh destinations; disposable SQLite recovery tests | `0fa1607` |
| Final verification and handoff | Fresh checks, scope review, remaining-work list and this handoff | This documentation commit |

Original saved-input/job/history implementation: `0687eb9`. The latest application code verified here is `0fa1607`; this closeout changes documentation only.

## Verification actually performed

From the Avertiq repository root on Node 24.15.0:

| Command | Result |
|---|---|
| `npm --prefix website test` | 34 tests passed; includes real disposable SQLite persistence, fault injection, concurrency, export and backup/restore checks |
| `npm --prefix website run typecheck` | Passed |
| `npm --prefix website run build` | Passed |
| `python -m unittest discover -s research/dispersion -p test_qualify.py -v` | 6 evidence-tool tests passed; these are not physical validation cases |

The build still reports a bundle above 500 kB and a framework static route-classification limitation. Neither prevented the build; performance optimization and real browser behaviour are not established by build success. Relevant local documentation links and Git whitespace checks were also checked before commit.

No computer control, browser walkthrough, ALOHA execution, live database restore, hosted migration or deployment was performed for this closeout. Earlier browser verification in the milestone document is historical evidence from the original backend build. These newer changes have CLI coverage only. The equilibrium research and original SurakshaMitra prototype were not modified.

## What remains, in order

1. **When the user is ready:** manually review the current dashboard save/assess/history/export workflow, including a failed request and stale-result export. This is a remaining UI acceptance check, not an unattended task during exams.
2. **Resume the first propylene qualification:** reconstruct the unsaved ALOHA setup; verify chemical identity and source-phase/temperature mapping; version the rounded site coordinates before results; run the frozen baseline and sensitivity cases; retain method, warnings, time/height/averaging basis and observed evidence. Follow the [qualification gates](research/FIRST_PHYSICS_QUALIFICATION.md).
3. **Only after those gates pass:** design a bounded calculated-result adapter with validated inputs and provenance. ALOHA is a supervised desktop reference; a supported headless integration has not been established. Any accepted output must remain labelled calculated research, not field validated.
4. **Separate later research:** methane/CNG and LPG surrogate/mixture applicability, experimental validation, fire radiation, blast and terrain-dependent dispersion each need their own qualification. The 3D map does not supply terrain physics.
5. **Before actual authority/public use:** verified incident data, agency responsibilities, access control, operational acceptance, deployment and communications design. None is enabled by this local demo.

The archived propane software reference reproduced four published values; that does not qualify the propylene incident or real emergency decisions. No completion percentage or date for all physics is claimed.

## Operating limits and recovery

- One local D-001 incident; bounded aggregate history (200 revisions / 400 jobs / bounded events), synchronous illustrative adapter and no background worker.
- Loopback and cross-origin checks do not provide agency authentication. No live multi-tab synchronization: exports reflect the last loaded backend snapshot.
- Backups preserve the incident record, not browser drafts or all D1 metadata. Restore produces a separate verified SQLite artifact; live promotion remains a supervised operation. See the [recovery guide](LOCAL_BACKUP_RESTORE.md).
- No scheduled automation remains. Work continues only in this chat under the user's instructions.

Run/setup: [website README](../website/README.md). Technical contract/history: [backend milestone](BACKEND_MILESTONE.md). Wider direction: [roadmap](ROADMAP.md).

## Short mentor explanation

“We have built and tested the software chain for one incident: save inputs, preserve revisions, request an assessment, handle retries and failures, export its evidence, and recover the saved record from backup. The map results are still explicitly illustrative. Our next scientific step is qualifying the assumed propylene dispersion case before connecting any calculated result. The successful propane reference checks the installed software, not the accident model.”
