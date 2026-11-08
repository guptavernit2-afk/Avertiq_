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

Step 1 is complete. Step 2 has an attributed incident fact sheet and reference chemistry notes; exact accident coordinates remain unverified. Step 3 has current tunnel geometry, 72 ERA5 weather hours and a terrain tile collected; a study-area road extract and terrain analysis remain pending. All three SMEDIS batches have been header-screened (30 trials plus one terrain-support workbook), with a detailed three-case propane shortlist and documented data issues. The [phase review](research/EEC550_PHASE_SUMMARY.md) does not accept the proposed gas-only EEC550 baseline; OpenFOAM remains a candidate platform and the nine-case matrix is held pending source/phase reconciliation. No model has been installed or run. See [collection report](research/2026-11-08-summary.md).

## Next milestone

The [source/energy review](research/EEC550_SOURCE_ENERGY_SUMMARY.md) closes conditional component ledgers and defines H00–H04 thermodynamic cases. A 0D PH/HEM model with ThermoPack fluid/ice properties is selected for local feasibility work; its documented two-phase PH call is not a complete moist/ice flash. After user instruction, implement and verify an explicit solid-aware calculation, check properties/references and solve the energy balance. Then review candidate source states before selecting a dispersion configuration or reviving the nine-case matrix. Historical inlet placement/timing and concentration/feed-state interpretations remain open.

Do not promise schedules until data access and modelling dependencies are understood.
