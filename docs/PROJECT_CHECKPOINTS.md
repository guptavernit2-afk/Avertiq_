# Avertiq: scope and checkpoints

## Current checkpoint: 10 November 2026

Confirmed target: **LPG, CNG and reported propylene**, transport/storage, light/heavy release behaviour, and applicable dispersion, fire-radiation and blast assessments. Terrain-dependent calculations are a separate model milestone, not provided by 3D rendering.

| Checkpoint | Current status | Exit / next evidence |
|---|---|---|
| Evidence and first product design | Bounded review complete | [Handoff](research/RESEARCH_HANDOFF_2026-11-10.md), 33 additional source records with access limits and defined first-build acceptance |
| Propane source and flow research | Implemented and numerically checked within reduced scope | Existing 295-test milestone and 283 saved atmospheric checks; not a reviewed propylene/CNG/LPG-mixture engine |
| Developed flat-ground plume | Incomplete | Source/grid/domain/runtime, atmospheric transport and finite-width/crosswind resolution |
| EEC550 field comparison | Not executed | Matched all-receptor concentration comparison after numerical/model gates |
| CNG / LPG model route | Candidate identified | [HyRAM+ audit](research/CHEMICAL_AND_STORAGE_SCOPE.md#engine-candidate-hyram); full version-specific validity review and reproduced runs remain |
| Fire / blast / terrain | Requirements reviewed; no Avertiq assessment implementation | Scenario-specific methods, applicable benchmarks and limitations |
| First website | Ready for bounded implementation as next work package | D-001 incident-to-map-to-revision-to-handover using labelled fixtures; no app code in this review |

No further general literature collection blocks the first fixture-based website. Real source sheets, mentor model/version decisions and validation remain necessary for calculated layers. Details: [chemical scope](research/CHEMICAL_AND_STORAGE_SCOPE.md), [physics](research/PHYSICS_REQUIREMENTS.md), [terrain](research/TERRAIN_AND_VALIDATION.md), [assessment interface](ASSESSMENT_CONTRACT.md).

## Historical checkpoint records

8 November 2026. This is the working finish line, not a promise of production readiness.

## What we are building

An **Adoshi-inspired tanker incident training demo**: record cargo, location and weather; choose explicitly hypothetical release conditions; review a traceable assessment on a map; add observations; preserve revisions and export a handover.

Version 1 covers one stationary propylene tanker and unignited-release scenarios. Roads and terrain provide context. Terrain-dependent flow, a refinery digital twin, live tanker telemetry, fire/explosion models and automatic response decisions are later work. Exact Adoshi plume reconstruction and operational safety validation are outside this demo.

## Where we are

Public evidence and experimental cases are collected. The standalone source thermodynamics works: the recorded run passed **38 tests and 34 property/numerical checks**. Its conditional H00 source is about 204.3 K with propane gas and water ice. This is an assumed source, not a recovered field measurement.

**We have no dispersion result or app yet.** Recent work established a defensible source because an unchecked gas-only inlet would discard phase-change physics. That research stage now has a clear exit; it must not become endless setup.

## Checkpoints

| Checkpoint | Status | Concrete exit evidence |
|---|---|---|
| 1. Evidence and source calculation | Complete within stated reduced-model scope | Attributed inputs, H00-H04 records, passed numerical/property checks and explicit historical gaps |
| 2. Source behaviour during mixing | Complete: 11-point diagnostic | Reproducible standalone warm-air mixing study; component/energy residuals; ice/phase behaviour; meaningful tests and limitations |
| 3. Dispersion handoff review | Complete: 16 arithmetic checks and independent review | Source mass, enthalpy, velocity and area agree; original 196 K record preserved; changed assumptions identified |
| 4. Freeze this research milestone | Complete: records and checks saved | Reviewed scope, short results note, reproducible commands and scoped Git record; next blocking question named |
| 5. Dispersion feasibility | Proposed next session | Select an implementable phase-bearing approach or document why it cannot support this source; define numerical checks and comparison recipe |
| 6. First experimental comparison | Pending checkpoint 5 | Numerically checked flat-ground model compared with all 30 EEC550 sensors using declared averaging/basis; discrepancies reported, no fit-selected baseline |
| 7. Demo application | Pending suitable calculation workflow | One complete scenario-to-map-to-handover flow; evidence labels, synthetic-data labels and assessment history |

EEC550 is a **propane validation analogue**, not Adoshi or terrain validation. Experimental agreement remains an open question, not an assumed checkpoint result.

## How daily work proceeds

Run independent work together: calculations, evidence review and documentation. Keep dependent steps sequential: inspect results before accepting a model. Each session should close with an artifact, a check and a Git record, plus a short next-step note.

Tomorrow's proposed starting point is checkpoint 5, informed by today's mixing results. App/CFD implementation or runs require a separate scope instruction; none are authorized or promised by this checklist. The nine-case CFD study remains held.

[Demo scope](DEMO_SCOPE.md) | [Source handoff](research/EEC550_DISPERSION_HANDOFF.md) | [Roadmap](ROADMAP.md)

[Today: short report](research/TODAY_SHORT_REPORT.md) | [Executed mixing milestone](research/EEC550_MIXING_MILESTONE.md)

## Larger implementation batch: completed 9 November

- Reusable study API and CLI: 132 states, 12 paths.
- Strict source-export API: four PH sources, 39 checks each.
- Offline report and checksum bundle: generated and saved.
- Full local suite: 136 passed; report-filter smoke test passed.
- CI workflow added; remote execution status is separate from local checks.

[Workbench v1 milestone](research/WORKBENCH_V1.md) | [Open offline report](../data/public/eec550-research-bundle-v1/report.html)

## Variable-density flow: completed 9 November

- Density-dependent 2D motion and pressure projection implemented.
- Buoyancy, hydrostatic/zero-gravity controls and mass budgets checked.
- Full suite: 173 tests passed; independent flow checks: 22 passed.
- Endpoint case and 12/24/48-cell grid comparison saved.
- Next: compatible thermal/phase EOS and conservative momentum/energy coupling before atmospheric comparison.

[Short report](research/VARIABLE_DENSITY_SUMMARY.md)

## Conservative heat and phase feedback: completed 9 November

- UV EOS, sound speed and thermal capacity implemented.
- Conservative 1D species/momentum/internal-plus-kinetic energy coupled to heat and phase equilibrium.
- HLLC resolves stationary contacts; zero-heat control passes.
- 210 package tests, 210 independent checks and an acoustic refinement benchmark pass.
- Next: integrate thermal and buoyancy physics multidimensionally before an atmospheric release comparison.

[Short report](research/THERMAL_PHASE_SUMMARY.md)

## 2D thermal/phase/buoyancy integration: completed 9 November

- Conservative 2D species, momentum and energy with gravity and UV feedback implemented.
- Hydrostatic rest, potential-energy accounting and wall-force budgets checked.
- 232 package tests and 552 independent checks passed.
- Nonzero-velocity reduction to the verified 1D thermal solver matches.
- Next: open boundaries, atmosphere/source configuration, convergence and computational scaling before EEC550 comparison.

[Short report](research/THERMAL_2D_SUMMARY.md)

## Open atmosphere/source/weather: completed 9 November

- Open inflow, source patch, outlets and backflow implemented and checked.
- Conditional H00 and selected EEC550 weather traced to prior records.
- 295 package tests and 283 independent checks passed.
- 4/8/12-grid and three-level time-step studies executed and saved.
- **Outcome:** spatial source/field convergence not established. Next: source-resolving mesh, boundary/domain and runtime studies.

[Short report](research/OPEN_ATMOSPHERE_SUMMARY.md)
