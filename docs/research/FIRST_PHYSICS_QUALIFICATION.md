# First physics qualification: propylene direct-source screening

11 November 2026. User authorized defining one explicit propylene case, reviewing a model and reproducing one documented reference before dashboard integration. This record describes completed preparation and open gates; the separate propane software control has now been reproduced; propylene remains pending.

## Bounded decision

Select **ALOHA 5.4.7 for supervised desktop qualification**, subject to the checks below. NOAA documents direct airborne sources and Gaussian/heavy-gas dispersion. The [official EPA download](https://www.epa.gov/cameo/aloha-software) provides this Windows version, but lists supported systems only through Windows 10. Successful operation on the current machine must be demonstrated; installation alone is insufficient.

The [technical reference](https://response.restoration.noaa.gov/sites/default/files/ALOHA_Tech_Doc.pdf), section 3.2, supports directly specified airborne releases. Its edition is 5.4.4 (2013), distinct from the installed 5.4.7 executable. [NOAA's limitations](https://response.restoration.noaa.gov/oil-and-chemical-spills/chemical-spills/response-tools/alohas-limitations.html) exclude terrain steering and arbitrary mixtures. These limitations fit an explicitly idealized flat-ground pure-species study, not the real valley accident.

HyRAM+ is not selected for this propylene case: its reviewed methane/propane support does not establish propylene applicability. PHAST is not assumed available. The current custom flow prototype is not substituted for a developed atmospheric plume.

## Input sheet and reference

The versioned [propylene input sheet](../../research/dispersion/cases/propylene-direct-v1.json) declares a post-release gas source rather than deriving a tanker leak. It includes source/environment conditions, wind measurement height, stability, surface assumptions, receptor heights and requested output basis. Its diagnostic contour levels have no health/evacuation authority.

The independent [propane reference control](../../research/dispersion/cases/aloha-reference-propane-v1.json) comes from [NOAA/EPA Example 2, Part 2](https://response.restoration.noaa.gov/sites/default/files/ALOHA_Examples.pdf), September 2016. It checks the installed tool/settings against a published fictional scenario. It is not measured experimental evidence or a qualification of propylene source physics. Comparisons must match the prescribed settings and output units; retain mismatches rather than tuning inputs to match the answer.

## Gates before a propylene result is accepted

1. Confirm the actual running version and exact propylene identity/CAS in the installed model.
2. Reproduce the separate published software reference using the predeclared tolerances and archive observed evidence. Do not fill observed values from the published answers.
3. Check that ALOHA's direct-source temperature/phase and momentum assumptions represent the declared gas-only source. Its bundled Direct Source help warns that sparse direct inputs do not necessarily resolve two-phase behaviour. A warning does not establish a physical phase model. If the source cannot be mapped consistently, reject or explicitly revise the proposed case before running it.
4. Record which dispersion method ALOHA actually selects, output height/time/averaging semantics, near-source limits, source duration and any warnings. Do not force a simple molecular-weight light/heavy switch.
5. Run the propylene baseline and independently labelled source-rate/wind sensitivity cases; inspect source mass and output consistency. Keep rate/duration assumptions distinct from real tanker measurements.
6. Export permitted calculated quantities with engine/input/evidence hashes. For an initial result, use declared locations/height/time basis; produce map contours only if the exported spatial output supports them. No hand-shaped calculated polygon or made-up time animation.

Only after these gates pass should an adapter be considered. Its evidence label would be **Calculated research result — not field validated**. Public notices and operational decisions remain outside this milestone.

## Completed preparation and limitations

The official installer and model files have been hashed in the [engine manifest](../../research/dispersion/engine-manifest.json). The runtime and bundled help are local under ignored outputs. A reference comparison CLI and six passing synthetic tool tests are in the [qualification package](../../research/dispersion/README.md). They reject wrong versions, changed case identities, missing/raw-evidence hash mismatches, incomplete numbers and declared synthetic runs. They do not establish any model's physical accuracy.

After user-authorized desktop launch, the propane reference reproduced all four preregistered values on 11 November 2026: 26 minutes, 5,730 lb/min, 166 yards red and 474 yards yellow. ALOHA selected Heavy Gas. The public reference-comparison.json records observed values and local evidence hashes. This is software reproduction only. Propylene setup was paused and not saved; no propylene result exists. Before restarting, record the location minute rounding and resolve direct-source temperature/phase mapping in a new case version. The existing local dashboard/backend is unchanged and continues to use illustrative A/B fixtures.

The bundled ALOHA terms restrict duplication of DIPPR data and include third-party endpoint material. Do not commit/rehost the installer, chemical library or unreviewed full Text Summary exports. No headless execution API, hosted deployment entitlement, chemical-mixture validation or local terrain capability has been established.

## CLI-only preparation milestone — 14 November 2026

See [propylene preparation](PROPYLENE_PREPARATION.md) for the v2 baseline and three sensitivity cases, documented input mapping and future observed-record checks. Rate/duration/weather entry mapping is documented; source-temperature/pressure/phase behaviour remains an explicit applicability gate. No propylene model run or result is claimed. The v1 sheets are preserved.
