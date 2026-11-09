# Mathematics and validation plan

## Calculation chain

Tank/release conditions -> source term -> atmospheric dispersion -> threshold envelope -> geographic intersections.

For inventory M, track release to the environment separately from transfer to receiving tankers:

dM/dt = -release_rate(t) -transfer_rate(t)

The source model must handle the applicable phase and thermodynamic regime. A pressurised liquid discharge is not automatically identical to the airborne gas source.

A dispersion model estimates concentration as a function of position and time. Threshold polygons must identify hazard, threshold/unit, averaging time, assessment height, model assumptions and prediction period.

## Model decision

The [humidity/phase decision](research/EEC550_PHASE_REVIEW.md) supersedes acceptance of the earlier gas-only configuration: the proposed source is supersaturated in the ideal propane screen, and ambient moisture cannot be retained entirely as vapour at 196 K. Reconcile source phase/enthalpy before executing the sensitivity design. OpenFOAM as a platform remains a candidate; no replacement configuration or accuracy result exists.


OpenFOAM Foundation 14 multicomponentFluid was selected conditionally before this phase review; that gas-only configuration is now not accepted for the current EEC550 inlet; see the [input/model plan](research/EEC550_COMPARISON_PLAN.md). No engine or equations have been selected for production use. Evaluate an established applicable source/dispersion workflow and integration/licensing constraints before implementation. Use reviewed ALOHA runs as references; do not assume an ALOHA automation API exists.

The original project's mass-based blast/fireball rings and geometric ellipse are not validated propylene release models.

## Test ladder

1. Verification: units, mass conservation, valid domains, coordinate transformations, wind-from convention, reproducibility, and numerical convergence where applicable.
2. First research comparison: prepare and verify the EEC550 flat-ground mixed-source setup; compare matching sensor concentrations only after source/averaging gates are reviewed. Relevant official ALOHA examples can be separate screening checks with assumptions and version differences documented.
3. Matched PHAST comparison: use the same source inputs and assessment definitions; report stage-by-stage differences.
4. Experimental validation: select applicable SMEDIS cases using measured source, weather and concentration records. Keep evaluation cases separate from tuning cases.
5. Sensitivity: vary justified uncertain inputs and report resulting changes; do not attach unsupported probability/confidence claims.
6. Tabletop review: evaluate provenance, missing-data handling, observation conflicts, assessment updates and handover clarity.

## Selected experimental starting point

The [SMEDIS review](research/SMEDIS_REVIEW.md) recommends EEC550 as the initial unobstructed propane case, EEC360 as a smaller-source comparison after duplicate-record handling is agreed, and EEC560 reserved from future fitting. Start with documented downstream equivalent sources for dispersion-only tests. Source-model validation remains separate. All selections are conditional on engine capability and agreed input/measurement handling. No model runs or accuracy claims exist.

## EEC550 follow-up

The [input-resolution review](research/EEC550_INPUT_RESOLUTION.md) confirms the local magnetic-north coordinate frame and shows that the original trial contained fenced and unfenced phases. REDIPHEM lists a 360 s full release; SMEDIS B27 lists 150 s. Preserve that discrepancy. The conditional first comparison uses a developed unfenced plume and a separate 150 s model averaging window, not a fresh 150 s pulse. Exact historical averaging indices and actual downstream inlet elevation remain unverified. A neutral weather baseline is declared separately from estimated unstable sensitivity; thermal/humidity/turbulence setup still needs review. No results exist.

## PHAST comparison checklist

Ask the mentor for:
- Product/version and available modules, including any CFD extensions.
- Agreed chemical property basis and complete tank/release input sheet.
- Wind height, stability method, surface conditions and other atmosphere settings.
- Source coordinates/height/orientation and concentration definitions.
- Thresholds, units, averaging time, receptor height and assessment period.
- Permitted input/output exports and report redistribution terms.

Compare source rate and state first, then concentration/distance results and threshold geometry. If possible, also compare dispersion with an identical defined source to separate source-model differences from dispersion-model differences.

PHAST agreement is model benchmarking, not experimental validation. Differences may result from legitimate assumptions and should be explained rather than hidden or tuned away.

## Metrics and gates

Record absolute/relative errors where meaningful for release rate, threshold distance and selected measurement locations/times. Handle zero values and below-detection observations explicitly. Add time-step/grid sensitivity when applicable.

The [EEC550 sensitivity design](research/EEC550_SENSITIVITY_STUDY.md) proposes internal numerical screening tolerances and a materiality triage rule before any run. These are study choices, not experimental accuracy requirements or SMEDIS pass marks. Review implementation-specific settings and experimental performance expectations before evaluation. Standalone thermodynamic numerical runs and checks now exist; no dispersion-validation or accuracy claim exists.

## Terrain boundary

Version 1 displays terrain and flags features for investigation. An ALOHA/free-field footprint over terrain remains subject to its original assumptions. Do not validate terrain-dependent gas movement using a visual overlay or synthetic detector points.

Actual Adoshi plume validation requires field release/weather/concentration records not currently available.

## Source-energy thermodynamic milestone

The [reconciliation plan](research/EEC550_SOURCE_ENERGY_RECONCILIATION.md) defines conditional mass ledgers, H00–H04 and a pressure-enthalpy homogeneous-equilibrium assessment using local ThermoPack properties with explicit ice-aware calculation. The planning record did not contain computed states. The [implementation report](research/EEC550_EQUILIBRIUM_VERIFICATION.md) now records conditional equilibrium states and numerical residuals; a unique historical source remains unestablished. Component and energy residual targets are proposed numerical checks, not experimental accuracy criteria. Confirm fluid/ice references and phase stability before any dispersion validation.

## Standalone implementation verified

The reduced ThermoPack-based package passed 38 tests and 34 CLI checkpoints. The original PR/water-ice closure failed a property screen and was replaced with an explicit IAPWS/NIST saturation-Gibbs/enthalpy water closure. This verifies the defined reduced model, not physical phase rates, the historical EEC550 source or dispersion. See the [verification report](research/EEC550_EQUILIBRIUM_VERIFICATION.md).

## Equilibrium-to-dispersion review

The [handoff plan](research/EEC550_DISPERSION_HANDOFF.md) defines a conditional H00 boundary, conservative total-component/enthalpy transport requirements, phase-bearing model gates and a versioned revision of the held sensitivity matrix. Preserve gas-versus-total concentration bases and the original source note. A phase-bearing implementation audit and numerical checks precede the conditional 30-receptor comparison. No new model execution occurred in this review.

## Mixing research checkpoint

The [executed 11-point mixing path](research/EEC550_MIXING_MILESTONE.md) conserves total component flow and thermal enthalpy as declared humid air is added to H00. It tests the reduced closure beyond the initial source and reveals changing ice/liquid-water phases. It does not validate relaxation times, transport, distance or dilution rates. The suite now has 51 passing tests; 16 additional handoff arithmetic checks passed. No dispersion or Adoshi validation claim follows.

## Research workbench v1

The [implemented workbench](research/WORKBENCH_V1.md) extends the verified source calculation to 132 conditional equilibrium states with fixed source interpretations and declared downstream RH sensitivities. The complete local suite passes 136 tests; each of four exported reference-source contracts passes 39 checks. This establishes repeatable numerical source/mixing accounting and a strict interface, not a validated transport closure. The offline report is tested for data safety, structure and filtering; browser layout inspection remains unverified. Original measurement records are unchanged.

## First numerical transport checks

The [transport prototype](research/TRANSPORT_PROTOTYPE_SUMMARY.md) passes analytical shift/diffusion/refinement and conservation tests; the research suite has 154 passing tests. This verifies prescribed-flow numerical transport with local equilibrium diagnostics, not atmospheric dispersion. Fixed reference-mass accounting does not solve variable-density continuity or buoyancy.

## Variable-density hydrodynamic verification

The [new flow stage](research/VARIABLE_DENSITY_SUMMARY.md) adds density-dependent flow/gravity/projection. Package tests: 173 passed; independent checks: 22 passed. Hydrostatic rest, buoyancy sign/controls, projection, scalar/density conservation and a small grid comparison provide numerical evidence. Endpoints are frozen; velocity-form advection is not a conservative momentum scheme. This does not validate thermal phase coupling, atmospheric turbulence or EEC550 field concentrations.

## Conservative thermal and phase coupling

The [new 1D prototype](research/THERMAL_PHASE_SUMMARY.md) passes 210 package tests and 210 independent checks. UV round trips, ideal-gas acoustics, stationary contacts, closed periodic species/momentum/total-energy budgets and independently rebuilt cell thermodynamics are tested. Heat/control comparisons distinguish physical conduction response from numerical mixing. An acoustic refinement benchmark reduces error across three meshes. No moving-contact/strong-shock, multidimensional thermal-buoyancy or EEC550 validation claim follows.

## Integrated 2D thermal/gravity verification

The [2D integrated prototype](research/THERMAL_2D_SUMMARY.md) passes 232 package tests and 552 independent checks. Conservative component/total-energy budgets, gravity plus wall-force momentum balance, per-cell thermodynamic reconstruction, hydrostatic rest, heat/gravity controls, reference invariance and a nontrivial 1D reduction are covered. These demonstrate implemented coupling and numerical accounting; tiny closed-box runs do not establish long-time atmospheric accuracy or EEC550 validation.
