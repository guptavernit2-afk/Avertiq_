# Data plan

## Public evidence to collect

| Data | Candidate source | Required handling |
|---|---|---|
| Incident chronology and reported quantities | TOI and Indian Express reports in source register | Attribute claims; record conflicting times; do not infer a continuous leak history |
| Chemical properties | NOAA CAMEO propylene entry; selected engine's documented property source | Record chemical identity, units, reference conditions, and source/version differences |
| Roads and tunnel entrances | OpenStreetMap candidate, cross-checked with imagery and reporting | Check completeness, attribution and terms; confirm the incident pin separately |
| Elevation | Copernicus GLO-30 | Record tile/release, horizontal and vertical references, surface-model limitations, attribution and terms |
| Weather, 3-5 February 2026 | Open-Meteo archive candidate | Record selected underlying dataset, grid resolution, measurement heights, hourly times and Asia/Kolkata conversion |
| Experimental measurements | Applicable SMEDIS trials | Review original conditions, units, availability and terms before selecting validation cases |

Archived gridded weather is not a station observation at the tanker. A public map location is not proof of the exact accident coordinates.

## Hypothetical demo inputs

Tank dimensions, filling, internal conditions, opening geometry, release phase/duration, telemetry, detector observations, team availability, and operational updates will be synthetic unless evidence establishes otherwise.

Choose mutually consistent quantities; pressure and temperature for liquefied propylene cannot be varied arbitrarily. Have a qualified modeller review the assumptions.

The reported total loss of approximately three tonnes is background, not a measured release-rate curve. Do not tune a model to a news claim about detector readings without the underlying measurements.

## Provenance fields

For each dataset or input retain: identifier, value/unit or path, source URL, retrieved date, observation time if applicable, location/reference system, evidence status, synthetic flag, uncertainty/limitations, licence/redistribution terms, and transformation history.

## Storage

- data/source-register.csv: small version-controlled discovery and provenance register.
- data/raw/: original external files, ignored by Git.
- data/processed/: derived files, ignored until a deliberate publication decision.
- data/private/: partner data, ignored; no such data is currently available.

Commit small redistributable fixtures only after review. Never commit proprietary PHAST databases or reports without permission.

## Collection status

First collection completed on 8 November 2026: 72 hourly ERA5 records; current OSM tunnel feature; one GLO-30 terrain tile; and one SMEDIS experimental archive (subsequently expanded and reviewed). The source register and data/public manifests record status and provenance. No verified accident coordinates, full road-network extract, real tanker record, field gas measurements, or physics results are available. See [research summary](research/2026-11-08-summary.md).

SMEDIS follow-up: all three batches are now collected and header-screened; see [shortlist](research/SMEDIS_SHORTLIST.md). Case suitability and data issues were reviewed, but no predictions or experimental validation scores were computed.
