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
