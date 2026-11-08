# Geographic anchor, terrain and weather

## Tunnel anchor: mapped feature, not accident position

Primary download: [OpenStreetMap way 42680772](https://api.openstreetmap.org/api/0.6/way/42680772/full) (SRC-013).

The current feature is tagged Adoshi Tunnel. Version 12 was edited on 19 February 2026, after the incident. It has two control nodes; this is not surveyed tunnel geometry.

Bounding-box centre, used only to request regional weather: 18.76449685 N, 73.3465372 E. The reported tanker incident position relative to either entrance remains unverified.

No historical road alignment, speed restriction, closure extent, settlement inventory or full road-network extract has been verified. Do not interpret current OSM tags as conditions on 3 February.

## Historical weather

[Open-Meteo archive documentation](https://open-meteo.com/en/docs/historical-weather-api) (SRC-006).

Collected ERA5 explicitly, rather than the provider's automatic model selection. Period: 3 February 00:00 through 5 February 23:00, Asia/Kolkata; 72 hourly records. Variables: 2 m temperature/humidity, 10 m wind speed/direction, cloud cover and surface pressure.

Requested coordinates are the tunnel anchor above. Returned grid coordinates: 18.75 N, 73.25 E. The approximately 0.25-degree source grid is regional context; the returned point is approximately 10 km from the anchor.

All requested values were present. That checks completeness, not local accuracy. No on-site station series or measured valley wind was obtained. The news description of favourable winds cannot be confirmed or rejected using this grid alone.

See the exact request, units, offset, checksum and limitations in [weather metadata](../../data/public/weather-era5-2026-02-03_05.metadata.json).

## Terrain

Downloaded the [GLO-30 N18 E073 tile](https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N18_00_E073_00_DEM/Copernicus_DSM_COG_10_N18_00_E073_00_DEM.tif) from the public AWS distribution (SRC-014).

File is 3600 x 3600, float32, with one-arc-second spacing and WGS84 horizontal georeferencing. The source product documents EGM2008 heights in metres; that vertical reference is not explicitly encoded in this file's inspected GeoKeys.

The AWS registry describes a 2021 release distribution. Acquisition predates the 2026 incident; current road-cut details cannot be assumed. Header/georeferencing and checksum were checked; no terrain clipping, slope analysis or gas-flow calculation has been performed.

Use it for landscape context. The surface includes structures and vegetation and cannot resolve tunnel interiors or small drains/barriers.

## References and rights

[OpenStreetMap copyright](https://www.openstreetmap.org/copyright), [Open-Meteo licence](https://open-meteo.com/en/licence), [Copernicus specifications](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM), [AWS distribution](https://registry.opendata.aws/copernicus-dem/).

See [data attribution](../../data/public/README.md). Raw OSM and terrain files remain local and ignored by Git.
