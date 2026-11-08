# EEC550 source mass/energy reconciliation and local model decision

8 November 2026. Planning, property arithmetic and read-only software review only. No application code, library installation, model execution or equilibrium solution.

## Decision and result

Select a **zero-dimensional, constant-pressure homogeneous-equilibrium (HEM) calculation**, conserving component totals and enthalpy, as our next thermodynamic model. Select **ThermoPack as the local property-library candidate**, including its water-ice model. A small solid-aware equilibrium/energy calculation will need implementation later; this is not an already runnable one-call flash or a selected CFD solver.

The conditional component ledger is closed below. The energy specification is defined, but a numerical equilibrium temperature and phase split have **not** been solved. Available evidence does not identify a unique historical downstream state. Preserve that distinction: this is a reconciled calculation specification, not a reconstructed measurement.

The original gas-only CFD baseline remains unaccepted; the nine-case dispersion study stays held. This study can decide which thermodynamic representation merits a later CFD comparison. It does not itself model a plume.

## 1. What we can and cannot fix

Retain the originals: physical propane 3 kg/s, liquid feed 286.45 K, pressure label 10 atm, and the equivalent window 196 K / 20 mol% / 18.1 m/s / 0.3042 m2. Ambient values remain 283.05 K, 102500 Pa and RH 99%.

Unknowns include wet/dry and gas/total concentration basis, downstream pressure, source enthalpy, condensed-water inventory, actual entrainment, any heat/deposition losses and static versus stagnation interpretation of upstream temperature. Absolute/gauge pressure and original inlet elevation/timing remain unresolved.

The source note is an equivalent downstream state, not an independent set of exact constraints. At selected pressure, its all-gas propane assumption fails the previous saturation screen. Fixing its temperature, gas concentration, phase split, mass rate, velocity and area simultaneously would overconstrain an equilibrium reconstruction.

**Primary reconstruction:** anchor propane mass at 3 kg/s and specified upstream/ambient feed states. Assume an entrainment interpretation, downstream pressure and heat-loss policy; solve temperature and phase amounts. Treat reported 196 K, gas concentration and window area as comparisons, not values forced into the answer.

## 2. Conditional component ledger

Use workbook propane MW=44.1 g/mol, water MW=18.0153 g/mol and approximate dry-air MW=28.965 g/mol for this arithmetic audit. Ambient water mole fraction from the prior valid-range screen is 0.0117719. The approximate dry-air convention must be reconciled with any explicit N2/O2/Ar species representation at implementation.

Propane molar rate = 3/0.0441 = 68.0272 mol/s.

| Interpretation | Dry air kg/s | Total water kg/s | Total mixture kg/s |
|---|---:|---:|---:|
| R-W: 20% refers to total propane feed / (propane + wet-air feed) | 7.78885 | 0.057707 | 10.84656 |
| R-D: 20% refers to propane feed / (propane + dry-air feed), then add ambient moisture | 7.88163 | 0.058395 | 10.94003 |

Both rows are **assumed total-feed interpretations**, not recovered source compositions. If the note's 20% means gas-phase concentration after condensation, neither row is directly established.

R-W uses n_wet_air=4*n_propane, n_water=x_water_ambient*n_wet_air and n_dry_air=(1-x_water_ambient)*n_wet_air. R-D uses n_dry_air=4*n_propane and n_water=n_dry_air*x_water_ambient/(1-x_water_ambient). Water totals include any subsequent ice/liquid/vapour; do not remove condensed mass from the balance.

**Independent window diagnostic:** an ideal dry mixture at the original 196 K, 102500 Pa and gas mole fraction 0.20, through 0.3042 m2 at 18.1 m/s, implies propane 3.05450 kg/s, about 1.82% above 3 kg/s. This is a rounded-input consistency check, not a measured flow or a valid all-gas source. Do not rescale concentration/area to conceal the discrepancy.

## 3. Energy specification

For a steady, nonreacting control volume from upstream liquid plus entrained ambient air to the equivalent window:

sum_in[m_dot*(h + U^2/2 + g*z)] + Q_dot - W_dot
= sum_out[m_dot_phase*(h_phase + U_phase^2/2 + g*z)].

Use enthalpy in J/kg and power in W. Pressure-flow work is already included in h. Count every component and condensed phase. In the HEM approximation all phases share one temperature and velocity; phase enthalpies contain latent effects automatically.

**Assumptions for the first conditional calculation:** no external heat/work, no rainout/deposition, all entrained water retained, equal phase velocity and zero net elevation-energy change. Take the liquid-feed enthalpy from the documented 286.45 K and a stated pressure branch. Using that temperature as a stagnation feed with negligible feed kinetic energy is an additional approximation; if the original state is static, account for its kinetic term instead of adding both.

Downstream pressure is assumed 102500 Pa. Prescribe outlet U=18.1 m/s for this thermodynamic audit, not as a momentum prediction. R-W outlet kinetic power is about 1.777 kW. Include or explicitly separate ambient inflow kinetic energy; using 2.73 m/s is a declared reference-speed approximation.

The required static thermal power is incoming total energy less outgoing kinetic/potential power. The pressure–enthalpy solve returns T and phase amounts satisfying that target. It must not add an extra latent-heat correction after using phase enthalpies.

**Scale check, not an energy closure:** for R-W, assuming dry-air cp=1.005 kJ/(kg K), cooling its dry air from 283.05 to 196 K releases about 681 kW. Assuming a water phase-change enthalpy scale of 2.8 MJ/kg gives another 162 kW for its water inventory if it all changes phase. These are deliberately approximate study constants, not full temperature-dependent property evaluations or predicted heat release. They show why ignoring water can matter. They do not yield an equilibrium temperature or authorize adding 162 kW to a source temperature that may already include moisture effects.

No complete numerical energy residual is reported because a consistent fluid/ice property evaluation and feed interpretation have not been executed. Do not describe the unsolved energy balance as passing.

## 4. First thermodynamic cases

| ID | Specification | Purpose |
|---|---|---|
| H00 | R-W, moist air, assumed 10 atm absolute liquid feed, downstream 102500 Pa, adiabatic retained mixture | Primary conditional PH/HEM case |
| H01 | R-D; otherwise H00 | Concentration-basis interpretation |
| H02 | H00 dry-air and propane totals, remove water only; do not renormalize dry air | Counterfactual dry control for latent/moisture effect |
| H03 | H00 but upstream 10 atm interpreted as gauge: 1013250+102500=1115750 Pa absolute | Pressure-label ambiguity; absolute branch is 1013250 Pa |
| H04 | Original 196 K imposed for a TP equilibrium audit, with H00 component totals | Calculate required enthalpy and energy mismatch; not an alternative PH solution |

In H04 compare the equilibrium gas concentration with the original 20% separately. Do not insist that TP equilibrium also retain all propane in gas. Calculate the external heat that would be required to make that imposed temperature consistent, then label it an implied discrepancy, not real measured heat exchange.

An actual gas-phase 20% at 196 K and selected pressure is already incompatible with the ideal saturation screen. More rigorous fugacity treatment is a property check, not permission to relabel total-feed concentration as gas concentration.

Future PH results may differ from both original temperature and gas concentration. That is an outcome to investigate, not an input to tune away.

## 5. Selected model and local implementation route

HEM assumes immediate local phase equilibrium and negligible phase slip. Allow gas, a propane-rich liquid, water-rich liquid and pure water ice as thermodynamic candidates; compare stable phase sets rather than imposing every phase as present. Retain dry-air species, propane and water component totals. Ignore reactions. A pure-immiscible-condensate approximation may be the first transparent reduced model; document its omitted solubility and compare with fluid-mixture fugacities before claiming applicability.

Select a solid-aware equilibrium calculation at each trial temperature, with an outer energy root at fixed pressure. Use nonnegative phase amounts, component conservation and equal chemical potentials for phases that coexist; inactive phases must pass stability checks. At a phase-transition plateau, allow phase fraction to satisfy energy rather than forcing a unique temperature-only root.

**ThermoPack is selected for local feasibility work, not certified properties.** Its official repository documents free Apache-2.0 licensing and Windows/Linux/macOS distributions. Inspected source commit: d68c794c7342bfc6938eb424a1fbb88b7780b738 (26 February 2026). This pins the research snapshot, not an installed runtime.

The ice module contains a Feistel–Wagner water-ice Gibbs model. Its initialization aligns the ice reference to the selected liquid-water fluid model. This directly addresses the risk of combining unrelated enthalpy zeroes, but still requires pure-property verification.

Important interface limitation: the reviewed public Python PH method and ph_solver operate on vapour/liquid states. Calling init_solid(H2O) does not prove that two_phase_phflash includes ice. Use the library's fluid/ice properties with an explicit solid-aware equilibrium/energy layer, or verify a genuinely solid-capable library entry point before adopting it. Do not present an unverified API as available.

Start property assessment with documented Peng–Robinson fluid support and the built-in water-ice model. Water association, cryogenic saturation and cross-component parameters are not automatically accurate under a cubic equation of state. Compare pure propane with NIST and water/ice with IAPWS first; if the candidate property model fails, revise the property package before computing EEC550 outcomes. A generic CPA label or zero default binary interaction parameter is not evidence of accuracy.

We will need a small implementation after user instruction. No paid PHAST licence is required for this route, but local installation, runtime compatibility, numerical robustness and applicable properties remain untested. Do not promise an off-the-shelf, ready-to-run moist four-phase flash.

## 6. Other options and limits

| Option | Finding | Decision |
|---|---|---|
| ThermoPack-backed 0D HEM | Fluid and water-ice properties; energy-equilibrium design feasible; solid-aware calculation needs explicit implementation | Selected next thermodynamic route |
| Stock gas-only OpenFOAM | No phase-resolved source/latent treatment in proposed setup | Still not accepted |
| OpenFOAM multiphaseEuler | Potential heat/mass-transfer framework; needs aerosol/ice closures and consistent source | Defer CFD selection until thermodynamic assessment |
| code_saturne humid-atmosphere route | Published EEC propane work makes it relevant; reviewed material does not establish a ready current propane/water/ice PH source model | Not selected as a shortcut |

HEM is an equilibrium reference, not a validated phase-rate model. If evaporation/condensation/freezing times compete with transit time, or particles slip/deposit, a relaxation/particle model needs separate data and verification. The rough 5 m / 18.1 m/s = 0.28 s transit scale is only a constant-speed indicator, not an actual residence-time measurement.

## 7. How we will check the thermodynamic model

Before CFD, require:
- Valid property ranges and explicit fluid/ice reference consistency. Reproduce earlier NIST/IAPWS screen points and pure-water melting/sublimation behaviour.
- A dry, all-gas limit; wet cases with and without stable ice; and appropriate no-condensate/phase-appearance limits.
- Component residual <=1e-8 relative for each nonzero feed component, and enthalpy residual <=1 J/kg mixture. These are proposed internal numerical targets, not experimental accuracy claims.
- Multiple starting guesses and bracket/phase-set checks; no negative fractions, hidden clipping or failure reported as a valid state.
- Compare thermodynamic property discrepancies before accepting an equation of state; do not relax tolerances because one option fits EEC550 better.
- Record feed basis, pressure, properties, phase composition, gas versus total concentration, energy terms and any implied heat/mass discrepancy for every case.

After a successful PH solution, derive density from phase volumes. With prescribed U, derive the implied area A=m_dot/(rho_bulk*U). Compare it with 0.3042 m2; do not force area, speed and mass simultaneously. A new downstream state is a candidate source, with geometry/momentum/enthalpy differences documented, not a silent replacement for SMEDIS.

The [structured record](../../data/public/eec550-source-energy-plan.json) preserves known values, assumptions, closed conditional mass ledgers, unsolved energy outputs and model status. Original source data remains unchanged.

## References

- [ThermoPack repository](https://github.com/thermotools/thermopack): licensing and local distributions.
- [Python methods](https://thermotools.github.io/thermopack/vcurrent/thermo_methods.html): fluid PH interface and solid property functions.
- [Pinned ice/solid interface](https://raw.githubusercontent.com/thermotools/thermopack/d68c794c7342bfc6938eb424a1fbb88b7780b738/src/solideos.f90), [ice Gibbs model](https://raw.githubusercontent.com/thermotools/thermopack/d68c794c7342bfc6938eb424a1fbb88b7780b738/src/h2o_gibbs.f90), [PH solver](https://raw.githubusercontent.com/thermotools/thermopack/d68c794c7342bfc6938eb424a1fbb88b7780b738/src/ph_solver.f90).
- [Equilibrium-algorithm memo](https://thermotools.github.io/thermopack/memo/flash/flash.pdf), sections 2.5.5–2.6: solid phases and an energy outer loop; does not establish the Python API's capabilities.
- [code_saturne EEC/atmosphere poster](https://www.code-saturne.org/cms/web/sites/default/files/file_attach/ClubU_2014/ClubU_2014-P6.pdf): a lead for later dispersion review.
- [Earlier phase screen](EEC550_PHASE_REVIEW.md): original values, NIST/IAPWS references and limits.

Raw reference snapshots are retained locally with hashes in the external download manifest. Source was inspected read-only, not installed or executed.

[Short report](EEC550_SOURCE_ENERGY_SUMMARY.md)
