# Local sensitivity review handoff plan

Planned 15 November 2026 before implementation. This is the readable reporting preparation for gate 6 of [first physics qualification](FIRST_PHYSICS_QUALIFICATION.md), building on the checked [sensitivity report](PROPYLENE_SENSITIVITY_REPORT.md). Actual propylene runs remain pending.

## Scope and acceptance criteria

1. Add a standalone CLI under research/dispersion that reads the four registered observations through the existing comparison/inspection path. Recheck all raw evidence; never render a supplied comparison JSON as trusted evidence.
2. Generate a self-contained local HTML review handoff with explicit pending-qualification labels, case/input/engine/evidence identity, changed inputs, receptor and diagnostic contour comparisons, withheld-value reasons, reporting bounds, model warnings and unresolved mapping gates.
3. Include a canonical checked-comparison hash and handoff-tool hash for traceability. Escape all transcribed text, include no scripts or external assets, and do not embed raw evidence or provide clickable local evidence paths. Keep exports local under ignored outputs until content/redistribution review.
4. Preserve existing run requirements and false propylene/field/dashboard flags. Refuse existing output paths. Validate and serialize before creating the destination; invalid or unrun inputs must create no handoff. Do not modify input records.
5. Test complete and blocked comparisons, missing/bounded/zero values, warnings, hostile HTML text, provenance, source preservation, overwrite refusal and invalid/unrun/evidence-tamper failures using disposable synthetic records only. Run the full qualification suite and four-platform/version CI checks.

## Delivery

Plan commit first on codex/propylene-review-handoff, then implementation/tests, PR, diff/CI review and merge. Use CLI only: no browser/computer control, ALOHA execution, actual physics output, dashboard adapter or deployment. HTML content/structure will be checked programmatically; visual browser acceptance is outside this task.

## Completion

Pending implementation. No actual handoff or model result exists.
