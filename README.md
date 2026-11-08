# Avertiq

Chemical transport incident assessment.

**Current stage:** standalone thermodynamic research implemented and numerically verified. No application or CFD has been implemented.

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

Start with the [short collection report](docs/research/2026-11-08-summary.md). Public weather data is tracked; larger raw terrain/map/experimental assets remain local with source URLs and checksums. Conditional thermodynamic results are available below; no dispersion results exist.

## Validation cases selected

Read the [short SMEDIS review](docs/research/SMEDIS_SHORTLIST.md): EEC550 first, EEC360 after duplicate-record review, and EEC560 reserved from future tuning. These are propane analogues, not validation of Adoshi. No dispersion model has been run.

## Standalone equilibrium calculation

Read the [short implementation report](docs/research/EEC550_EQUILIBRIUM_SUMMARY.md). The [research package](research/equilibrium/README.md) runs locally with ThermoPack 2.2.3 and an explicit reference-saturation water/ice closure. It passed 38 tests and 34 property/numerical checkpoints. Results are conditional source studies, not experimental validation.

The primary assumed case gives about 204.3 K with water ice. The original gas-only baseline remains unaccepted and the nine-case CFD study remains held pending review. Run instructions, dependency pins, source/native-library hashes and results are recorded in the repo. No app or CFD work was performed.

## Demo flow

Open incident -> confirm cargo and location -> select documented release assumptions -> review a hazard estimate -> inspect roads and terrain -> add simulated observations -> revise assessment -> export handover.

Every important value must include its unit, source, timestamp, and evidence status: measured, reported, assumed, or unavailable. Simulated data must also carry a synthetic-data flag.

## Project records

Keep each reviewed decision and completed milestone in Git. Record what changed, why, supporting evidence, validation performed, and unresolved questions. Small, meaningful commits are preferred.

The previous [SurakshaMitra prototype](https://github.com/guptavernit2-afk/SurakshaMitra) remains a separate project. Its existing equations are not accepted as validated models for this demo.

Initial planning baseline: 8 November 2026.

## Source-to-dispersion plan

The [short handoff decision](docs/research/EEC550_DISPERSION_SUMMARY.md) selects H00 as a conditional phase-bearing candidate and preserves the original equivalent source separately. Warm-air mixing checks and an implementation audit come next; the nine-case study remains held. No CFD solver has been selected or run.
