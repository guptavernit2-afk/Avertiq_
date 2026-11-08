# Avertiq

Chemical transport incident assessment.

**Current stage:** planning and research. No application or physics engine has been implemented.

Avertiq starts with an **Adoshi-inspired training demo**: one stationary propylene tanker, real geographic context, and explicitly hypothetical release conditions. It does not reconstruct the historical gas cloud or provide operational clearance decisions.

## Read first

- [One-page roadmap](docs/ROADMAP.md)
- [Demo scope](docs/DEMO_SCOPE.md)
- [Data collection plan](docs/DATA_PLAN.md)
- [Scenario definitions](docs/SCENARIOS.md)
- [Mathematics and validation](docs/VALIDATION.md)
- [Decision history](docs/DECISIONS.md)
- [Source register](data/source-register.csv)

## Research collected

Start with the [short collection report](docs/research/2026-11-08-summary.md). Public weather data is tracked; larger raw terrain/map/experimental assets remain local with source URLs and checksums. No model results exist yet.

## Validation cases selected

Read the [short SMEDIS review](docs/research/SMEDIS_SHORTLIST.md): EEC550 first, EEC360 after duplicate-record review, and EEC560 reserved from future tuning. These are propane analogues, not validation of Adoshi. No model has been run.

## Demo flow

Open incident -> confirm cargo and location -> select documented release assumptions -> review a hazard estimate -> inspect roads and terrain -> add simulated observations -> revise assessment -> export handover.

Every important value must include its unit, source, timestamp, and evidence status: measured, reported, assumed, or unavailable. Simulated data must also carry a synthetic-data flag.

## Project records

Keep each reviewed decision and completed milestone in Git. Record what changed, why, supporting evidence, validation performed, and unresolved questions. Small, meaningful commits are preferred.

The previous [SurakshaMitra prototype](https://github.com/guptavernit2-afk/SurakshaMitra) remains a separate project. Its existing equations are not accepted as validated models for this demo.

Initial planning baseline: 8 November 2026.
