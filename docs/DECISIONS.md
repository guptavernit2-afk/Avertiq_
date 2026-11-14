# Decision log

## 2026-11-08 - Initial planning baseline

- Name: Avertiq.
- Repository: guptavernit2-afk/Avertiq_.
- Keep the original SurakshaMitra prototype separate.
- Work begins with documentation and research; no application code yet.
- First demo: stationary propylene tanker, Adoshi-inspired geography, hypothetical release inputs.
- Separate reported facts, measurements, assumptions and calculated results.
- Show terrain context first; defer terrain-dependent dispersion and tunnel modelling.
- Prepare matched PHAST comparison cases because the mentor may review outputs with Phast. Access, version and modules remain unconfirmed.
- Preserve source provenance, scenario versions, discrepancies and completed work in Git.

## Open decisions

- Exact location and confidence after cross-checking.
- Corridor bounds and map data sources/terms.
- Tank profile and numeric scenario assumptions.
- Source/dispersion model, integration approach and licensing.
- Thresholds, output definitions and assessment period.
- PHAST comparison setup and acceptance criteria.
- Applicable experimental validation cases.
- Application architecture after research and user instruction.

## How to add decisions

Record date, decision, reason, evidence, affected documents and any superseded decision. Do not rewrite history to imply unresolved questions were already settled.

## 2026-11-08 - First data collection and repository boundary

- Use the explicit Avertiq path and verify origin before mutations. Do not work in or delete SurakshaMitra.
- Use current OSM tunnel geometry as a regional sampling anchor only; the accident position is unverified and the way version postdates the incident.
- Collect ERA5 explicitly for reproducibility; preserve returned grid coordinates and do not describe it as on-site wind.
- Commit the small attributed weather response and provenance. Retain large/raw OSM, terrain and experimental files locally with checksums.
- Defer scenario numbers, terrain-dependent predictions and engine selection until evidence/model review.
- Folder detachment from the desktop app is pending user action; no disk folder has been deleted.

## 2026-11-08 - SMEDIS trial selection

- Screen all three version-2.4 batches: 30 trials and one terrain-support workbook.
- Select EEC550 for the first dispersion comparison, EEC360 for the lower-rate comparison after duplicate-coordinate review, and EEC560 as a prospective evaluation case excluded from future tuning.
- Start with the documented downstream gas source when testing dispersion alone. Keep discharge/aerosol physics and terrain validation separate.
- Preserve original units, estimates, missing markers, aliases and measurement records. Reconcile scale, averaging, source geometry and receptor heights before a run.
- Defer complex-terrain and obstacle cases until the model can represent their defining physics. Resolve DAT647/DAT637 identity before using that file.
- No engine selection, application implementation, model execution or accuracy claim was authorized or completed in this review.

## 2026-11-08 - EEC550 local research comparison

- User selected a model we can run ourselves without a paid licence.
- Select OpenFOAM Foundation 14 multicomponentFluid conditionally for the first flat-ground, nonreacting, variable-density mixed-source dispersion comparison. This does not select a production engine.
- Target the documented downstream EEC55 propane-air source, subject to family mapping and geometry/timing review. Do not enter it as a pure-propane SLAB jet: the standard SLAB initialization and temperature restrictions change this source.
- Preserve physical release inputs separately from equivalent mixed inlet inputs; preserve measured and ideal wind as distinct cases.
- Record source/atmosphere/observation lineage and unresolved fields in data/public/eec550-input-plan.json. No invented source-plane height or averaging start.
- Resolve readiness gates and agree numerical/performance criteria before an evaluated run. PHAST remains an optional later external benchmark; EEC560 remains excluded from tuning.
- No installation, model configuration files, application code, simulations or validation results were produced. See research/EEC550_SHORT_PLAN.md and research/EEC550_COMPARISON_PLAN.md.

## 2026-11-08 - EEC550 inlet, timing and atmosphere follow-up

- Acquire four public primary/supporting reports locally with hashes; preserve originals outside tracked data.
- Use original local X east, Y magnetic north, Z up coordinates supported by R582; do not apply unverified declination or Adoshi geography.
- Adopt EEC55 unfenced-to-EEC550 mapping as a strong documented cross-reference inference, not an explicit source-note key.
- Keep actual equivalent-window centre height unknown. Record candidate jet-aligned placement at (2.500,4.330,0.500) m as assumed, with separate geometry sensitivities.
- Correct the fresh 150-second-pulse interpretation: original EEC55 had fenced/unfenced phases; REDIPHEM Table 30 lists 360 s full-release duration on 6 September 1989. Retain conflicting SMEDIS B27=150 s and missing averaging indices.
- Define a conditional developed-plume mean comparison with a 150 s model averaging window after ABL/plume establishment. No historical-window recovery or fence-transition validation claimed.
- Define a simplified neutral atmosphere matched to revised U=2.73 m/s at 6 m and z0=0.006 m; derive neutral u_star rather than forcing estimated 0.190 m/s. Keep estimated L=-90 m as separate consistent sensitivity; thermal/humidity/turbulence details remain open.
- Original REDIPHEM archive redirect is unavailable; no time-series archive obtained and no messages sent. Faithful reproduction remains not run-ready. No coding, installation or simulations.

## 2026-11-08 - EEC550 sensitivity-study design

- User requested planning of a clearly labelled conditional sensitivity study, not coding or execution.
- Record nine core physical cases: baseline; two inlet-height alternatives; source-displacement interpretation; ideal wind; estimated weak instability; two source-turbulence intensities; fixed-temperature versus adiabatic ground.
- Label all unmeasured values and ranges as study assumptions, not observed bounds or probability distributions. Keep documented source state/geometry fixed and preserve historical unknowns.
- Reuse each case for three 150 s model-time averaging windows after prediction-only readiness checks; do not vary 150/360 s release duration to find a better fit.
- Separate numerical verification cases from physical sensitivities. Predeclare proposed internal screening tolerances and materiality rules; no experimental pass mark is asserted.
- Compare every case with S00 and the same sensor records, report coverage/zeros and height-specific results, and do not select a new baseline by best experimental fit. EEC560 remains excluded from tuning.
- Allow only documented targeted follow-up interactions/transport assumptions when indicated; no full factorial sweep planned.
- Thermophysical/humidity suitability, full ABL recipes and numerical setup remain execution gates. No installation, solver configuration, code or simulations produced.

## 2026-11-08 - EEC550 humidity/phase model decision

- Review valid-range NIST propane/water saturation fits and IAPWS ice sublimation relation. Save property-screen arithmetic and reference checks, not a CFD result or rigorous flash.
- At 196 K and assumed downstream pressure 102500 Pa, 20 mol% propane has ideal partial pressure 20500 Pa versus saturation about 15699 Pa. The proposed all-gas source needs thermodynamic reconciliation.
- RH=99% at 283.05 K implies water partial pressure about 1207 Pa. Conditional carryover with 80 mol% ambient wet air gives about 965 Pa water at the inlet versus ice saturation about 0.0869 Pa. This is not an actual measured inlet inventory or phase fraction.
- Do not accept the unmodified gas-only multicomponentFluid configuration as the EEC550 physical baseline. This supersedes its earlier conditional selection; OpenFOAM remains a possible platform, not a selected replacement phase model.
- Hold the nine-case matrix pending source composition/pressure/phase/enthalpy reconciliation. Preserve all original source values and unknowns; do not force feasibility by warming, drying or lowering pressure without evidence.
- Next assess enthalpy-conserving moist phase behaviour and model capability, including water/ice and possible propane phase transfer. Avoid latent-heat double counting. No coding, installation, simulation or claimed physical validation performed.

## 2026-11-08 - EEC550 source-energy specification and local model

- Preserve original window/source records and underdetermined historical inputs. Close two conditional feed-basis component ledgers; do not present assumed entrainment as measured.
- Anchor forward reconstruction to nominal propane 3 kg/s, documented feed/ambient states and explicit pressure/heat assumptions; solve temperature/phase amounts rather than enforcing the rounded 196 K window state.
- Record the original dry ideal-window diagnostic of 3.05450 kg/s propane and the independent mass/area/velocity constraint. No discrepancy is silently renormalized.
- Select a local zero-dimensional constant-pressure homogeneous-equilibrium PH calculation as the next thermodynamic model, using ThermoPack fluid/ice properties. Research source snapshot d68c794c7342bfc6938eb424a1fbb88b7780b738; free Apache-2.0 local distribution documented.
- The reviewed Python PH call is vapour/liquid only; explicit solid-aware phase stability and energy calculation must be implemented and checked later. No ready one-call moist/ice flash or replacement CFD solver claimed.
- Define H00-H04 and component/energy numerical targets; leave equilibrium T, phase split, enthalpy target and energy residual null until coherent properties are evaluated. Do not double-count latent heat or mix enthalpy references.
- Preserve the gas-only rejection and hold on the nine-case dispersion study. No installation, application code or model execution authorized/completed in this research task.

## 2026-11-08 - Standalone equilibrium implementation and verification

- User authorized standalone ThermoPack-based equilibrium implementation, including ice and conservation checks; app and CFD remain out of scope.
- Install ThermoPack 2.2.3, NumPy 2.5.4 and SciPy 1.18.1 in ignored .venv; record runtime/test pins.
- Initial native PR/water-ice Gibbs plus ideal-gas closure failed ice-pressure screening (about 43% low at 196 K). Reject it; retain the adverse check in the verification record.
- Implement a reduced ideal-gas/pure-immiscible-condensate model with native C3 NIST_MEOS and an IAPWS/NIST water saturation Gibbs/enthalpy closure sharing ThermoPack gas references. Native condensed volumes are used for density; no latent-heat double counting. Melting at 273.16 K is an explicit low-pressure approximation.
- Enumerate phase sets and use a PH outer root plus melting lever rule. Verify phase limits, conservation, reference invariance, scale changes, invalid inputs and failure handling. 38 tests and all 34 CLI checkpoints passed; dependency check passed.
- Execute H00-H04 with explicit assumptions. H00 gives about 204.3 K with water ice; H04 at 196 K requires about 496 kW extra heat removal. These are reduced-model conditional results, not measurements or field validation.
- Preserve source unknowns and the hold on the nine CFD cases. No application, CFD, mapping or operational predictions implemented.

## 2026-11-08 - Conditional dispersion handoff

- Review existing H00-H04; no new equilibrium, CFD or app execution. Preserve reported 196 K source and historical inputs.
- Select H00 only as a conditional candidate: about 204.3 K, propane gas and water ice. H01 is a source-basis alternative; H02/H03 diagnostics and H04 nonadiabatic audit do not become automatic CFD cases.
- Preserve 18.1 m/s and derive area from conserved volume flow (0.308458 m²). Record component fluxes, gas basis, bulk density, enthalpy reference, momentum and assumed geometry.
- Prefer a common-velocity/common-temperature HEM research formulation, subject to applicability and capability review. No CFD implementation selected; multiphaseEuler capabilities do not establish an ice-aerosol model.
- Plan conservative H00/ambient mixing and phase-transition checks before coupling. Preserve phase-rate/slip/particle-size limitations.
- Keep S00-S08 as historical v1 on hold; freeze a v2 source/geometry/turbulence recipe before execution. Extend budgets to total water/propane and energy; preserve 30-receptor/150 s policy and holdout.
- Save [full plan](research/EEC550_DISPERSION_HANDOFF.md) and [short report](research/EEC550_DISPERSION_SUMMARY.md). No new field validation or terrain claim.

## 2026-11-08 - Parallel checkpoint bundle and research milestone closure

- User requested clear scope and multiple checkpoints completed together. Parallelize scope documentation, standalone mixing implementation/tests and independent source review; integrate results after review.
- Complete the existing authorized standalone thermodynamic scope; do not expand to app or CFD implementation/runs.
- Freeze the [checkpoint board](PROJECT_CHECKPOINTS.md). Execute 11 H00/ambient PH mixing points, where ratio is added wet-air mass / original H00 total mass. Conserve components and thermal enthalpy; explicitly exclude momentum/kinetic-energy conversion.
- Humidity initially increases ice flow; between sampled ratios 2 and 5 ice disappears and liquid water remains. Liquid water persists at ratio 100. No spatial, temporal or phase-rate inference.
- Expanded suite passed 51 tests. All 16 arithmetic source handoff checks passed; independent review found no material inconsistency. Preserve original source/run records.
- Close this research milestone with results and reproducible commands. Next: bounded phase-bearing dispersion implementation feasibility, rather than another general setup cycle. Nine-case CFD matrix remains held.

## 2026-11-09 - Research workbench v1 implementation batch

- User explicitly requested a substantial parallel implementation chunk, followed by commit/push; retain no app/CFD boundary.
- Deliver reusable study, strict source-contract exports, offline report, verification-gated bundle CLI and Windows/Python 3.13 CI workflow.
- Execute 4 source alternatives x 3 downstream RH settings x 11 ratios (132 states). Downstream RH is an assumed sensitivity, not source-feed or historical weather replacement.
- Adopt normalized closure saturation for the new ambient RH builder. Preserve older raw-fit mixing results and document the reference distinction.
- Export only adiabatic PH sources H00-H03, with 39 passed checks each; reject H04. Keep mixture component/phase/enthalpy/geometry consistency and explicit not-ready-for-CFD status.
- Full local suite: 136 passed; generated bundle/property gate and report-script smoke check passed; dependency check passed. Browser visual QA timed out awaiting app approval.
- Store curated first-party results and exact-byte manifest under data/public/eec550-research-bundle-v1. Next stage is conservative phase-bearing transport, not another source-setup loop.

- Remote verification completed successfully: GitHub Actions run 42552591781 on code commit 5b441d3. Record saved in data/public/eec550-workbench-ci.json; no deployment or CFD run.

## 2026-11-09 - First transport implementation

- User authorized dispersion prototype and parallel checkpoints; no app.
- Select a bounded self-run 1D conservative scalar advection-diffusion implementation as the first numerical transport milestone, not a field-ready dense-gas model.
- Couple mass-specific conserved component/enthalpy interpolation to local PH diagnostics; keep density feedback explicitly excluded.
- 154 package tests passed; execute synthetic pulse and 3-grid analytical Fourier benchmark. Save model decision and numerical evidence.
- Add transport command to CI. Buoyancy, variable-density continuity/momentum, atmospheric domain and receptor comparison remain future gates.

## 2026-11-09 - Variable-density buoyancy implementation

- User authorized variable-density flow/buoyancy, parallel checkpoints, tests and commit/push; no app.
- Implement a bounded 2D variable-density incompressible MAC model with conservative volume fraction, affine frozen-endpoint density, velocity-form advection, gravity and variable-coefficient projection.
- Use H00/ambient densities only as fixed endpoint properties; do not claim evolving PH feedback, conservative momentum/energy or field-ready dense-gas modelling.
- Independent numerical checks caught a tiny-final-timestep bug; fix and add regression coverage. Review projection operators, hydrostatic balance and alpha/mass-fraction distinction.
- Complete 173 passing package tests and 22 independent checks; run endpoint case and 12/24/48 grid comparison. Dense centroid descent approaches about 0.027 m in the specified synthetic 0.25 s experiment.
- Save [results](research/VARIABLE_DENSITY_SUMMARY.md), references and provenance. EEC550 receptor comparison remains held pending thermal/EOS, momentum, atmosphere and boundary work.

## 2026-11-09 - Conservative heat/phase flow coupling

- User authorized thermal/phase feedback, conservative momentum/energy, parallel checkpoints, tests and commit/push; no app.
- Reject a mere isobaric parcel exchange operator as insufficient for spatial flow coupling. Implement a separate 1D compressible conservative prototype with UV thermodynamic closure; do not imply 2D buoyancy integration.
- Invert density/composition/internal energy via bounded pressure root and existing solid-aware PH solver. Preserve energy references and phase latent effects without adding another latent source.
- Transport all five component masses, momentum and total internal-plus-kinetic energy, including pressure work and Fourier conduction. Synthetic conductivity explicitly labelled.
- Independent no-heat control exposed ~492 Pa spurious pressure drift with Rusanov. Replace default with conservative HLLC and verify smooth/sharp stationary contacts. Keep Rusanov as a labelled baseline.
- Complete 210 package tests and 210 independent checks, including TP reconstruction at every final control cell. JSON serialization regression added after CLI caught NumPy booleans.
- Acoustic cell-average pressure RMSE falls across 8/16/32 cells. Save raw first-party outputs and source/runtime provenance. No strong-wave, moving-contact, multidimensional or field-validity claim.
- Next: compatible multidimensional thermal/buoyancy integration and open-domain atmosphere/source verification before EEC550 receptor comparison.

## 2026-11-09 - Integrated 2D thermal, phase and buoyancy flow

- User authorized integration of thermal/phase feedback into 2D buoyancy, parallel checkpoints, tests and commit/push; no app.
- Build a conservative compressible formulation with five component masses, two momentum components and energy including gravitational potential. Retain old frozen-endpoint projection model as a regression baseline.
- Use UV equilibrium closure; gas HLLC face flux plus face potential times mass flux; Fourier heat flux; no duplicate gravity energy source.
- Preserve a canonical analytic isothermal hydrostatic reference through shared-flux correction. Reject arbitrary altered reference arrays rather than freezing an unphysical background.
- Account for corrected wall traction and full gravitational impulse in vertical momentum. Closed-wall component and total-energy budgets remain conservative.
- Complete 232 package tests and 552 independent numerical checks. Nontrivial 1D reduction, axis symmetry and caloric-reference shifts are tested. Strict JSON export passes.
- Save the synthetic 4x4/0.0003-second case, controls and provenance. Gravity-off matched initial pressure is not hydrostatic and is not mislabelled a rest case.
- This closes 2D integration, not field validation. Next: boundaries/atmosphere/source, convergence and scaling before the EEC550 comparison.

## 2026-11-09 - Open atmosphere, source/weather and refinement

- User authorized open atmospheric boundaries, EEC550 source/weather setup, parallel checkpoints, refinement tests and commit/push; no app.
- Extend the coupled solver with ambient inflow, prescribed conservative source patch, extrapolated right/top outflow and ambient-reservoir backflow. Do not claim nonreflecting boundaries or characteristic-compatible source forcing.
- Preserve H00 and original 196 K records separately. Normalize finite source flow by width for a 2D slab; integrate overlap and potential-energy first moment exactly across boundary faces. Separate gross source from displaced ambient and full boundary fluxes.
- Preserve shifted neutral-log convention and raw wind direction. Record along-plane projection/omitted crosswind, pressure-datum excess and inviscid-ground assumptions. Match numerical defaults to the executable case.
- Live-property source compatibility and closed-baseline regressions pass. Full suite: 295 tests; independent open-boundary checks: 283.
- Execute matched .001s studies on 4/8/12 grids and CFL .2/.1/.05 (different actual step counts). Save raw runs and descriptive field/inventory changes.
- Mass inventory agrees; peak fields do not converge. Explicitly flag source underresolution and no sensor-readiness. Next: source-resolving geometry, inlet/outlet/domain and runtime studies before any EEC550 scoring.

- Added a local aperture study at fixed horizontal spacing and matched timesteps. Compare gas propane mol% over a common physical rectangle on both grid families. The vertical result applies to the lower 1.6 m domain at 1 ms.

## First product walkthrough — D-001

- Define one stationary propylene-tanker demo with five screens in the product brief.
- Use explicitly fictional weather and direct-release assumptions, visible missing tanker/phase inputs and an approximate demo location.
- Load prepared illustrative assessment A, then B after a simulated wind update. Preserve both input snapshots and revision history.
- Carry simulation labels through maps, observations and exports; unsupported edits mark a fixture outdated.
- Track product walkthrough acceptance separately from the calculation-validation milestone so both workstreams can progress.
- Update planning documents only. Application implementation remains pending.

## 2026-11-10 - Relevant research collection and website handoff

- User requested remaining relevant research to be collected honestly, committed and pushed before moving to the build. No product implementation is included in this work package.
- User clarified the mentor's focus as LPG, CNG and the Mumbai-Pune incident chemical (reported propylene), including storage and lighter/heavier gas behaviour. Do not invent a fourth selected chemical; preserve the first propylene D-001 walkthrough.
- Add targeted primary-source records SRC-062 through SRC-094 with review/access status. Distinguish full targeted reads, indexed excerpts, discovered-but-unretrieved reports and chemical-specific current values not obtained.
- Specify separate source/dispersion, thermal-radiation, VCE and mechanical-failure branches. Treat terrain rendering separately from terrain-dependent flow. Existing heat/phase code is not a fire-radiation model.
- Preserve conditional propane results and unresolved grid/time/domain/atmospheric/finite-width gates. No EEC550 scores, new hazard distances, new solver runs or newly passed tests are claimed.
- Identify Sandia HyRAM+ as a candidate methane/propane release/flame/selected-overpressure engine; public Python API and GPLv3 identity were reviewed. No installation, pin, execution, complete validation-report review, LPG-mixture/propylene acceptance or terrain capability established.
- Prepare an assessment interface, chemical/storage matrix, source/threshold handling and validation ladder. Reference defaults are not adopted operating thresholds, incident probabilities or Indian regulatory compliance.
- Close bounded literature/design collection for the first fixture-based website. Continue model development/validation through explicit work packages, not another unlimited background-research loop. Commit/push success is verified separately.

## 2026-11-10 - First website dashboard implementation

- User explicitly authorized building the preview dashboard and 3D map while retaining clear demo labels. Update the research-only authorization boundary for D-001; leave solver/prototype code unchanged.
- Use the Sites Vinext starter with a client dashboard, pinned MapLibre 6.17.0, attributed OSM raster roads and Mapterhorn terrain. Retain the previously collected approximate tunnel midpoint; do not claim surveyed accident coordinates.
- Use prepared A/B polygons and fictional place markers, with per-input fixture invalidation and no calculated threshold/distance. LPG/CNG are input options only; no fixture or model support is invented for them.
- Add browser-local state, immutable revision snapshots, synthetic observations, demo reviews and labelled HTML/JSON handover. Public view remains an unpublished visual preview, not access control or an agency notification.
- Seven domain tests, TypeScript and production build passed; browser walkthrough verified terrain, controls, invalidation, revision preservation, observation/export and reload persistence. More specific map-container CSS and a separately served worker repair observed map integration failures.
- Keep Site publishing source isolated under ignored outputs; never repoint the Avertiq GitHub origin or include research raw/private data. Record deployment success separately from creation. See [milestone](WEBSITE_MILESTONE.md).

## 2026-11-10 - Local-first handoff and backend clarification

- User requested localhost rather than the hosted version. Future development/previews are local-only unless publication is explicitly requested; retain the existing Site identity without redeploying it.
- User requested commit/push of the first dashboard and reported that the raw interface does not explain the incident or intended assessment clearly enough.
- Document the current disconnected browser-fixture/Python-research architecture and the proposed incident-to-assessment backend chain in [backend workflow](BACKEND_WORKFLOW.md). No new backend or physics implementation is claimed.
- Recommend one persistent D-001 software slice with an honestly illustrative result adapter, then a separately qualified calculation adapter. Improve the interface explanation alongside that chain rather than adding unexplained map layers.

## 2026-11-11 - Mentor workflow diagrams

- Save the simplified seven-step incident workflow and separate physics diagram in the user's Eraser account. Keep technical backend detail in the existing backend document so the presentation remains readable.
- User requested committing and pushing the workflow to the existing Avertiq GitHub repository. Add versioned Eraser DSL sources, GitHub-rendered Mermaid diagrams, a workflow preview and a short glossary in the [workflow explainer](WORKFLOW_EXPLAINER.md); link it from the README.
- Preserve the distinction between implemented browser-local demo, independent research and planned backend/qualified calculations. No application, solver, dispatch or deployment changes are included.

## 2026-11-11 - First local D-001 backend

- User authorized saved inputs, assessment status and history for one incident while keeping results explicitly demo-labelled.
- Implement local SQLite-backed D1 persistence with a schema migration, server-owned bounded incident aggregate, immutable input snapshots and optimistic version checks. Retain local-only operation; no publication or agency authentication is implied.
- Run the illustrative A/B adapter synchronously with durable queued/running/terminal events. Unsupported inputs return reasons, and interrupted jobs recover to failed after a bounded lease. Keep all physical quantities uncalculated.
- Connect explicit dashboard save/assessment controls, saved revision/job/event history and backend-aware exports. Hide result geometry for unsaved input edits and unavailable/stale/failed/unsupported results. Preserve earlier browser storage without silently importing it.
- See [backend milestone](BACKEND_MILESTONE.md) for verification and limits. Research solvers and the original SurakshaMitra prototype remain unchanged.

## 2026-11-11 - First bounded physics qualification preparation

- User authorized the proposed propylene direct-source input sheet, model applicability review and documented reference reproduction before dashboard integration.
- Freeze an assumed gas-only, ground-level, flat-open-country propylene case and a separate published propane unignited-leak software control. Record comparison tolerances before observing any output. Neither case reconstructs the historical accident.
- Download/install the official EPA ALOHA 5.4.7 reference tool locally and record installer/runtime hashes. Bundled terms restrict DIPPR duplication; keep libraries and raw summaries in ignored local outputs.
- At the initial preparation checkpoint the process had no usable window. This was subsequently resolved with user-authorized launch on 11 November: the archived propane reference reproduced all four preregistered values. Propylene setup was unsaved and its calculation remains pending. See the qualification report; expected values must never substitute for observed results.
- Add six passing evidence-tool tests and input arithmetic checks in [standalone qualification](../research/dispersion/README.md). These do not validate dispersion. Leave the dashboard/backend's illustrative adapter unchanged; see [applicability gates](research/FIRST_PHYSICS_QUALIFICATION.md).

## 2026-11-14 - Local backend plan closeout

- Completed the authorized validation, retry, recovery, export and local backup/restore work, followed by fresh CLI verification and a [mentor/developer handoff](BACKEND_HANDOFF_2026-11-14.md).
- Preserve the single-incident illustrative scope. Browser acceptance and live restore promotion were not performed; physics qualification remains open. No computer-control tools or scheduled runs are authorized during this work.

## 2026-11-14 - Propylene preparation without computer control

- User authorized input mapping, reproducible cases, result checks, tests and push, with model results pending.
- Preserve frozen v1 and add four v2 unrun cases. Separate Direct Source mass-rate entries from unverified source/ground thermodynamic assumptions; retain the earlier observed location-minute precision.
- Gate future record inspection on exact case/engine/input identity, units, output semantics, source consistency and hashed local evidence. Retain unavailable outputs and warnings; withhold mixed-method/basis comparisons. Checks never enable the dashboard or qualify physical accuracy. See [preparation](research/PROPYLENE_PREPARATION.md).

## 2026-11-14 - Separate equilibrium plausibility from model applicability

- Add an independent NIST-based screen for the declared pure propylene state without altering frozen inputs. Do not extrapolate the published low-temperature Antoine fit to ambient temperature.
- Keep actual tanker discharge state and installed ALOHA source thermodynamics unresolved. Passing this screen never enables result acceptance or dashboard physics. See [state review](research/PROPYLENE_SOURCE_STATE.md).

## 2026-11-14 - ALOHA Direct Source treatment investigation

- Record partial compatibility of the prescribed airborne-gas input contract; keep internal temperature, pressure, vapour fraction and enthalpy unknown. Do not infer these from storage conversion fields, warnings, mass totals or map polygons.
- Reviewed the official mapping/weather and pass-file specifications without invoking ALOHA or its DLL. They do not establish a complete headless execution or source-state inspection route.
- Add source-treatment checks and provenance to research reports, preserving frozen cases and all qualification gates. See [investigation and next evidence](research/ALOHA_DIRECT_SOURCE_REVIEW.md).

## 2026-11-14 - Preserve future propylene run evidence locally

- Add a private archive/verification CLI for the qualification plan's evidence-retention step. Preserve original observations and raw bytes with frozen inputs, inspection and review provenance; reject incomplete records and existing output paths.
- Reinspect only when current case/configuration/checking-code provenance matches. Otherwise distinguish byte integrity from pending reinspection. All physics acceptance and dashboard gates remain closed.
- Test only with disposable synthetic archives, including interrupted writes and changed evidence. Raw archives use an ignored suffix and remain local. See [workflow and limitations](research/PROPYLENE_EVIDENCE_ARCHIVE.md).

## 2026-11-14 - Define and guard propylene output meaning

- Review installed 5.4.7 output help and NOAA's concentration graph explanation. Adopt reported outdoor maxima of averaged concentrations over the first hour for this scalar receptor suite; keep exact averaging unresolved.
- Add an unconfirmed structured supplement without modifying frozen case inputs or existing unrun observations. Withhold comparisons for legacy records without the supplement; reject incompatible or contradictory declared meanings.
- Retain raw-evidence references and include semantics dependencies in archive provenance. No metadata check closes physical qualification or enables the dashboard. See [output interpretation and capture policy](research/PROPYLENE_OUTPUT_SEMANTICS.md).
