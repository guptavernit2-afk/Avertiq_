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
