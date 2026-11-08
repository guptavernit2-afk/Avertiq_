# EEC550: equilibrium review and dispersion handoff

8 November 2026. **Planning only. No new equilibrium run, app work, CFD implementation or CFD run.**

## Decision

Use **H00 as the primary conditional source candidate** for a future phase-bearing dispersion study. Preserve the original reported equivalent source separately. This assesses predictions under declared assumptions; it cannot yet reproduce the historical EEC550 experiment faithfully.

Prefer a **homogeneous-equilibrium mixture (HEM) research formulation**: one velocity and temperature, conserved total component mass and enthalpy, and local gas/liquid/ice partition. This matches the existing zero-dimensional approximation. It is a hypothesis to assess, not a selected ready-to-run CFD solver. Keep the nine-case study held.

Read the [equilibrium verification](EEC550_EQUILIBRIUM_VERIFICATION.md) and [structured handoff](../../data/public/eec550-dispersion-handoff.json). The handoff is a review record, not executable solver input.

## What the results establish

| Case | Temperature K | Propane liquid kg/s | Water ice kg/s | Use |
|---|---:|---:|---:|---|
| H00 wet-feed interpretation | 204.261 | 0 | 0.057692 | Primary conditional candidate |
| H01 dry-feed interpretation | 205.050 | 0 | 0.058377 | Source-basis alternative |
| H02 counterfactual dry control | 199.377 | 0.251465 | 0 | Diagnostic |
| H03 upstream gauge-pressure interpretation | 204.270 | 0 | 0.057692 | Pressure-interpretation diagnostic |
| H04 imposed 196 K | 196.000 | 0.867162 | 0.057705 | Nonadiabatic audit only |

H00-H03 close the defined component and energy budgets. H04 requires about **496 kW heat removal** for the assumed feed and prescribed outlet speed; it does not satisfy that adiabatic PH target. This does not establish real experimental heat loss or show that the reported 196 K is wrong: entrainment, source basis and control-volume assumptions remain uncertain.

The reduced model passed 38 tests and 34 numerical/property checkpoints. Ideal gas, immiscible condensates, instantaneous equilibrium and common phase motion are approximations. Verification is not experimental validation. H00 contains gas-phase propane but is **not all gas**. Ice is about 0.532% of total mass; small mass fraction alone does not justify discarding phase-change energy.

## Proposed H00 boundary

All values are conditional calculations or geometry assumptions, not new measurements.

| Quantity | Candidate |
|---|---|
| Pressure / temperature | 102500 Pa / 204.260962 K |
| Total mass / propane flow | 10.845671 / 3.000000 kg/s |
| Gas / ice flow | 10.787979 / 0.057692 kg/s |
| Gas propane concentration | 20.190080 mol% |
| Bulk density / volume flow | 1.942593 kg/m³ / 5.583091 m³/s |
| Speed / assumed direction | 18.1 m/s; azimuth 30° in local magnetic-north frame |
| Advective momentum rate | 196.306653 N; no assumed excess-pressure thrust |
| Thermal enthalpy flow / outgoing kinetic energy | -193794.198255 W / 1776.575212 W |
| Inlet area | 0.308458 m² |
| Assumed width / height | 0.785440 / 0.392720 m, aspect ratio 2:1 |
| Assumed centre | (2.500, 4.330127, 0.500) m |

Negative enthalpy reflects the property reference. A future solver must use the same reference or explicitly map species/phase reference offsets; copying the number into another property package without that audit is invalid.

Area follows volume flow divided by speed, including condensed-phase volume. It is 1.40% larger than the original 0.3042 m² rectangle. Preserve prescribed 18.1 m/s and derive area for this candidate. Do not impose original area, new density, original velocity and original mass rate simultaneously. If original area is prioritized later, solve velocity and the kinetic-energy/PH balance together rather than adjusting velocity after the flash.

The original note remains 196 K, 20 mol%, 18.1 m/s and a 0.78 × 0.39 m rectangle. Do not overwrite it or label H00 a measurement correction. H00's 20.190080% is gas-phase mole fraction after water condensation; the assumed feed's 20% total mole basis differs. Do not renormalize the gas back to 20%.

Use gas mass fractions for a gas-species formulation and total component fractions for HEM. Bulk density includes ice and must not be assigned as gas density. Evaluate phase volumes/densities consistently if a solver requires them separately.

Inject the equivalent mixture only at the downstream window. It already contains assumed entrained air/water: injecting the original nozzle too, or adding the same entrainment again at the window, double-counts mass and energy.

## Phase-bearing maths

For a common-velocity mixture, each total component obeys:
rho × Y_total,i = sum over phases(alpha_phase × rho_phase × Y_phase,i).
The mixture density obeys 1/rho = sum over phases(w_phase/rho_phase).

Transport total propane, total water and carrier components, momentum, and a consistently defined energy variable. At each local pressure, composition and thermal enthalpy, the PH closure returns temperature, phase split and density. Water can sublime, melt or evaporate during warming; propane condensation must remain available wherever phase stability requires it. Do not freeze H00 phase fractions everywhere.

Phase enthalpies already contain latent effects. Add no second latent-heat source for the same equilibrium transfer. Distinguish thermal enthalpy from kinetic/gravitational energy in the actual transport equations. Phase redistribution must conserve total component mass and energy.

Common motion/temperature assumes fast mechanical/thermal relaxation and phase equilibration. Particle-size, slip, nucleation and deposition evidence is unavailable. If those processes matter, a separate-phase or particle model needs size/transfer data and an explicit water-ice/propane closure. Do not invent inputs to make a stock solver usable.

OpenFOAM remains a possible platform. Its [multiphaseEuler reference](https://cpp.openfoam.org/v14/classFoam_1_1solvers_1_1multiphaseEuler.html) describes compressible fluid phases with optional transfer models (existing source-register SRC-040). That capability does not establish a validated atmospheric ice-aerosol configuration. No stock gas-only or multiphase configuration is selected here.

## Before dispersion execution

1. **Review applicability.** Show H00 assumptions, the rejected native water closure and H01-H04 alternatives to the mentor. Seek source-water/basis, window-placement and particle/phase-relaxation evidence. Missing history can remain explicitly unresolved for a conditional study.
2. **Plan a mixing-path check.** Combine one H00 stream with increasing ambient wet-air mass at 283.05 K, RH 99%, and 102500 Pa. Conserve component flow and thermal enthalpy; treat kinetic-energy dissipation separately and consistently. Check ice disappearance/melting, possible propane condensation, phase transitions and density/enthalpy behaviour. Do not prescribe temperature by linear interpolation. No such calculation is executed here.
3. **Audit an implementation.** Demonstrate the verified closure, property-reference mapping, changing condensates, conservative transport and buoyancy. Stay inside the reviewed 180–300 K / 50–200 kPa domain; fail explicitly outside it. Verify positivity and phase limits. No silent clipping or extrapolation.
4. **Freeze revised inputs.** Version S00-S08 before execution, retaining weather/placement alternatives and observation policy. Use H00-derived geometry; ground-touching centre becomes half its height (0.196360 m). Review turbulence length derived from the old height. H01 is a targeted source-basis follow-up, not nine automatic extra cases. H02-H04 are not default CFD cases.
5. **Separate instruction before CFD.** Numerical/transport checks precede one flat-ground H00 comparison; expand physical sensitivities only after numerical gates pass. Thermodynamic verification does not unlock terrain, Adoshi transfer or app work.

The mixing-path check and implementation audit assess whether HEM is practical; they cannot recover historical truth or replace missing phase-rate evidence.

## Testing and comparison

Retain the [sensitivity-study rules](EEC550_SENSITIVITY_STUDY.md), with a documented v2 before execution. Proposed internal transport gates: each component's normalized cumulative mass imbalance at most 1%; total-energy imbalance at most 1%, accounting for boundary, storage, wall and gravity terms. Normalize energy with a declared positive throughput scale based on absolute energy fluxes, not a signed near-zero net flux. Show absolute residuals and reference sensitivity too. These are screening choices, not certified accuracy criteria. Retain the stricter existing equilibrium checks for local PH calls.

Uniform-flow transport and closed mixing/phase-change checks must conserve **total propane and water across phases**, not just gas species. Include sublimation and melting. Empty-atmosphere maintenance, three meshes, reduced time step and enlarged domain remain gates. Review implementation-specific tolerances and property interpolation error before freezing a solver recipe.

Use all 30 concentration receptors at recorded coordinates/heights. Confirm instrument concentration basis; compare gas propane mole fraction only if it matches that definition. Preserve zeros, declare missing predictions, and report bias, MAE, RMSE and FAC2 under the predeclared zero policy. Experimental standard deviation is temporal variability, not a confidence interval. Arc summaries are supplementary, not independent extra validation points.

Retain a developed unfenced plume, readiness determined from predictions, and 150 s model averaging. Historical averaging indices and the 150/360 s duration conflict remain unresolved; this is not a reconstructed fresh pulse. Preserve measured wind direction and distinct neutral/unstable assumptions. Overlapping windows are not independent trials.

Report numerical sensitivity, missing-input sensitivity and experimental discrepancy separately. Do not select H00/H01 or placement by best experimental fit. EEC560 remains excluded from tuning. No claim about terrain flow, propylene, Adoshi hazard distances or operational safety follows from this flat-ground propane comparison.

## Review-record checks

Checked source-ledger arithmetic, normalized UTF-8 result hash, unchanged historical JSON input fields, local links, JSON syntax and source-register structure. Existing equilibrium code/results are unchanged; their earlier test results were reviewed, not rerun. No dispersion predictions were generated.
