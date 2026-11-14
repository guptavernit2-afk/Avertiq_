# First dispersion qualification

This package prepares and checks evidence for an external model. It is **not a dispersion solver** and is not connected to the dashboard. The existing equilibrium/flow research is unchanged.

## Frozen cases

- [D-001-PHYS-001](cases/propylene-direct-v1.json): assumed pure propylene, prescribed airborne gas source of 0.1 kg/s for 600 s, ground level, flat open country. Every physical/environmental value is an assumption, not a tanker measurement. This is not a hole, flashing-liquid or pressurised-jet calculation.
- [REF-ALOHA-547-PROPANE-02](cases/aloha-reference-propane-v1.json): the unignited propane leak from NOAA/EPA's September 2016 Example 2, Part 2. It is a separate software reproduction control, not validation of propylene, LPG mixtures or the historical accident. Expected outputs are source-reference values, not Avertiq results. Tolerances were saved before any observed run.

Do not edit a frozen case after seeing outputs. Create a new version and explain the change. The comparison uses a canonical JSON hash so Git line endings do not invalidate case identity.

## Commands

From the repository root, using Python 3.11+ with the standard library:

```powershell
python -m unittest discover -s research/dispersion -p test_qualify.py -v
python research/dispersion/qualify.py input-check --output outputs/my-input-check.json
python research/dispersion/qualify.py reference-template --output outputs/my-reference-run.json
```

The template has no observed values and cannot pass as a run. After an actual ALOHA calculation, record the displayed engine version, selected dispersion method, observed values in the named units, run timestamp and hashes of archived local evidence files. Then:

```powershell
python research/dispersion/qualify.py compare-reference --observed outputs/my-reference-run.json --output outputs/my-reference-comparison.json
```

Use fresh output paths. The commands never overwrite existing evidence. A comparison reports the actual differences, the previously registered tolerances and pass/fail; it always leaves propylene qualification, field validation and dashboard enablement false. Evidence files stay local; a manifest/hash check supports traceability but does not independently prove the contents are authentic. Human review of the source inputs and displayed outputs remains necessary.

## Installed model and redistribution

[Engine manifest](engine-manifest.json) identifies the official EPA 5.4.7 installer and installed binary/library hashes. The downloaded installer and runtime are under ignored `outputs/physics-qualification/`. The raw chemical library is not copied into this research package.

ALOHA's bundled terms identify restrictions on duplicating DIPPR physical-property data. Keep raw chemical-library files, installers, saved sessions and complete Text Summary exports local until their redistribution is reviewed. Public reports should contain the assumed input sheet, permitted calculated results and provenance hashes, rather than republishing the property database. This is a supervised desktop-reference route; no headless/API integration or distribution permission is asserted.

## Current evidence

- Official Windows installer downloaded and installed; SHA-256 and runtime/library hashes recorded.
- Installed library contains the propylene name; exact CAS/property selection still needs confirmation in the model UI.
- Six qualification-tool tests pass. These test input arithmetic, hash identity, comparison handling and rejected/incomplete evidence; they are not six physical validation cases.
- The propylene input check passes and identifies 60 kg as the assumed integrated airborne mass. This is only rate-times-duration arithmetic, not a plume prediction.
- The supervised ALOHA 5.4.7 propane reference run succeeded on 11 November: 26 min, 5,730 lb/min, 166 yd red and 474 yd yellow, with Heavy Gas selected. All four match the preregistered reference. See ../../data/public/dispersion-qualification-v1/reference-comparison.json. Propylene has no calculated result; its manual setup was not saved.

See the [model applicability decision](../../docs/research/FIRST_PHYSICS_QUALIFICATION.md) for the remaining gates. Keep the website's illustrative adapter and demo labels unchanged.

## Propylene v2 preparation

The [preparation milestone](../../docs/research/PROPYLENE_PREPARATION.md) maps documented fields, separates unverified source assumptions, versions the observed site-minute precision and defines four unrun cases. `propylene.py` provides prepare-check, template, inspect-run and compare-runs commands; no model is executed. Eight additional synthetic validator tests bring this package to 14 tests. All observed templates remain null/unrun. Record consistency never enables physics or grants applicability/field validation.
