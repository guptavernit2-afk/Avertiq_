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

Pending implementation and verification. No physics result is supplied by this plan.
