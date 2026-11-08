# Short roadmap

| Order | Work | Evidence of completion |
|---|---|---|
| 1 | Establish repository and scope | Planning baseline committed; no application code |
| 2 | Collect public evidence | Source register updated; incident facts cross-checked; approximate location documented |
| 3 | Prepare geographic and weather context | Corridor map, elevation coverage, historical weather source, time zone and resolution recorded |
| 4 | Define hypothetical scenarios | Three internally consistent input sheets reviewed; unknowns and synthetic data identified |
| 5 | Establish calculation and comparison method | Applicable research model and experimental inputs reviewed; PHAST benchmark separately agreed if available |
| 6 | Implement after user instruction | Small, reviewable milestones: incident form, map/context, assessment workflow, observations, handover |
| 7 | Evaluate | Reproducible results, discrepancy report, and tabletop feedback |

## Current status

Step 1 is complete. Step 2 has an attributed incident fact sheet and reference chemistry notes; exact accident coordinates remain unverified. Step 3 has current tunnel geometry, 72 ERA5 weather hours and a terrain tile collected; a study-area road extract and terrain analysis remain pending. All three SMEDIS batches have been header-screened (30 trials plus one terrain-support workbook), with a detailed three-case propane shortlist and documented data issues. The [phase review](research/EEC550_PHASE_SUMMARY.md) does not accept the proposed gas-only EEC550 baseline; OpenFOAM remains a candidate platform and the nine-case matrix is held pending source/phase reconciliation. ThermoPack 2.2.3 is now installed locally and the standalone reduced equilibrium calculation has been run and numerically verified; no dispersion model has been installed or run. See [collection report](research/2026-11-08-summary.md).

## Next milestone

Today's [scope, mixing and handoff checkpoints](PROJECT_CHECKPOINTS.md) are complete within the standalone research scope: 11 mixing states, 16 handoff checks and 51 passing tests. See the [short report](research/TODAY_SHORT_REPORT.md).

Next session: make a bounded phase-bearing dispersion implementation feasibility decision using the [executed mixing path](research/EEC550_MIXING_MILESTONE.md) as a regression case. Select one implementable route or explicitly reject it. The nine-case comparison remains held. App and CFD implementation/runs remain outside current authorization.

Do not promise schedules until data access and modelling dependencies are understood.
