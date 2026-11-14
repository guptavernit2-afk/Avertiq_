# Sensitivity-comparison report plan

Planned 15 November 2026, before implementation. This task prepares the review/reporting portion of gates 5 and 6 in [first physics qualification](FIRST_PHYSICS_QUALIFICATION.md): inspect baseline/sensitivity consistency and retain traceable permitted quantities. Actual ALOHA runs remain pending.

## Deliverable and acceptance criteria

Extend the existing `compare-runs` CLI, without adding a solver or dashboard adapter:

1. Identify the changed frozen model input for each of the three variants, with units and baseline/variant values. Preserve case IDs/hashes in the checked run records.
2. Compare contour downwind distances by diagnostic ppm threshold, alongside the existing receptor comparisons. Retain existing receptor value/difference/ratio fields for compatibility.
3. Report specific method/basis/structured-semantics blockers. No numerical comparison for incompatible records. For compatible records, carry each side's unavailable reason and any transcribed reporting bound; null scalars remain null and never become zero. Zero-baseline ratios and unrepresentable arithmetic remain null with reasons.
4. Keep actual run inspection/evidence requirements, warnings and false propylene/field/dashboard qualification flags. Do not infer monotonic trends, health limits, polygons or operational safety.
5. Add disposable synthetic regression tests for changed inputs, contour matching independent of row order, mismatched methods/bases, missing/bounded outputs, zero denominators and extreme arithmetic. Verify the existing CLI workflow and the full qualification suite.

## Delivery workflow

Work on `codex/propylene-sensitivity-report`. Record this plan first, then implement and test. Push the branch and open a PR against `main`; review its diff and four Windows/Linux CI jobs before merging. Verify the merged commit and synchronize local `main`. No direct-to-main implementation push, computer control, deployment or ALOHA execution.

## Completion record

Implemented on the planned feature branch. All 74 qualification-tool tests pass locally, including eight new sensitivity-report tests. The CLI retains existing receptor comparison fields and adds changed-input details, explicit blockers, contour changes and per-side unavailability/bound metadata. Tests verify reordered rows, falling values, missing outputs, zero denominators, ratio overflow/underflow, unchanged source files, overwrite refusal and unrun-record rejection. No physics result is supplied by these tests.

Completed through [PR #1](https://github.com/guptavernit2-afk/Avertiq_/pull/1), merged as b4596d0 after diff review and successful Windows/Linux CI. Actual baseline/sensitivity model runs remain pending.

## Report contract

`changed_inputs` lists each changed frozen model input with its unit and baseline/variant values. Current registered variants change only `rate_kg_s` or `wind_m_s`. Inputs are still verified against frozen cases before comparison.

`comparison_blockers` identifies method mismatch, basis mismatch, missing baseline/variant structured semantics, or incompatible structured signatures. When blocked, both `receptor_changes` and `contour_changes` are empty. This remains a same-engine diagnostic comparison only.

For comparable runs, receptor rows keep `downwind_m`, `baseline_ppm`, `variant_ppm`, `difference_ppm` and `ratio`. New contour rows use `level_ppm`, `baseline_m`, `variant_m`, `difference_m` and `ratio`; rows are matched by identifiers, not their input order. Differences are variant minus baseline, ratios are variant divided by baseline. A decreasing value is reported without declaring a pass/fail physical trend.

Each row also carries each side's unavailable reason and, if supplied through checked transcription, its bound relation/value/unit. Bounded scalars remain null; no interval arithmetic is inferred. Difference/ratio unavailability distinguishes a missing side from a zero denominator or arithmetic outside floating-point range. Finite displayed numbers still have their original precision limits.

Warnings, case/engine/evidence identity and open gates remain in the full checked run records. No map polygons, source release predictions, time animation, health limits or dashboard adapter are created. Existing archives already hash the changed checking module and retain their provenance-drift rules.
