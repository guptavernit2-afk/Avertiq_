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

The [integrated 2D thermal/phase/buoyancy prototype](research/THERMAL_2D_SUMMARY.md) is implemented and tested. The research package has 232 passing tests and 552 independent integration checks. Original thermodynamic, 1D and frozen-density baselines remain available. Public incident/geography/weather evidence and SMEDIS case records are preserved; no EEC550 field comparison or product application exists.

## Next milestone

Define and verify open-domain boundaries, atmosphere and source configuration, with mesh/time/domain and runtime/scaling studies. The current 4x4, 0.0003-second closed-box case verifies integration, not a 150-second field release. Review transport/phase assumptions and lock the EEC550 comparison recipe before sensor evaluation.

Do not promise schedules until data access and modelling dependencies are understood.

## Transport milestone completed

The [first 1D transport diagnostic](research/TRANSPORT_PROTOTYPE_SUMMARY.md) is implemented and tested. Next physical milestone: compatible variable-density momentum and buoyancy, then open-domain atmosphere/source checks before receptor comparison.
