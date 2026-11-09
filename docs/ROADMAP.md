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

Open boundaries and a [conditional EEC550 source/weather setup](research/OPEN_ATMOSPHERE_SUMMARY.md) run on the coupled 2D solver. The package passes 295 tests and 283 independent atmospheric checks. Actual grid/time studies are saved; spatial convergence is explicitly not established. Earlier baselines and public evidence remain preserved. No product app or EEC550 field validation exists.

## Next milestone

Resolve the source vertically and study inlet compatibility/reflection, domain size and runtime scaling. Grid/time smoke studies show conservation but strongly mesh-dependent peak fields. The 2D slab omits crosswind/finite-width dispersion; longer atmospheric runs and appropriate dimensionality are required before receptor scoring.

Do not promise schedules until data access and modelling dependencies are understood.

## Transport milestone completed

The [first 1D transport diagnostic](research/TRANSPORT_PROTOTYPE_SUMMARY.md) is implemented and tested. Next physical milestone: compatible variable-density momentum and buoyancy, then open-domain atmosphere/source checks before receptor comparison.
