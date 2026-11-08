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
