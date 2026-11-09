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

The [conservative 1D thermal/phase flow prototype](research/THERMAL_PHASE_SUMMARY.md) is implemented: UV equilibrium EOS, contact-resolving conservative momentum/energy and heat transport. The package passes 210 tests; 210 independent thermal checks and an acoustic refinement benchmark pass.

Next: multidimensional integration of thermal/phase feedback with buoyancy and compatible boundaries, then refinement and atmosphere/source studies. The existing 2D buoyant solver is still frozen-endpoint; EEC550 field comparison remains held. No product app.

Do not promise schedules until data access and modelling dependencies are understood.

## Transport milestone completed

The [first 1D transport diagnostic](research/TRANSPORT_PROTOTYPE_SUMMARY.md) is implemented and tested. Next physical milestone: compatible variable-density momentum and buoyancy, then open-domain atmosphere/source checks before receptor comparison.
