# Public-data collection ledger

Collection date: 8 November 2026. This directory contains provenance and a small redistributable weather response. It contains no live tanker data or hazard predictions.

| Asset | Location | Git status | Checks completed |
|---|---|---|---|
| ERA5 hourly response | weather-era5-2026-02-03_05.json | Tracked | 72 unique consecutive local hours; six complete variables; unit/range checks |
| Weather provenance | weather-era5-2026-02-03_05.metadata.json | Tracked | Exact URL, requested/returned coordinates, units and SHA-256 |
| OSM tunnel provenance | tunnel-anchor.metadata.json | Tracked | Current mapped feature identified; not verified accident coordinates |
| OSM XML | ../raw/2026-11-08/osm-way-42680772.osm | Ignored local file | XML parsed; two referenced nodes present |
| Terrain TIFF | ../raw/2026-11-08/terrain-glo30-N18-E073.tif | Ignored local file | TIFF header, dimensions, float type, georeferencing and SHA-256 |
| SMEDIS batch 1 | ../raw/2026-11-08/smedis-batch1_24.zip | Ignored local file | ZIP integrity and member listing; trial headers screened; no model runs |

[External download manifest](external-download-manifest.json) records exact URLs, sizes and checksums. A fresh clone will not contain ignored raw files. Download from those URLs into the listed paths and compare checksums before use; do not overwrite an existing different file without review.

## Attribution and reuse

Weather data by [Open-Meteo.com](https://open-meteo.com/), using ERA5 from Copernicus Climate Change Service / ECMWF. API data: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) per [provider licence](https://open-meteo.com/en/licence). The committed API response is unmodified; companion metadata and notes were added. Provider interpolation/elevation processing is retained. API access conditions are separate from data reuse; reassess the service plan before commercial deployment.

Tunnel coordinate metadata derives from OpenStreetMap. Copyright OpenStreetMap contributors; available under [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/) and [OSM attribution requirements](https://www.openstreetmap.org/copyright). Geometry remains local; coordinate metadata is provided with that attribution.

Copernicus DEM notice:
Â© DLR e.V. 2010-2014 and Â© Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.

[Copernicus licensing/citation guidance](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM). Tile unchanged and retained locally; any later modification requires the applicable modified-data attribution.

SMEDIS archive: provided through [ADMLC](https://admlc.com/smedis-dataset/). No broad redistribution licence has been established in this collection; retain locally pending terms/applicability review. All three batches have now been inspected for suitability. No predictions have been compared with experimental measurements.

News articles and photos are not included. Source URLs and short attributed factual notes are retained.

## SMEDIS follow-up

[Case inventory](smedis-case-inventory.json) records 30 trials plus one terrain-support workbook, their original IDs/aliases, source hashes and review depth. Batches 2/3 and four supporting PDFs remain in the ignored raw directory; their URLs and checksums are in the external manifest. The [short review](../../docs/research/SMEDIS_SHORTLIST.md) links to case-level findings. Originals remain unchanged; no spreadsheet was authored and no physics engine was run.

## EEC550 input preparation

The [input plan](eec550-input-plan.json) records original workbook cells, equivalent-source provenance, observation ranges and unresolved gates. It is not a runnable solver configuration or a prediction dataset. Full concentration records remain in the unchanged local workbook pending reuse-term review. The SLAB manual was downloaded locally and its checksum added to the external manifest after a targeted input-capability review. See the [short comparison plan](../../docs/research/EEC550_SHORT_PLAN.md). No model has been installed or run.

## EEC550 input follow-up

The structured input record is now schema version 2. It retains original values while recording the magnetic-north coordinate evidence, source-placement assumptions, full-trial/SMEDIS duration discrepancy, conditional stationary averaging policy and simplified neutral-weather plan. Four supporting reports were acquired locally and added to the manifest. The original REDIPHEM time-series link returns an unavailable-download page; no archive was acquired. [Review findings](../../docs/research/EEC550_INPUT_RESOLUTION.md). No model was run.

## EEC550 sensitivity design

[eec550-sensitivity-plan.json](eec550-sensitivity-plan.json) records nine planned physical cases, assumed baseline values, three averaging windows, proposed numerical screening and output-comparison rules. It is planning metadata, not executable solver configuration. Numerical controls are additional to the nine cases. Historical unknowns remain null in the input lineage. No predictions or results are included.

## Humidity and phase screen

[eec550-phase-screen.json](eec550-phase-screen.json) records valid-range property correlations, ideal partial-pressure checks and limitations. It is neither a rigorous equilibrium flash nor a CFD output. NIST HTML snapshots and the IAPWS reference PDF remain local with manifest hashes. The current gas-only baseline is not accepted; the input and sensitivity records point to this superseding decision. [Short review](../../docs/research/EEC550_PHASE_SUMMARY.md).

## Source-energy specification

[eec550-source-energy-plan.json](eec550-source-energy-plan.json) contains conditional component ledgers, energy equations, unsolved state fields, H00-H04 and the next-model decision. It is planning metadata, not executable input or a flash result. Pinned ThermoPack reference snapshots are ignored locally with manifest hashes; no downloaded source was installed or executed. [Short report](../../docs/research/EEC550_SOURCE_ENERGY_SUMMARY.md).

## Implemented equilibrium results

[eec550-equilibrium-results.json](eec550-equilibrium-results.json) and [verification](eec550-equilibrium-verification.json) now record executed conditional 0D cases and numerical/property checks. They are distinct from the earlier planning records above and do not validate source reconstruction or dispersion. Native-library and normalized source hashes are included. Large/local output remains ignored; small first-party result records are tracked. [Short report](../../docs/research/EEC550_EQUILIBRIUM_SUMMARY.md).

## Conditional dispersion handoff

[eec550-dispersion-handoff.json](eec550-dispersion-handoff.json) derives an H00 boundary ledger from existing equilibrium results and records their normalized-text hash. It preserves gas/ice mass, enthalpy and velocity/area consistency. This is planning metadata, not solver configuration. Original source values and historical sensitivity matrix remain preserved; implementation/execution gates are explicit. [Short decision](../../docs/research/EEC550_DISPERSION_SUMMARY.md). No new equilibrium or CFD run.

## Executed mixing milestone and handoff checks

[eec550-mixing-results.json](eec550-mixing-results.json) contains 11 executed conditional 0D H00/ambient thermal-enthalpy equilibrium states, with provenance. It is not CFD or a plume prediction. [eec550-handoff-checks.json](eec550-handoff-checks.json) records 16 passed arithmetic boundary checks; these are not physical validation. [Milestone report](../../docs/research/EEC550_MIXING_MILESTONE.md).

## Research workbench bundle v1

[eec550-research-bundle-v1](eec550-research-bundle-v1/report.html) contains the executed 132-state study, four v2 source contracts with audits, property verification, offline HTML and exact-byte checksums. These are first-party research outputs, not external measurement data or CFD predictions. LF rules preserve manifest hashes across Git checkouts. [Milestone and interpretation](../../docs/research/WORKBENCH_V1.md).

## First transport prototype

[transport-prototype-v1](transport-prototype-v1/transport.json) contains a synthetic periodic pulse result and Fourier grid-refinement evidence. These are numerical verification outputs, not measurements or EEC550 predictions.

## Variable-density flow v1

[variable-density-flow-v1](variable-density-flow-v1/flow.json) contains the synthetic 2D endpoint-density flow, 22 independent checks and a three-grid comparison. These are computed hydrodynamic verification cases, not experimental measurements or EEC550 field predictions. [Interpretation](../../docs/research/VARIABLE_DENSITY_SUMMARY.md).

## Conservative thermal/phase flow v1

[thermal-phase-flow-v1](thermal-phase-flow-v1/flow.json) contains the executed 1D coupled flow, controls/210 checks and an analytical acoustic grid comparison. These are first-party synthetic numerical results, not industrial measurements or EEC550 predictions. [Interpretation](../../docs/research/THERMAL_PHASE_SUMMARY.md).

## Integrated thermal 2D v1

[integrated-thermal2d-v1](integrated-thermal2d-v1/flow.json) contains the executed 4x4 heat/phase/gravity case and 552 independent numerical checks with controls. These are first-party synthetic research outputs, not industrial measurements or EEC550 predictions. [Interpretation](../../docs/research/THERMAL_2D_SUMMARY.md).

## EEC550 open-atmosphere v1

[eec550-open-atmosphere-v1](eec550-open-atmosphere-v1/case.json) contains the conditional setup, short open-domain run, independent boundary controls and raw grid/time studies. These first-party synthetic results explicitly flag unresolved spatial convergence. They are not experimental measurements, sensor scores or a 150-second release prediction. [Interpretation](../../docs/research/OPEN_ATMOSPHERE_SUMMARY.md).
