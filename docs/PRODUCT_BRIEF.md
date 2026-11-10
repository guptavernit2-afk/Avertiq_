# Avertiq product brief

Scope clarification, 10 November 2026: this is the first D-001 walkthrough. The confirmed wider research target includes LPG, CNG and reported propylene, transport/storage and light/heavy release behaviour. Use the [research handoff](research/RESEARCH_HANDOFF_2026-11-10.md) and [assessment interface](ASSESSMENT_CONTRACT.md) to preserve separate gas, fire-radiation and blast layers and their readiness limits. No new product code was written in this research review.

## Product goal

Help a chemical-tanker incident coordinator and hazmat specialist assemble incomplete information, compare release scenarios, inspect potential affected areas on a map and prepare a traceable handover.

The first demo centres on one stationary propylene tanker in an Adoshi-inspired scenario. Release inputs will be explicitly hypothetical until real industrial data becomes available.

## First demo scenario

**Demo D-001 — stationary propylene tanker near the Adoshi road corridor.**

The coordinator receives a report of an ongoing leak and prepares a handover for the next responder. Use public road geography with an approximate **demo pin**. Confirm the pin against the collected geographic record during implementation and label its location accuracy.

The following are proposed fictional walkthrough inputs, chosen for the product demo.

| Item | Demo value | Evidence label |
|---|---|---|
| Cargo | Propylene | Assumed for demo |
| Incident | Stationary tanker, ongoing unignited leak | Simulated incident report |
| Time | T+00, relative demo clock | Simulated time |
| Wind | 2 m/s, from west | Simulated weather |
| Air temperature | 25 °C | Simulated weather |
| Release | Direct assumed rate 0.1 kg/s over a 10-minute scenario | Assumed release input |
| Inventory, tank pressure, opening and release phase | Unknown | Missing information |
| Assessment A | Prepared illustrative map area | Simulated assessment fixture |
| Update at T+05 | Wind report changes to southwest, same speed | Simulated update |
| Assessment B | Second prepared illustrative map area | Simulated assessment fixture |

The direct release rate is a scenario assumption. Unknown tank and phase inputs remain visible. The initial walkthrough uses prepared illustration data; physics-based assessment readiness will be checked against the eventual calculation method.

## Screen sketches

The walkthrough has five screens. A persistent banner reads **Training demo — simulated incident and assessment**. Each screen shows the active revision and relative demo time.

### 1. Incident overview

| Main panel | Map panel |
|---|---|
| D-001, cargo, incident report, T+00 | Public roads and approximate demo pin |
| Missing-information list and evidence labels | Location accuracy note |
| Action — Review inputs | |

The coordinator sees what has been reported and what still needs confirmation.

### 2. Scenario inputs

| Release inputs | Weather inputs |
|---|---|
| Assumed direct rate and duration | Simulated wind arrow, speed and temperature |
| Unknown tanker/phase fields | Evidence label beside every value |
| Action — Load simulated assessment A | |

A short note explains that this action loads a prepared illustration. Editing arbitrary inputs marks the fixture as outdated until the operator selects a documented demo preset again.

### 3. Assessment map

| Left panel | Main map |
|---|---|
| Revision A and input summary | Roads, demo pin and wind arrow |
| Legend — Simulated illustrative area A | Hatched illustrative area |
| Layer controls and missing inputs | Observation markers |
| Actions — Add observation / Record update | |

Keep the simulation label attached to the area and legend. Illustrative areas have no calculated hazard distance, concentration threshold or safety-zone designation. Terrain can provide geographic context when available.

### 4. Observation and revision

| Update form | Revision comparison |
|---|---|
| T+05, simulated southwest wind report | A — original demo inputs |
| Simulated note — Driver reports leak ongoing | B — updated wind preset |
| Action — Load simulated assessment B | Prepared area B and a list of changed inputs |

Save A before creating B. The observation is a simulated report; its text does not validate the assessment. Revision B is another prepared fixture with its own input snapshot and label.

### 5. Handover preview

| Report body | Actions |
|---|---|
| Incident, location accuracy, current revision and timeline | Review / Export |
| Inputs, evidence labels, map and observations | |
| Missing information and next information requests | |

Every exported page carries **Training demo — simulated assessment**. The map retains its own simulation legend when exported separately. Earlier revisions remain accessible.

## What the first walkthrough demonstrates

One coordinator can create the incident record, inspect assumptions, view a labelled illustrative assessment, add a simulated observation, load the revised preset and export a traceable handover.

The product workflow and calculation validation can progress alongside each other. Connecting physics-generated assessments requires a suitable method and documented comparison evidence.

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

### Product walkthrough

1. Complete D-001 through all five screens without losing an input, observation or revision.
2. Show the simulation banner on every screen and keep it attached to map areas and exports.
3. Keep measured, reported, assumed, simulated and missing information identifiable.
4. Preserve revision A after the wind update and make the difference from B easy to inspect.
5. Mark fixtures outdated after unsupported input edits.
6. Export a readable handover with the current input snapshot, location accuracy and missing information.

### Calculation validation

Establish numerical reliability, experimental comparison, supported inputs and uncertainty before connecting a physics-generated hazard assessment. Track this alongside product development.

## Next work package

Review these five screen sketches and the proposed demo values together. After implementation is authorized, build the single D-001 workflow with prepared fixtures and evidence labels. Continue calculation validation as a parallel project workstream.

This update covers product planning. Application implementation remains pending.
