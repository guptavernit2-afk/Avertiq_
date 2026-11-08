# SMEDIS case selection and data review

Review date: 8 November 2026. Status: dataset selection and test design only. No model predictions, fitting, pass/fail scores or mathematical validation results.

## Scope and evidence

All three version-2.4 ZIP batches were acquired and integrity checked. Their 30 trial workbooks were screened by source/release/terrain/obstacle metadata. A separate terrain-support workbook is not a 31st experiment. All worksheets were parsed read-only with xlrd 2.0.2; the primary three cases received detailed sensor/arc checks.

Original files are under data/raw/2026-11-08/smedis-extracted/ and are ignored by Git. Full measurement tables are not redistributed because broad reuse terms have not been established. The tracked inventory contains paths, identifiers, dimensions and hashes.

Supporting sources: [ADMLC database](https://admlc.com/smedis-dataset/), [variable definitions](https://admlc.com/wp-content/uploads/2020/12/sme9718d-vardef.pdf), [revision history](https://admlc.com/wp-content/uploads/2020/12/sdbrev.pdf), [database paper](https://admlc.com/wp-content/uploads/2020/12/ijep_smedis_2001.pdf), and [evaluation protocol](https://admlc.com/wp-content/uploads/2021/08/smedis_protocol_v2.0.pdf).

The paper's case table (Table 2.3, PDF page 6) and revision page were visually checked. The protocol review was targeted, including Appendix 3 definitions and Appendix 5 FAQs, not a claim to have independently verified every derivation.

## Selected first suite

### EEC550: main initial comparison

Source: batch1/eec550.xls, worksheet Sheet 1.

- Propane: B6. Jet and no fences: B12, B28. Flat surface: B43.
- Source rate: 3 kg/s (B23); release duration: 150 s (B27).
- Wind: 2.73 m/s at 6 m (B33:B34). Version 2.2 corrected the previous value; do not use 3.19.
- Mean-value averaging time: 150 s (B48).
- Concentration observations: A95:E124, 30 rows. Coordinates and receptor height are A:C; mean and temporal standard deviation are D:E, in percent.
- Arc summaries: A89:D92, four rows. These are derived from the measurements and not four additional independent experiments.

Recommended first because it is an unobstructed hydrocarbon field release with useful horizontal/vertical concentration observations and no duplicate coordinate triples found in its concentration block.

### EEC360: smaller-source comparison, with a data issue to resolve

Source: batch1/eec360.xls, worksheet Sheet 1. B2 is numeric 360; preserve this original identifier and map it to the catalogued EEC360.

- Propane: B6. Jet/no fences: B12, B28.
- Rate: 0.11 kg/s (B23); release and averaging durations: 50 s (B27, B48).
- Wind: 3.4 m/s at 3.3 m (B33:B34).
- Concentration observations: A97:E122, 26 rows; arc summaries: A92:D94.
- Rows 97 and 100 have identical X/Y/Z but differing reported mean concentrations. Preserve both original records. Do not merge, choose the larger, or count them as independent without a documented resolution.

Recommended as a lower-rate comparison after its duplicate-coordinate handling is agreed. The duplicate is a review gate, not permission to silently discard inconvenient measurements.

### EEC560: reserved evaluation case

Source: batch3/eec560.xls, worksheet Sheet 1. B2 says EEC56; the archive filename and published case table identify the un-fenced case as EEC560. Keep the alias mapping explicit.

- Propane: B6. Jet/no fences: B7, B23; flat surface: B38.
- Rate: 3 kg/s (B18); release duration: 360 s (B22).
- Wind: 2.43 m/s at 6 m (B28:B29); stability C (B33).
- Averaging time: 100 s (B43), not the release duration.
- Concentration observations: A89:E113, 25 rows; arc summaries: A83:D86.
- Revision 2.3 corrected the arc maximum at 31.9 m; use the supplied revised file.
- Units in several condition labels are incomplete; the wind-direction sensor header incorrectly includes m/s. Resolve units from companion definitions and original records before a run.

Reserve it from future parameter tuning and freeze the handling plan first. We have inspected it for suitability, so this is prospective holdout from fitting, not a blind dataset.

## Other cases

| Cases | Decision and reason |
|---|---|
| PG17 / PG8 | Optional passive-dispersion baseline, not dense-gas validation. SO2, 600 s averaging, sensors at 1.5 m. Check the paper's apparently inconsistent stability wording against each sheet; do not fix the originals. |
| EEC170 | Later propane comparison. Approximate wind and multiple repeated sensor coordinates make it a less clean starter than EEC550. |
| EEC361/362, EEC551, EEC561, EEC171 | Defer until the engine supports fences/obstacles. Use associated un-fenced cases as references but preserve differences in duration and weather. |
| DT1/DT2; FLADIS9/16/24 | Later ammonia/aerosol and atmospheric-regime tests. Different thermodynamics from propylene; require applicable physics. |
| TI08/TI21; LAT49 | Later instantaneous-cloud tests; unsuitable substitutes for the continuous-release suite. |
| DAT638/DAT648 | Later scaled transient slope tests, SF6 and zero listed mean wind. Sheets list 11.6% and 4% slopes. Keep original and scaled columns separate. |
| DAT647 | Defer. File is dat647.xls but B2 says DAT637. Resolve identity and scaled source representation first. |
| DAT231/DAT458/049101/129034; TUV11/13; EMUDJ/EMUNJ | Defer obstacle, confinement and/or complex-terrain configurations and scaling. Do not simplify away defining features and claim to validate them. |

## Source-model choice

There are two distinct comparisons:

1. End-to-end release/aerosol/dispersion: use physically documented nozzle conditions and an applicable source model.
2. Dispersion alone: prescribe the documented equivalent source downstream of vaporisation.

Recommend comparison 2 first. The batch-1 equivsrc.txt provides an equivalent-source table for EEC36/EEC55 families; batch 3 has an EEC560 table. These represent cold gas-air mixtures at a downstream plane, not pure ambient-temperature propane at the damaged nozzle.

Preserve source position, mixture concentration, temperature, momentum and geometry. The batch-1 rectangular-window half-width/height convention differs from the batch-3 radius convention. Confirm family mappings and concentration units before use. Do not run a flashing model again on a post-vaporisation source.

Actual and effective molar weights are different concepts; do not replace physical propane properties with the effective value in a thermodynamic library. Workbook pressure labels and the generic definitions do not always use the same unit. Absolute versus gauge pressure needs confirmation before a source-model comparison.

## Measurement handling

- Treat -999, question marks and blank fields as unavailable/special markers, not physical values. The protocol explicitly uses -999 for unavailable predictions.
- Retain estimated/text-valued inputs as estimates. Do not coerce strings such as decimal commas or approximately-qualified values without recording the interpretation.
- Preserve a genuine listed zero. Detection limits and treatment of near-zero readings need an agreed policy.
- Propane mean_C is percent; Prairie Grass is ppm. Percent LEL is another quantity. Confirm the concentration basis before conversion.
- Phase is defined as a liquid mass fraction before release, despite some sheets calling it a liquid-to-gas ratio.
- Slope percent and tangent/slope-angle definitions require explicit conversion; do not interpret 4 as four degrees.
- Respect the local X-axis orientation and meteorological wind-from convention. Experimental coordinates must not be replaced by Adoshi map coordinates.
- Use the case's experimental weather, never the Adoshi ERA5 series, for these validations.
- Temporal std_C is variability over the averaging interval, not automatically a standard error or confidence interval.

## Planned comparison and gates

Before calculations, agree the engine, capability/domain limits, equivalent-source setup, coordinate transform, averaging window, applicable receptors and exclusions. If a model cannot provide a sensor height or near-source prediction, report missing coverage rather than substituting a different height or zero.

Primary comparisons: mean concentration at each eligible receptor, in matching units and averaging periods. Report per-case bias and absolute-error measures, plus positive-pair concentration ratios/FAC2 where defined. Keep observed-zero and missing-prediction counts visible. Do not invent a small epsilon to make ratios work.

Supplementary comparisons: arc maximum of time-averaged concentration and sigma-y width using the protocol definition. Arc maxima are not necessarily centreline values, and sigma-y is not a full hazardous-cloud width. Do not double-count arc summaries in the pointwise score.

Do not evaluate an instantaneous predicted maximum against a measured time mean. Do not present a modelled threshold contour as a measured plume boundary.

Acceptance thresholds and uncertainty/exclusion rules remain to be agreed with the modeller before running or fitting. Passing these tests would support the tested dispersion regimes only. It would not establish Adoshi reconstruction, tanker blowdown accuracy, tunnel behaviour or propylene terrain performance.

## Next concrete task

The [EEC550 comparison plan](EEC550_COMPARISON_PLAN.md) selects OpenFOAM Foundation 14 conditionally; the [follow-up findings](EEC550_INPUT_RESOLUTION.md) establish axes and clarify timing/weather handling. Original B27=150 s must be retained alongside the conflicting full-trial duration of 360 s; do not treat it as verified total release time. Recover source-window elevation and exact averaging indices before a faithful reproduction. EEC360 duplicate handling and any mentor PHAST benchmark remain separate follow-ups.
