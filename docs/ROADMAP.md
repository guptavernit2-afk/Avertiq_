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

Step 1 is complete. Step 2 has an attributed incident fact sheet and reference chemistry notes; exact accident coordinates remain unverified. Step 3 has current tunnel geometry, 72 ERA5 weather hours and a terrain tile collected; a study-area road extract and terrain analysis remain pending. All three SMEDIS batches have been header-screened (30 trials plus one terrain-support workbook), with a detailed three-case propane shortlist and documented data issues. OpenFOAM Foundation 14 is selected conditionally for the first EEC550 research comparison; input mapping and numerical/measurement gates remain open. No model has been installed or run. See [collection report](research/2026-11-08-summary.md).

## Next research task

Use the [EEC550 findings](research/EEC550_SHORT_PLAN.md): axes and conditional comparison/weather policies are defined; actual inlet elevation and exact measurement timing remain unverified. Recover original records or explicitly agree an exploratory sensitivity study; review thermal/turbulence assumptions and predeclare criteria before any evaluated run. Resolve EEC360 duplicate-record handling; reserve EEC560 from future tuning. Verify incident location/study-area bounds and request the mentor's PHAST version/modules and acceptance criteria.

Do not promise schedules until data access and modelling dependencies are understood.
