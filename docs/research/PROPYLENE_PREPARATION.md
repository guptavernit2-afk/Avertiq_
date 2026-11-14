# Propylene preparation milestone

14 November 2026. This package prepares four assumed cases and checks future manually transcribed model records. No propylene model has been run. Source/phase applicability and output semantics remain open; passing record checks cannot enable dashboard physics.

## Input mapping decision

The installed ALOHA 5.4.7 help was read from disk without launching the application. Sources are `AlohaHelp/Source/DirectSource/Direct_Source.htm`, `Direct_Source_Inputs.htm`, `Atmospheric/User_Input/Ground_Roughness.htm`, and `Reference/DispersionModeling/Heavy_Gas_Dispersion.htm` under the ignored installation. Their hashes are in [mapping evidence](../../research/dispersion/mapping-evidence.json). Existing source-register entries SRC-095–097 cover the software, reference and bundled help. Raw property tables are not redistributed.

| Declared quantity | Entry / treatment | Status |
|---|---|---|
| Pure propylene, CAS 115-07-1 | Select exact chemical; retain observed identity | Candidate selected by the user previously, but setup/evidence not saved; reconfirm |
| Airborne gas rate | Direct source, continuous, kilograms per second | Documented input; this bypasses tank-release calculation |
| Duration 600 s | Enter 10 minutes even though the rate is per second | Unit mapping resolved |
| Source height 0 m | Ground-level entry | Documented input |
| Wind 2 or 4 m/s, from 270 degrees, measured at 10 m | Atmospheric fields; wind travels eastward | Explicit synthetic assumptions |
| Air 25 C, humidity 50%, cloud 10/10, stability D, no inversion | Atmospheric fields | Verify saved summary when run |
| Open Country | Categorical roughness selection | Numeric effective roughness remains unverified; do not invent a z0 |
| Source temperature 298.15 K and pressure 101325 Pa | Retained scenario assumptions, absent from mass-rate Direct Source entry | NOT proven applied by the model; applicability remains open |
| Gas-only/no droplets; no source momentum | Declared idealization | Direct Source can warn about phase ambiguity; warnings must be retained and reviewed |
| Ground temperature 298.15 K | Retained idealization, not a verified direct-source field | Mapping remains open |
| Site/date | 18 deg 45.8 min N, 73 deg 20.7 min E; elevation 0 m; 11 Nov 2026 12:00 IST | v2 uses earlier observed UI minute precision, not full v1 coordinates; approximate fictional anchor |
| Requested receptors | 50/100/200/500 m downwind, crosswind 0, ground level, gas-volume ppm | Capture model-specific availability and exact output basis; never infer missing values |
| Diagnostic levels | 1000/100/10 ppm in the concentration display | Numerical diagnostics only; no health, evacuation or flammability authority |

**The source-temperature/phase question is not resolved by changing to volume units.** Bundled help describes the extra storage fields in volume mode as inputs to a volume-to-mass conversion. That does not demonstrate control of cloud thermodynamics. Keep the specified mass rate. Before accepting predictions, document installed-model behaviour and its compatibility with the assumptions, or create a new case version. Do not silently substitute a tank model, flashing release or propane.

The [NOAA technical documentation](https://response.restoration.noaa.gov/sites/default/files/ALOHA_Tech_Doc.pdf) is version 5.4.4, distinct from installed 5.4.7. Section 3.2 describes a prescribed vapour source. Section 4.4.1 describes automatic selection using a Richardson-number criterion: record the chosen method rather than forcing a molecular-weight rule. Sections 4.4.4 and 4.5 distinguish averaging and time-envelope concepts. For these cases request the concentration display consistently; do not compare it with flammable-cloud outputs or describe its maximum as an instantaneous concentration. Confirm actual installed semantics in the observed record.

## Frozen v2 suite

The [original v1 sheet](../../research/dispersion/cases/propylene-direct-v1.json) is unchanged. v2 separates actual UI entries from unresolved assumptions and versions the site precision before any outputs exist. The original historical date remains fixed for reproducibility. Each file has a canonical JSON hash and parent/reference identifiers.

| Case | Rate kg/s | Duration min | Wind m/s | Integrated source mass kg (arithmetic only) |
|---|---:|---:|---:|---:|
| [baseline](../../research/dispersion/cases/propylene-v2/baseline.json) | 0.1 | 10 | 2 | 60 |
| [rate-half](../../research/dispersion/cases/propylene-v2/rate-half.json) | 0.05 | 10 | 2 | 30 |
| [rate-double](../../research/dispersion/cases/propylene-v2/rate-double.json) | 0.2 | 10 | 2 | 120 |
| [wind-higher](../../research/dispersion/cases/propylene-v2/wind-higher.json) | 0.1 | 10 | 4 | 60 |

Variations are independent runs with one physical input changed. The [preparation report](../../data/public/dispersion-qualification-v1/propylene-preparation.json) contains hashes and arithmetic, no concentrations/distances. Separate propane reference success is recorded in v2; propylene applicability, field validation and dashboard integration remain false/pending.

## CLI workflow

From the Avertiq root (Python 3.11+, standard library only):

```powershell
python -m unittest discover -s research/dispersion -p 'test_*.py' -v
python research/dispersion/propylene.py prepare-check --output outputs/propylene/preparation-check.json
python research/dispersion/propylene.py template --case baseline --output outputs/propylene/baseline.json
```

Templates for all four cases are also versioned under `research/dispersion/templates/`. They contain null observed results and cannot pass inspection. The command never launches ALOHA or fills expected answers. Use fresh output paths; overwrite is refused.

After a real future model run, fill the corresponding local template using observed outputs, not the frozen intended inputs as evidence. Record normalized actual inputs with explicit units, engine/version/binary hash, actual UTC observation timestamp, selected method, source summary, receptor/contour values, warnings and mapping-review notes. Retain raw evidence beside the local JSON, naming each file and its SHA-256. Do not republish complete property summaries.

```powershell
python research/dispersion/propylene.py inspect-run --case baseline --observed outputs/propylene/baseline.json --output outputs/propylene/baseline-checked.json
python research/dispersion/propylene.py compare-runs --runs-dir outputs/propylene --output outputs/propylene/comparison.json
```

Comparison requires `baseline.json`, `rate-half.json`, `rate-double.json`, and `wind-higher.json`, and rechecks every source record. It withholds numeric comparisons when the selected method or recorded output basis differs, or when either record lacks the [structured output-meaning supplement](PROPYLENE_OUTPUT_SEMANTICS.md). Missing receptor values require the actual unavailability reason and remain null; zero is never a missing-data placeholder. Ratios with a zero baseline remain null. No monotonic trend is asserted.

Record checks reject wrong case/chemical/engine, mismatched entered inputs, wrong units, missing semantics, changed evidence, outside-directory evidence paths, duplicate/missing receptors or contours, and invalid numeric values. Source mass/duration consistency uses the preregistered tolerance of max(1%, 0.01 in the named SI unit); this is a rounding sanity check, not physical validation. Contour distances are optional only with an observed unavailability reason; no polygons are synthesized.

The resulting status is `record_consistent_applicability_review_pending`. Hashes prove file consistency, not authenticity or model suitability; manual transcription and free-text semantics require human review against raw output. Warnings and review notes are retained. Actual results, physical acceptance and the dashboard adapter are still pending. No ALOHA command-line/API route is claimed.

After a future completed record passes inspection, the [local evidence archive workflow](PROPYLENE_EVIDENCE_ARCHIVE.md) can preserve the original record, raw files, frozen inputs and review provenance together. Archive verification does not close physical qualification gates.

For displayed units and reporting limits, use the [unit-transcription workflow](PROPYLENE_UNIT_TRANSCRIPTION.md). It preserves raw tokens and bounds while producing a separately checked normalized observation; it never converts a missing or bounded result into an exact scalar.

## Follow-up state review

The [independent source-state screen](PROPYLENE_SOURCE_STATE.md) supports the declared 25 C / one-atmosphere equilibrium gas assumption. It does not close ALOHA source-state applicability or identify the real release phase/temperature. Observed results and all model-acceptance gates remain pending.

## Single-command capture setup

The [capture-folder workflow](PROPYLENE_CAPTURE_FOLDER.md) can assemble all four blank records and their unconfirmed supplements in a fresh local directory. Intended input snapshots remain separate from observed fields; all run/evidence requirements above still apply.
