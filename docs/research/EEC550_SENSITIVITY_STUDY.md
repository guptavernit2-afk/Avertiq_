# EEC550 sensitivity study: planning version 1

8 November 2026. Authorization: plan a conditional sensitivity study only. No code, solver setup, installation or simulations. Model platform remains OpenFOAM Foundation 14; no production engine decision changes.

## Purpose and interpretation

Determine how much selected missing-input interpretations change predicted concentrations. Compare every predeclared case with the same baseline and the same experimental records. This is an exploratory dispersion study under assumed conditions, not a faithful historical reconstruction or a search for the best-looking map.

Use the [input findings](EEC550_INPUT_RESOLUTION.md) and [input lineage](../../data/public/eec550-input-plan.json). The original inlet elevation and SMEDIS averaging indices remain unknown. Choosing a study assumption does not recover either fact. No probability distributions, confidence intervals, certified accuracy or worst-case bounds are implied by the ranges below.

## Baseline S00

| Item | Fixed study value | Evidence status |
|---|---|---|
| Chemical/source state | Propane-air, 20 mol% propane, 196 K, 18.1 m/s | Documented equivalent-source note; rounded values |
| Window | Width 0.78 m, height 0.39 m, normal to 30-degree jet | Dimensions from note; orientation assumed |
| Window centre | (2.500,4.330,0.500) m | Assumed: 5 m along original horizontal jet, inherited nozzle elevation |
| Source profiles | Uniform top-hat velocity, temperature and composition | Assumed; no measured inlet profiles |
| Wind | From 197.73 degrees, 2.73 m/s at 6 m | Selected revised SMEDIS inputs |
| Reference frame | X east, Y magnetic north, Z up | Supported by original trial analysis |
| Atmosphere | Neutral class D; z0=0.006 m; kappa=0.4; zero displacement | Class/roughness documented; exact neutral profile a simplification |
| Friction velocity | Derived 0.15806 m/s | Derived to match selected neutral wind profile, not a measurement |
| Ambient gas | 283.05 K, 102500 Pa | Selected SMEDIS inputs; historical pressure provenance qualified |
| Ground | Flat, impermeable, no-slip; adiabatic heat boundary | Flat surface documented; mechanical/thermal idealization assumed |
| Closure | Transient RANS k–epsilon, Cmu=0.09 | Selected research closure; buoyancy coupling must be checked |
| Source turbulence | Intensity I=10%, length scale ell=0.039 m | Assumed isotropic turbulence; ell=10% window height |
| Turbulent transport | Schmidt 0.7; Prandtl 0.85 | Study assumptions, not experiment-specific measured constants |
| Averaging | Developed unfenced plume; primary 150 s model window | Conditional comparison policy; historical start time unknown |

Keep source state, area, speed and composition fixed across the nine cases. Compute the inlet's propane flux from its actual mixture properties and report the small mismatch with nominal physical-source 3 kg/s; do not secretly renormalize geometry or concentration. Source turbulence changes alter turbulence energy/dissipation, not the prescribed mean velocity.

Humidity is **not silently converted from measured RH=99% to dry air**. Before execution, review species properties, propane phase feasibility and water condensation/freezing for the cold mixture. A dry, single-phase treatment is a declared model-form simplification only; its validity has not been established. If inappropriate, revise this study version and property model before any comparison rather than fabricate a humid inlet or compare inconsistent species bases. No arbitrary RH sweep is planned because humidity is documented, while the water/phase treatment is unresolved.

## Nine core cases

All changes are relative to S00, one factor at a time. A factor may require coupled boundary-condition changes for physical consistency.

| ID | Change from S00 | Label / reason |
|---|---|---|
| S00 | Baseline | Conditional reference; not claimed true setup |
| S01 | Centre height 0.195 m | Assumed ground-touching window; not an observed lower bound |
| S02 | Centre height 0.800 m | Assumed elevated stress case; not an observed upper bound |
| S03 | Centre XY=(1.523,4.763) m | Interpret 5 m downstream along measured wind; retain jet speed, direction and window normal |
| S04 | Wind-from 210 degrees | Documented ideal wind, compared with actual selected mean; source stays at S00 position/orientation |
| S05 | Weakly unstable atmosphere, L=-90 m | Estimated stability alternative; rebuild consistent ABL, not just one inlet number |
| S06 | Source turbulence intensity 5% | Assumed low-intensity scenario; ell remains 0.039 m |
| S07 | Source turbulence intensity 15% | Assumed higher-intensity scenario; ell remains 0.039 m |
| S08 | Ground fixed at 283.05 K instead of adiabatic | Assumed heat-exchanging surface at ambient reference temperature |

S01 keeps its rectangle entirely above ground, touching at the lower edge; verify no patch overlap or unintended blockage. Mesh representation must preserve the same physical area and flux in all cases. S02 is a design stress test, not evidence that 0.195–0.800 m brackets reality.

S03 changes position only. Changing both location and inlet direction would confound displacement with source momentum. S04 rotates the complete ambient wind/turbulence boundary treatment consistently; do not rotate the source or sensors. Neither case realigns observed concentration data to improve agreement.

S05 must use a documented Monin–Obukhov formulation with wind, potential temperature, heat flux and turbulence consistent with L=-90 m and U(6 m)=2.73 m/s. Freeze similarity functions, thermal roughness, reference-temperature height and buoyancy treatment before implementation. Do not retain both neutral u_star=0.15806 and estimated 0.190 as simultaneous exact constraints. This case is held until the ABL recipe is reviewed; if unavailable, report not run rather than replacing it with a neutral case.

For assumed isotropic source turbulence:
k=1.5*(I*18.1)^2, epsilon=Cmu^(3/4)*k^(3/2)/ell.
Units: k in m2/s2, epsilon in m2/s3. Vary k and epsilon together as I changes. Do not estimate atmospheric k from speed standard deviation alone or substitute source turbulence for ambient turbulence.

## Timing sensitivity: reuse each run

Define t_ready separately for each case using the same stability rule, independent of observed concentrations. Keep the inlet active and collect at least 300 s after t_ready.

| Window | Relative model interval | Role |
|---|---|---|
| W0 | t_ready to t_ready+150 s | Primary, always reported |
| W1 | t_ready+75 to t_ready+225 s | Shifted-window diagnostic |
| W2 | t_ready+150 to t_ready+300 s | Later-window diagnostic |

These are model-time windows, not guessed historical timestamps. W0/W1/W2 overlap and are not independent replicates; do not use them for confidence intervals. The full 300 s mean is a stationarity diagnostic, not a replacement for the 150 s primary mean. If deterministic RANS settles to a steady solution, identical windows do not establish that historical wind meander or timing uncertainty was negligible.

Do not vary release duration between 150 and 360 s to select a better fit. That source discrepancy requires separate source records or a later transient study. No fence-drop simulation is included.

## Numerical checks before sensitivity interpretation

These are **proposed internal numerical screening tolerances**, chosen for this exploratory study, not SMEDIS requirements or experimental accuracy criteria. Freeze them before the first evaluated run. Version any later changes with a reason independent of improved measurement fit.

- Clean-air ABL: at fixed upstream/downstream probes covering receptor heights where the inlet model applies, speed-profile drift <=5% of intended local speed and temperature drift <=0.2 K. Inspect k/epsilon and surface stress/heat consistency as well; no concentration-fit criterion enters this check.
- Propane mass budget: absolute inlet minus net boundary export minus domain storage change <=1% of integrated inlet propane mass. Include diffusive species flux and all boundaries; do not confuse plume storage with lost mass.
- Species/physics: document boundedness, sum of mass fractions, temperature/property validity and solver convergence. No silent clipping of negative concentrations or undocumented mass corrections.
- Plume readiness: after gas has reached the farthest receptors, require two consecutive 30 s block comparisons to satisfy RMS change of the receptor-mean vector <=max(0.01 percentage points, 5% of the previous vector RMS), with mass budget passing. Record the first qualifying t_ready. If never achieved, label nonstationary; do not choose a favourable window.
- Baseline numerical sensitivity: three systematically refined meshes resolving the window and low sensors; a halved time-step case; a larger-domain case. These are additional verification calculations, **not included in nine physical cases**. Keep physics fixed.
- For fine/medium mesh, time and domain comparisons: receptor-vector RMS difference <=max(0.01 percentage points, 5% of reference-vector RMS); also flag individual differences >max(0.02 percentage points, 10% of reference concentration). Inspect the three-mesh trend; satisfying these screening limits alone does not establish formal convergence or an error bound.
- Recheck numerical adequacy for cases that change near-ground/source resolution or fail stationarity. Do not apply baseline numerical confidence automatically to S01 or S05.

Exact domain bounds, mesh counts, first-cell treatment, time steps, sampling cadence and solver residual settings must be pinned at setup. Ensure 0.05 m sensor values are represented and interpolated appropriately; an unresolved low sensor is missing coverage, not a zero prediction. No flow calculations occur in this planning task.

## Comparisons and ranking

For every completed case and window, preserve all 30 original sensor row IDs, coordinates, heights and zeros. Use matching concentration basis and report predicted mole/volume percent; verify instrument definitions before treating comparisons as formal validation. Keep reported standard deviations as variability, not uncertainty bounds.

**Sensitivity to assumptions:** first compare each case with S00 at each sensor using W0. Report signed changes, maximum absolute change and RMS change in concentration percentage points. Rank factors by RMS change and show separate height groups so near-ground impacts are visible. For two-sided factors show both cases, not only the larger improvement.

Proposed materiality flag: RMS case-baseline change >max(0.02 percentage points, 10% of baseline-vector RMS). This is a study triage rule only; always show actual changes, flagged or not. Compare this change with measured mesh/time/domain changes. Effects of similar size remain numerically unresolved. Relative per-sensor changes are supplementary only where baseline concentration >=0.05%; show the omitted count and retain every sensor in absolute metrics.

**Comparison with observations:** report MAE, RMSE and mean signed bias (predicted-observed), in concentration percentage points, over the complete eligible set and by height. List missing/invalid predictions and do not improve scores by dropping them; publish a common-sensor comparison if coverage differs. FAC2 is supplementary: for observed O>0, count 0.5<=P/O<=2; P=0 fails, observed-zero rows are excluded and counted separately. No arbitrary epsilon. Display observed-zero predictions as absolute values. No single experimental pass mark is declared.

Compare original arc peaks/widths and vertical profiles as supplementary diagnostics only after matching definitions; do not double-count arc summaries as independent measurements. Any optional contour uses fixed height, threshold, averaging and domain; it is not a measured plume boundary or route clearance.

Use one table per sensor, a case-metric table, sensitivity-by-factor plot and fixed-scale observed/predicted plot. Show the envelope across **this finite set of cases** with an explicit label; do not call it a 95% interval, guaranteed bound or worst-case hazard zone.

## Limited follow-up cases

Do not launch a full factorial sweep. After the core study, two possible interaction checks are:
- S01+S05: ground-touching inlet with weak instability.
- S01+S08: ground-touching inlet with fixed-temperature ground.

Run an interaction only if a component exceeds the materiality rule or the change is comparable to numerical uncertainty requiring clarification. For concentrations, report interaction residual C_AB-C_A-C_B+C_00; no assumption that effects simply add.

If missing turbulence scale or assumed transport coefficients could change the interpretation, a separately versioned follow-up may vary ell to 0.0195/0.078 m or turbulent Schmidt to 0.5/1.0, one factor at a time. These are unmeasured design choices, not calibrated ranges, and are outside the nine core cases. Humidity/phase capability must be resolved first, not deferred as optional parameter tuning.

## Records and execution gates

The [machine-readable study record](../../data/public/eec550-sensitivity-plan.json) is planning metadata, not executable solver input. Every future run must record study version, Git commit, exact solver/package and properties, full assumptions/overrides, evidence hashes, domain/mesh/time controls, mass budget, t_ready, windows, sensor coverage, metrics and failures. Keep large outputs local under ignored outputs/; retain small attributed summaries and provenance after reuse-term review.

Before any run: user instruction to implement/run, thermophysical and humidity review, complete baseline/unstable ABL recipes, buoyancy/turbulence and transport capability checks, and a reviewed numerical setup. If a gate cannot be met, record it and stop dependent cases; never substitute undocumented settings.

S00 remains the primary reference regardless of which case has the lowest RMSE. No fitting to EEC550; no selection of a different assumption at each sensor. Any later calibration must be labelled and separated from evaluation. EEC560 stays excluded from tuning. This study cannot validate tanker discharge, fire, Adoshi terrain or historical plume reconstruction.

## Supporting references

- [SMEDIS evaluation protocol](https://admlc.com/wp-content/uploads/2021/08/smedis_protocol_v2.0.pdf): auditable evaluation, matched output definitions and time-averaged comparisons. The case matrix, numerical tolerances and sensitivity flags here are our choices, not prescribed by that protocol.
- [Foundation 14 k–epsilon reference](https://cpp.openfoam.org/v14/classFoam_1_1RASModels_1_1kEpsilon.html): closure and default Cmu; this does not validate its dense-gas performance.
- Source values and unresolved evidence are documented in the linked input findings.

[Short report](EEC550_SENSITIVITY_SUMMARY.md)
