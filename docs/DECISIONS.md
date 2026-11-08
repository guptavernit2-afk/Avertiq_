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
