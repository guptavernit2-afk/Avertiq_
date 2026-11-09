# Avertiq

Chemical transport incident assessment.

**Current stage:** integrated 2D conservative thermal/phase/buoyancy research prototype, with earlier verified baselines retained. No product application or EEC550 field validation.

Avertiq starts with an **Adoshi-inspired training demo**: one stationary propylene tanker, real geographic context, and explicitly hypothetical release conditions. It does not reconstruct the historical gas cloud or provide operational clearance decisions.

## Read first

- [One-page roadmap](docs/ROADMAP.md)
- [Demo scope](docs/DEMO_SCOPE.md)
- [Data collection plan](docs/DATA_PLAN.md)
- [Scenario definitions](docs/SCENARIOS.md)
- [Mathematics and validation](docs/VALIDATION.md)
- [Decision history](docs/DECISIONS.md)
- [Source register](data/source-register.csv)

## Research collected

Start with the [short collection report](docs/research/2026-11-08-summary.md). Public weather data is tracked; larger raw terrain/map/experimental assets remain local with source URLs and checksums. Conditional thermodynamic results are available below; no field-dispersion comparison results exist.

## Validation cases selected

Read the [short SMEDIS review](docs/research/SMEDIS_SHORTLIST.md): EEC550 first, EEC360 after duplicate-record review, and EEC560 reserved from future tuning. These are propane analogues, not validation of Adoshi. No EEC550 field comparison has been run.

## Standalone equilibrium calculation

Read the [short implementation report](docs/research/EEC550_EQUILIBRIUM_SUMMARY.md). The [research package](research/equilibrium/README.md) runs locally with ThermoPack 2.2.3 and an explicit reference-saturation water/ice closure. It passed 38 tests and 34 property/numerical checkpoints. Results are conditional source studies, not experimental validation.

The primary assumed case gives about 204.3 K with water ice. The original gas-only baseline remains unaccepted and the nine-case CFD study remains held pending review. Run instructions, dependency pins, source/native-library hashes and results are recorded in the repo. No app or CFD work was performed.

## Demo flow

Open incident -> confirm cargo and location -> select documented release assumptions -> review a hazard estimate -> inspect roads and terrain -> add simulated observations -> revise assessment -> export handover.

Every important value must include its unit, source, timestamp, and evidence status: measured, reported, assumed, or unavailable. Simulated data must also carry a synthetic-data flag.

## Project records

Keep each reviewed decision and completed milestone in Git. Record what changed, why, supporting evidence, validation performed, and unresolved questions. Small, meaningful commits are preferred.

The previous [SurakshaMitra prototype](https://github.com/guptavernit2-afk/SurakshaMitra) remains a separate project. Its existing equations are not accepted as validated models for this demo.

Initial planning baseline: 8 November 2026.

## Source-to-dispersion plan

The [short handoff decision](docs/research/EEC550_DISPERSION_SUMMARY.md) selects H00 as a conditional phase-bearing candidate and preserves the original equivalent source separately. Warm-air mixing checks and an implementation audit come next; the nine-case study remains held. No CFD solver has been selected or run.

## Current checkpoints

[Scope and checkpoint board](docs/PROJECT_CHECKPOINTS.md) | [Today's short report](docs/research/TODAY_SHORT_REPORT.md)

Completed the standalone mixing milestone: 11 conditional states, 16 source handoff checks and 51 passing research tests. Mixing retains changing water phases; no spatial dispersion or app exists yet. Next is one bounded dispersion implementation feasibility decision.

## Working research workbench

[Open the offline results report](data/public/eec550-research-bundle-v1/report.html) | [Latest short report](docs/research/TODAY_SHORT_REPORT.md)

The reusable study/bundle commands now run 132 conditional states, export four checked source contracts and produce an offline report with provenance and checksums. The complete research suite passes 136 tests. See [workbench v1](docs/research/WORKBENCH_V1.md) for commands and limits. No dispersion solver or product application exists yet.

## First transport prototype

A self-run 1D conservative advection-diffusion diagnostic with equilibrium phase postprocessing is implemented. The full suite has 154 passing tests. [Short report and run command](docs/research/TRANSPORT_PROTOTYPE_SUMMARY.md). Prescribed flow and periodic boundaries do not model a buoyant atmospheric cloud; no app or field-prediction claim.

## Variable-density buoyant flow

A 2D frozen-endpoint variable-density incompressible prototype now computes density-dependent motion, gravity and pressure correction. The package passes 173 tests and 22 independent flow checks. [Short report and commands](docs/research/VARIABLE_DENSITY_SUMMARY.md). This is a synthetic hydrodynamic milestone; evolving thermal/phase coupling and EEC550 field validation remain outstanding.

## Conservative thermal and phase coupling

A separate 1D conservative Euler/HLLC/Fourier prototype now couples component mass, momentum, total energy and equilibrium pressure/temperature/phase feedback. It passes 210 package tests and 210 independent thermal checks; an acoustic refinement benchmark also passes. [Short report](docs/research/THERMAL_PHASE_SUMMARY.md). Integration into 2D buoyancy and EEC550 field validation remain outstanding.

## Integrated 2D thermal buoyancy

Heat/phase feedback, conservative momentum/energy and gravity now run together in a 2D compressible research prototype. The package passes 232 tests and 552 independent integration checks. [Short report and commands](docs/research/THERMAL_2D_SUMMARY.md). These are tiny closed-box verification runs; open-domain atmosphere/source configuration, convergence and field validation remain outstanding.
