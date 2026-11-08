# Completed research milestone: H00 mixing and source handoff

8 November 2026. Scope: standalone thermodynamic research only. No app, CFD, terrain calculation or hazard footprint.

## What closed today

1. [Project scope and checkpoints](../PROJECT_CHECKPOINTS.md) frozen for this milestone.
2. Implemented and executed an 11-point conservative H00/ambient equilibrium mixing path.
3. Completed 16 source handoff arithmetic checks and independent read-only review.
4. Recorded results, meaningful tests, limits and the next stage in Git.

The full equilibrium research suite now passes **51 tests** (38 existing plus 13 new). The mixing CLI passed its property/numerical verification gate before executing. [Mixing results](../../data/public/eec550-mixing-results.json) and [handoff checks](../../data/public/eec550-handoff-checks.json) are first-party records. Earlier H00-H04 run records are unchanged; their provenance describes that earlier code snapshot.

## Experiment performed

This is a conditional **zero-dimensional isobaric thermal-enthalpy mixing diagnostic**, not a dispersion experiment. Start with the same calculated H00 source; add ambient wet air at 283.05 K, RH 99%, 102500 Pa. Ratio means added wet-air mass divided by original total H00 mass, not propane mass. Every point is an independent PH equilibrium solve; no spatial/time evolution is solved.

Propane stays 3 kg/s. Added air carries additional water vapour. Conserve total component flow and thermal enthalpy at every ratio. Kinetic-energy conversion, momentum, work, mixing rates, particle slip, nucleation, deposition and finite phase rates are excluded. No velocity or source area is assigned to mixed states.

| Added wet-air / H00 mass | Temperature K | Ice kg/s | Liquid water kg/s | Gas propane mol% |
|---:|---:|---:|---:|---:|
| 0 | 204.261 | 0.057692 | 0.000000 | 20.1901 |
| 0.1 | 212.690 | 0.065621 | 0.000000 | 18.1838 |
| 0.25 | 222.856 | 0.077368 | 0.000000 | 15.8247 |
| 0.5 | 235.304 | 0.096096 | 0.000000 | 13.0101 |
| 1 | 250.459 | 0.127575 | 0.000000 | 9.5919 |
| 2 | 263.913 | 0.164325 | 0.000000 | 6.2795 |
| 5 | 273.948 | 0.000000 | 0.205102 | 3.0788 |
| 10 | 278.327 | 0.000000 | 0.220573 | 1.6635 |
| 20 | 280.614 | 0.000000 | 0.226112 | 0.8665 |
| 50 | 282.016 | 0.000000 | 0.220330 | 0.3555 |
| 100 | 282.488 | 0.000000 | 0.202889 | 0.1793 |

## Findings and limits

Humid air initially adds condensable water faster than warming removes ice: ice mass flow rises between sampled ratios 0 and 2. At ratio 5 the equilibrium state is above the model melting temperature and has liquid water instead. Ice disappearance lies somewhere between sampled ratios 2 and 5; this grid does not locate an exact threshold or resolve the melting plateau.

At ratio 100 the state is about 282.49 K and still has approximately 0.2029 kg/s liquid water. **Ice disappearing does not mean all condensate disappeared.** Propane remains gas in all sampled states, but no claim is made for unsampled states or other source interpretations.

Maximum absolute energy residual across sampled points is below 0.000001 J/kg; component residuals meet the numerical gate. This checks the defined reduced model's accounting. It does not independently validate its properties, equilibrium time scales or experimental applicability. Mixing ratio does not imply any distance, time, probability or real dilution rate.

The 16 handoff checks cover individual components and phase mass, composition sums, area/flow/density, velocity, kinetic energy, advective momentum and source energy. The independent review found no material arithmetic inconsistency. Neither exercise verifies a transport implementation.

## Reproduce

From the Avertiq repository root, using the existing environment:

~~~powershell
.\.venv\Scripts\python.exe -m pytest research/equilibrium -q
.\.venv\Scripts\python.exe -m avertiq_equilibrium mixing --output outputs/thermodynamics/my-new-mixing-run/mixing.json
~~~

Choose a new output path; existing results are protected against overwrite. The executed local path was outputs/thermodynamics/2026-11-08-mixing-v1/mixing.json. Tracked output records runtime, native-library and current module hashes. No dependencies were added.

## The next checkpoint

Research setup is closed for this milestone. Next is a bounded **dispersion implementation feasibility decision**, not another general literature sweep: can a practical local method transport conserved propane/water/air and energy with the required changing gas/liquid/ice phases, buoyancy and consistent property references?

Use today's path as a regression case for that decision. Evaluate HEM applicability and implementation effort; explicitly accept a conditional research approximation or reject it with reasons. Select one route before installations or a CFD prototype. The nine-case comparison stays held and no production-readiness claim follows. The eventual flat-ground propane comparison is separate from transferring to the propylene Adoshi-inspired demo.
