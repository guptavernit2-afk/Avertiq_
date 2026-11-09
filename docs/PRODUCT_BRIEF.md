# Avertiq product brief

## Product goal

Help a chemical-tanker incident coordinator and hazmat specialist assemble incomplete information, compare release scenarios, inspect potential affected areas on a map and prepare a traceable handover.

The first demo centres on one stationary propylene tanker in an Adoshi-inspired scenario. Release inputs will be explicitly hypothetical until real industrial data becomes available.

## First-demo user flow

1. Enter the incident location, cargo and time.
2. Enter weather and tanker/release information with sources and assumptions.
3. Run a supported assessment and review its uncertainty.
4. Inspect the assessment alongside roads, terrain context and observations.
5. Revise the scenario as information changes.
6. Export an incident handover with inputs, results and revision history.

## What exists today

| Area | Status |
|---|---|
| Product scope and public research | Documented incident evidence, chemistry, geography/weather sources and experimental cases |
| Source thermodynamics | Working local calculation of temperature, gas/liquid/ice partition and mass/energy budgets |
| Flow research | Working small 1D and 2D prototypes covering transport, heat, phase feedback, gravity and conservation |
| Open boundaries | Wind inflow, release inlet, outflow and backflow implemented |
| Numerical verification | 295 package tests and 283 atmospheric checks passed; grid/time studies saved |
| Version history | Research, code, results and CI checks committed to GitHub |
| User-facing application | Pending |
| Experimentally demonstrated prediction accuracy | Pending |

**Current position:** we have built the calculation research foundation. The usable incident-to-map application still needs implementation. The saved flow experiments currently cover the first millisecond of release startup.

## What remains

### Calculation readiness

- Resolve spatial accuracy, boundary behaviour and computational cost over much longer runs.
- Establish suitable atmosphere/turbulence and transport assumptions.
- Account for finite-width and crosswind dispersion, which the current 2D slice omits.
- Compare with EEC550 experimental concentrations using matched receptor positions, units and averaging times.
- Review the results with the industry mentor and benchmark against PHAST if access becomes available.
- Establish the propylene tanker source/assessment workflow for the Adoshi-inspired demo. EEC550 is a propane analogue.

### Product implementation

- Incident and scenario forms with evidence/assumption labels.
- Map with roads, terrain context and supported assessment layers.
- Observation entry, assessment revisions and handover export.
- A complete walkthrough tested with a prospective user.

## First-demo boundaries

Live SCADA/telematics, moving tanker releases, refinery digital twins, fire/explosion models, terrain-dependent flow and automated response decisions are deferred. The initial geographic terrain layer provides context. Historical Adoshi plume reconstruction remains unsupported by available data.

## Acceptance checkpoints

1. Calculation results have demonstrated numerical reliability and a documented experimental comparison.
2. A reviewer can reproduce an assessment and identify every measured, assumed and simulated input.
3. A user can complete the incident-to-map-to-handover flow.
4. Mentor/user feedback and known limitations are recorded before any operational product claim.

## Work status

Implementation is paused at the user's request. Review this brief together before choosing the next work package. Future sessions should name their deliverable and show a short before/after result when they close.
