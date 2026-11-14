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

Implemented on the planned branch. All 82 qualification-tool tests pass locally, including eight new handoff tests. Synthetic tests cover traceability, case/output units and labels, preserved warnings and gates, withheld comparisons, bounds/zero values, escaped markup, source preservation, refused overwrites and rejection of unrun/malformed/missing/tampered inputs. No actual handoff or model result was created. HTML content and structure were checked through Python's HTML parser; no visual browser acceptance is claimed.

Completed through [PR #2](https://github.com/guptavernit2-afk/Avertiq_/pull/2), merged as 70c1e35 after diff review and successful Windows/Linux CI. Actual propylene results remain pending.


## Future local workflow

Only after actual observations and raw evidence exist for all four cases:

```powershell
python research/dispersion/review_handoff.py --runs-dir outputs/propylene --output outputs/propylene/review-handoff.html
```

The command accepts the original run directory, not a prebuilt comparison JSON. It reuses `compare_runs` and every underlying case/engine/evidence/semantics/transcription check. Missing and unrun records cannot generate a handoff. Method or basis mismatches produce a handoff with explicit withheld-comparison reasons and each run's separately labelled recorded values; incompatible outputs are never numerically compared.

The self-contained HTML contains no scripts, external assets or clickable evidence paths. It includes evidence filenames/hashes, not raw files. Operator notes, warnings and other recorded free text are escaped but retained, so keep the report local until content and redistribution review; escaping is not a privacy or licensing review. The current output is for scientific review, not public communication or emergency guidance.

Traceability includes the canonical checked-comparison SHA-256 (reproducible using the existing comparison command and canonical JSON hashing), case/engine/evidence hashes, recorded run times and the LF-normalized handoff-tool hash. Hashes do not establish authenticity or applicability. The export has no new run timestamp because creating a report is not executing a model.

Use a fresh `.html` path. Validation and rendering finish before destination creation, and exclusive creation rejects an existing/racing file. A storage interruption can leave a partial HTML file: do not treat that as a complete handoff; preserve it for diagnosis and retry to a fresh path. No raw evidence, observations, frozen cases or public reference records are rewritten.
