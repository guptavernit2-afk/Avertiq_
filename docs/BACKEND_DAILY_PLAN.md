# Daily backend plan: 14–20 November 2026

User authorized independent CLI-only backend work and daily scoped commits/pushes during exams. No computer control, browser automation, visible windows or ALOHA runs. Work stays in this chat. The user cancelled scheduling; no autonomous daily run is configured.

## Completion status

All six bounded tasks are complete as of 14 November 2026. Final verification: 34 application/backup tests, 6 qualification-tool tests, typecheck and build passed. See [handoff and remaining work](BACKEND_HANDOFF_2026-11-14.md). No daily schedule is active. Historical progress entries below describe each stage; their next-task notes are superseded by this completion status.

## Bounded order

Aim for 3–4 bounded tasks per active workday, inspecting existing implementation first; prioritize tested completion over task counts. Skip already satisfied requirements; do not add features just to consume credits.

1. Audit incident API input boundaries: malformed bodies, numeric/unit bounds, unsupported chemicals, and forged calculated results. Fix demonstrated gaps with regression tests.
2. Assess duplicate assessment submissions and version conflicts. Make retry behaviour deterministic without duplicate jobs or overwriting immutable input revisions; preserve existing API compatibility.
3. Audit interrupted queued/running job recovery, terminal events and storage failures. Add targeted failure tests and fix demonstrated gaps.
4. Strengthen export provenance: saved revision, adapter version, status, timestamps and illustrative evidence must remain consistent; unavailable/stale results must never carry usable geometry.
5. Add a local backup/restore procedure for the existing database, with integrity checks and a disposable-database restoration test. Never overwrite the user's live database automatically.
6. Run the relevant backend tests/typecheck/build, review scope and document remaining gaps and a concise mentor handoff. No browser verification is authorized; report that limit.

## Boundaries

Keep D-001 single-incident scope. No agency authentication, multi-tenant deployment, live dispatch, new physical solver, headless ALOHA integration or terrain calculations. Preserve research/equilibrium and SurakshaMitra. Do not enable calculated results. No secrets, local databases, installers, licensed property tables or unrelated screenshots in commits. Verify origin before mutations and push normally without force. Record an actual blocker instead of claiming success.

## Progress

- 14 November: reconciled qualification documentation with the archived successful propane software reference. Propylene setup was unsaved and remains pending. Frozen input sheets retain their original pre-run gates; the separate comparison report records subsequent evidence. Daily backend work scheduled for six runs; inspect this log on each run to avoid duplication.

- 14 November follow-up: deleted the scheduled automation at user request. Completed first API boundary audit: streamed UTF-8 byte limit, exact JSON media-type and object/version validation, and rejection before storage initialization/recovery. Added two regression tests covering malformed envelopes, media types, multibyte limits and state preservation. Existing tests retain numeric/unsupported-input and forged-result protections. All 15 tests and typecheck pass. Browser checks intentionally omitted under user instruction.

- Duplicate/retry task completed: persist the initiating version on each job; repeated POSTs reuse it and concurrent requests resolve to one job. Preserve current revision/stale geometry rules and legacy conflict handling. Added regression coverage; next bounded task is interrupted-job recovery and storage failures.

- Recovery/storage task: consistent 60-second lease clock, bounded conflict reconciliation, and persisted-state checks after uncertain writes. Added SQLite fault-injection and recovery-race tests. Next task is export provenance and unavailable/stale-result consistency.

- Export task completed: shared JSON/HTML builder, explicit revision/job/time/unit provenance, truthful unavailable and draft statuses, detached snapshots, and map capture identity checks. Regression suite now has 28 passing tests; typecheck and build pass. Next bounded task is local backup/restore with disposable-database verification.

- Backup/restore milestone implemented: explicit inspect/backup/verify/restore CLI, read-only consistent incident snapshots, checksums/schema/domain checks, exclusive fresh restore destinations, Git exclusions and recovery guide. Disposable database tests cover round trip, WAL, API retry/continued work, interrupted recovery, corruption and CLI failures. No live database was used. Final verification and backend handoff are the remaining planned closeout.

- Milestone verification: 34 tests passed, including six backup/restore test groups; TypeScript and production build passed. Git exclusions verified for backup files and restored SQLite files. No browser verification or live promotion performed.

- Final closeout: repeated the agreed CLI checks, reviewed repository scope and corrected stale reference-run status. No computer control or live database use. Wider physics and later operational work remain explicitly open in the handoff.
