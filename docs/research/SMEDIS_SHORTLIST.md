# SMEDIS review: short report

**Recommendation:** begin with propane dispersion experiments, using documented source conditions. No model has been run and no accuracy claim is made.

| Case | Use | Important condition |
|---|---|---|
| EEC550 | First main test: unobstructed propane jet | 30 concentration records; use corrected wind speed and 150-second averaging |
| EEC360 | Smaller-release comparison | 26 records, including an unresolved duplicate-coordinate pair |
| EEC560 | Reserve for evaluation after setup choices are frozen | 25 records; 100-second averaging despite a 360-second release |

These trials are useful physical analogues, not propylene or Adoshi ground truth.

## Test approach

First compare concentration at the actual sensor coordinates/heights using the documented downstream gas source. Separately evaluate any future liquid-discharge/aerosol model. Do not count the same physics twice.

Use per-case absolute errors, bias and positive-pair ratio statistics. Keep zeros and missing values distinct. Freeze unit handling, exclusions, averaging definitions and acceptance criteria before running predictions.

## Terrain later

DAT638/DAT648 are candidate scaled slope tests. They need a suitable transient terrain model and consistent scaling. They do not establish accuracy for the Adoshi valleys. DAT647 additionally has a filename/header identity conflict.

## Work completed

Screened 30 trial headers and one terrain-support workbook across all three batches. Inspected the three core cases in detail and checked variable definitions, revisions and relevant protocol sections. Raw files remain unchanged and local.

[Detailed findings and cell references](SMEDIS_REVIEW.md) | [Case inventory](../../data/public/smedis-case-inventory.json)

Next: agree the source representation and case-handling rules with the modeller/mentor before implementing the engine.
