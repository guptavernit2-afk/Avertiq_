# EEC550 humidity and phase review

8 November 2026. Property screening and model-selection research only. No application code, solver configuration, installation, CFD runs or rigorous equilibrium flash calculation.

## Decision

**Do not accept the proposed unmodified gas-only multicomponentFluid setup for the EEC550 comparison at the documented 196 K / 20 mol% inlet.** Two checks fail to support an equilibrium all-gas assumption: propane supersaturation at the selected pressure, and the phase behaviour of water carried by humid entrained air.

This supersedes the earlier conditional selection of a gas-only configuration. OpenFOAM remains a possible research platform, but no replacement multiphase configuration is selected or validated. Hold the nine-case sensitivity study until the source state and phase/enthalpy treatment are reconciled. Do not run the gas-only cases and treat measurement agreement as proof that omitted phase physics is negligible.

## Inputs and assumptions

| Item | Value | Evidence |
|---|---|---|
| Equivalent source temperature | 196 K | Batch-1 equivalent-source note |
| Propane molar concentration | 20% | Same note; gas/total and wet/dry reporting details not fully recovered |
| Source pressure used for screening | 102500 Pa absolute | Selected ambient workbook value, assumed appropriate at downstream plane |
| Ambient temperature | 283.05 K (9.9 C) | Workbook B40 |
| Ambient RH | 0.99 (99%) | Workbook B42; not water mole fraction |
| Source-water inventory/phase | Unknown | Not supplied by the short equivalent-source note |
| Original nozzle liquid phase | Before flashing | Not automatically the downstream phase inventory |

The pressure at the downstream window has not been independently measured. Use the selected ambient pressure transparently, not the upstream 10 atm nozzle pressure. These are ideal partial-pressure equilibrium checks, not a full fugacity-based flash, droplet measurement or phase-transition-rate prediction. Finite residence time/nucleation could permit nonequilibrium states; such a defence needs evidence and a corresponding model.

## Propane check

Use the [NIST low-temperature Antoine fit](https://webbook.nist.gov/cgi/cbook.cgi?ID=C74986&Mask=FEF&Plot=on&Type=ANTOINE&Units=SI), valid 166.02–231.41 K:
log10(p_sat/bar)=4.01158-834.26/(T/K-22.763).

At 196 K:
- Pure-propane saturation pressure = **15.699 kPa**.
- Ideal propane partial pressure = 0.20*102.5 = **20.500 kPa**.
- Saturation ratio = **1.306**; saturated gas mole fraction would be about **15.32%** at this temperature/pressure.
- The ideal dew temperature for 20 mol% at 102.5 kPa is about **200.27 K**.

Therefore the prescribed all-gas boundary is supersaturated in this screen. Comparing 196 K with the pure-component normal boiling point alone would be wrong; mixture partial pressure is the relevant first check. Do not extrapolate the separate NIST 230.6–320.7 K coefficient set down to 196 K.

The result is not repaired by a routine one-atmosphere substitution: at 101325 Pa the same screen still indicates supersaturation. At 196 K, 20 mol% would require total pressure <=about 78.49 kPa for this ideal saturation criterion. Neither such a pressure nor a warmer revised source is documented. These thresholds are diagnostics, not permission to edit the experiment.

## Ambient moisture and cold-source water

[NIST water coefficients](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Plot=on&Type=ANTOINE), used within their 273–303 K range, give ambient liquid-water saturation pressure about **1218.81 Pa**. At RH=99%, water partial pressure is **1206.62 Pa**, water mole fraction about **1.177%**, and dew point about **282.90 K**. Ambient air is consequently close to saturation.

At 196 K use an ice-vapour relation, not that warm-water Antoine fit. [IAPWS R14-08(2011)](https://iapws.org/technical-guidance/release/MeltSub) Eq. (6) gives ice sublimation pressure **0.08693 Pa**.

Conditional water-carryover diagnostic: if 80% of the inlet's moles are entrained ambient wet air retaining all its vapour, then x_water=0.8*0.0117719=0.0094175 and p_water=**965.30 Pa** at 102500 Pa. This is roughly **11000 times** ice saturation at 196 K. It cannot represent an equilibrium gas-only inlet with all that water retained as vapour. The numerical carryover is an assumption, not a recovered inlet measurement.

Setting RH=99% at the cold inlet would instead introduce a vastly different water inventory. Likewise, declaring the source dry does not make surrounding humid air dry or establish that later mixing avoids condensation.

Water can condense as the mixture cools and can form ice at sufficiently low temperature; warming and dilution can subsequently cause evaporation/sublimation. The actual phase split and rates require mass/enthalpy and phase-kinetic treatment. Do not infer an observed ice fraction, visible-fog extent or deposition rate from this equilibrium screen.

## Why this matters for the calculation

Condensation/deposition release latent heat; evaporation/sublimation absorb it. Condensed material also carries mass, enthalpy and potentially relative momentum. These processes can change cloud temperature, density and buoyancy. Small water mass does not automatically imply a negligible thermal effect.

The note describes a downstream state where liquid has disappeared, but does not provide a phase-resolved water inventory, enthalpy or derivation. It is insufficient to establish that all species are gaseous. Its rounded propane state also conflicts with the ideal saturation screen under the selected pressure. Preserve the original note and investigate its concentration basis, thermodynamic assumptions and pressure rather than declare it false or silently repair it.

If an upstream source model already included atmospheric-water heat effects, adding condensation heat again to the fixed 196 K boundary would double-count energy. Conversely, retaining its temperature while dropping condensed water would change mass and energy unless an explicit equivalent-source mapping justified it.

## Solver assessment

The [Foundation 14 predictor source](https://raw.githubusercontent.com/OpenFOAM/OpenFOAM-14/master/applications/modules/multicomponentFluid/thermophysicalPredictor.C) transports species and energy, with optional source terms. Our proposed nonreacting gas-only mixture has no specified condensate inventory, interphase transfer or ice treatment. Adding gaseous H2O to the species list does not by itself supply them.

The [multicomponentFluid documentation](https://cpp.openfoam.org/v14/classFoam_1_1solvers_1_1multicomponentFluid.html) permits extensions, including particles. Thus this is a rejection of the proposed configuration, not a claim that OpenFOAM cannot represent phase change.

[multiphaseEuler](https://cpp.openfoam.org/v14/classFoam_1_1solvers_1_1multiphaseEuler.html) supports multiple fluid phases and optional interphase transfers; the [phaseChange framework](https://cpp.openfoam.org/v14/classFoam_1_1fv_1_1phaseChange.html) exposes mass and latent-heat transfer. These are capability leads, not a ready EEC550 solution. Water-ice transitions, dilute aerosol behaviour, phase relaxation and needed closures must be checked explicitly. Do not assume a boiling/condensation tutorial handles atmospheric ice.

## What we should do next

1. Reconcile the equivalent source: confirm its pressure, propane concentration basis, water/propane phase inventory and whether latent effects were included. Retain unresolved inlet placement/timing from the [earlier review](EEC550_INPUT_RESOLUTION.md).
2. Plan an enthalpy-conserving moist phase-equilibrium assessment of that source and its mixing with ambient air. Track dry air, total propane and total water separately from their phase fractions; use valid-range properties and review fugacity corrections. Do not prescribe both a fixed temperature and arbitrary new phase fractions.
3. Use that assessment to choose between a reviewed phase-changing mixture model and a genuinely justified gas-only downstream state. The latter requires consistent flux, momentum, enthalpy, position and measured comparison coverage, not simply raising temperature to the dew point.
4. Specify and verify phase mass/energy conservation and thermodynamic limit cases before reviving the sensitivity matrix. If relaxation/particle behaviour matters, equilibrium alone is not sufficient.
5. A gas-only model could still serve as a separately labelled idealized numerical exercise or a warm/dilute comparison after justification. It is not presently accepted as an EEC550 physical baseline.

No new source state or alternative engine is invented here. No install or phase-model implementation is authorized by this review.

## Reproducibility

[Phase-screen record](../../data/public/eec550-phase-screen.json) records input assumptions, formulas, coefficient ranges, calculated values and checks. Raw NIST HTML snapshots and the IAPWS PDF are retained locally with hashes in the [external manifest](../../data/public/external-download-manifest.json).

For IAPWS, theta=T/273.16 and:
ln(p_ice/611.657 Pa)=[sum(a_i*theta^b_i)]/theta,
with a=(-21.2144006,27.3203819,-6.10598130), b=(0.00333333333,1.20666667,1.70333333), valid 50–273.16 K. Eq. (6) and its range were visually checked on PDF p. 5. Arithmetic reproduces the official 230 K check (8.94735 Pa, rounded) and triple-point pressure 611.657 Pa.

This is a property-screen result. It neither predicts the cloud nor validates any model.

[Short report](EEC550_PHASE_SUMMARY.md)
