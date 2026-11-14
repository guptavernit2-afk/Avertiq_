# Daily backend plan: 14–20 November 2026

User authorized independent CLI-only backend work and daily scoped commits/pushes during exams. No computer control, browser automation, visible windows or ALOHA runs. Local scheduled runs depend on the Codex app/machine being available; missed execution is not completed work.

## Bounded order

Complete at most one substantive item per daily run, inspecting existing implementation first. Skip already satisfied requirements; do not add features just to consume credits.

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
