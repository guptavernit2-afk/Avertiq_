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

## Declared source-state review

The [temperature/phase review](../../docs/research/PROPYLENE_SOURCE_STATE.md) independently supports the assumed equilibrium gas state, while retaining actual release and ALOHA internal-state gates. `source-state-check` adds a bounded property-based screen, with no extrapolated vapour pressure or model predictions. The package now has 18 passing tests. Frozen cases and observed templates are unchanged.

## Direct Source treatment investigation

The [source-treatment review](../../docs/research/ALOHA_DIRECT_SOURCE_REVIEW.md) distinguishes the documented prescribed-gas input subset from unresolved internal thermodynamics. `source-treatment-check` checks source semantics and normalized entries, retaining null effective state and false qualification flags. `inspect-run` includes this review separately from observed outputs. Eight new tests bring the package to 26; frozen cases and unrun templates are unchanged. Actual propylene results remain pending.

## Local run evidence archives

`archive.py archive-run` preserves a future completed observation and its raw evidence with frozen inputs and checking provenance. `verify-archive` checks integrity and reinspects when current provenance matches; changed tooling/configuration leaves reinspection pending. Use an independently retained archive SHA-256 for whole-file identity. See the [archive workflow](../../docs/research/PROPYLENE_EVIDENCE_ARCHIVE.md). Raw archives stay local and Git-ignored. Thirteen additional disposable synthetic tests bring the package to 39 passing tests; actual propylene results remain pending.

## Structured output meaning

The [output interpretation milestone](../../docs/research/PROPYLENE_OUTPUT_SEMANTICS.md) adds `output-semantics-template` and evidence-linked metadata for outdoor averaged maxima, the first-hour observation window, relative receptors and diagnostic contour meaning. Legacy observations remain inspectable, but numerical comparisons require consistent structured metadata; actual outputs and exact averaging remain pending. Archive provenance includes the new dependencies. Eight additional synthetic tests bring the package to 47 passing tests.

## Raw units and reporting limits

`transcription-template` prepares an unconfirmed supplement; `normalize-run` creates a separately checked observation from recorded units and evidence. Bounds remain null in scalar fields with their qualifier and limit retained; unsupported conversions are rejected. See the [unit-transcription workflow](../../docs/research/PROPYLENE_UNIT_TRANSCRIPTION.md). Inspection and archive provenance preserve the original tokens. Twelve additional synthetic tests bring the package to 59; actual propylene physics results remain pending.

## Automated qualification-tool checks

The [dispersion workflow](../../.github/workflows/dispersion.yml) runs this package's synthetic regression tests and input/preparation CLI checks on Windows and Linux with Python 3.11 and 3.13. It triggers when the tools, their public qualification records or the workflow change, and can also be started manually. Each job uses a fresh checkout and only Python's standard library; no installed ALOHA, local evidence archive or external dataset is required.

The workflow checks that tests leave versioned research records unchanged. Temporary evidence remains disposable, and no CI artifacts are uploaded. A green job means the record-checking software passed its tests; it is not an ALOHA run, new reference reproduction, propylene result, applicability decision or field validation. The historical propane reference is read as a registered control record, not rerun. Actual physics results and dashboard integration remain pending.

To repeat the regression suite locally:

```powershell
python -m unittest discover -s research/dispersion -p 'test_*.py' -v
```

The input/preparation smoke commands are documented above; use fresh output filenames because they refuse overwrites. GitHub Actions results establish the remote platform/version checks separately from a local test pass.

Local verification for this CI addition: all 59 tests passed on Python 3.13.6, then passed again in a disposable snapshot containing only tracked dispersion code and public qualification records. Both workflow smoke commands passed there, their model-execution/dashboard flags stayed false, and source bytes remained unchanged. Workflow YAML and changed documentation paths were also checked. Remote matrix outcomes are available in the workflow run history.

## Unambiguous evidence JSON intake

On 15 November 2026, file and archive readers were unified around one strict JSON-object parser. Duplicate keys are rejected at every nesting level, including equivalent escaped key names and repeated identical values. Previously the ordinary file reader silently kept the last occurrence, allowing an earlier synthetic-data flag or output value to be hidden. Archive decoding already rejected duplicates; both entry paths now apply the same policy.

The parser also rejects non-finite numeric constants, exponent overflow (for example `1e309`) and nonzero numbers that would underflow to zero (for example `1e-999`). These are synthetic parser examples, not concentrations from ALOHA. Literal zero, null/unavailable values, finite representable numbers and ordinary free text remain supported. Normal floating-point rounding still applies; this is not arbitrary-precision measurement storage. Original displayed digits belong in the raw transcription supplement and evidence files.

Rejected observations produce no inspection, normalization, comparison or new archive output. The input file is not repaired or modified automatically: resolve ambiguous fields against raw evidence and save a reviewed correction separately. Parsing only checks representation; it cannot authenticate an operator's claims or close scientific review gates.

Seven new regression tests cover nested/escaped duplicates, numeric overflow/underflow, valid zero/null handling and the observation CLI entry points. The full suite passes 66 tests locally. Frozen cases, unrun templates and public preparation/reference records remain unchanged. Archive provenance already hashes the shared parser module; archives created with older tooling therefore retain the existing integrity-only/reinspection-pending behaviour when code provenance differs. Actual physics results remain pending.

## Sensitivity comparison report

The [planned sensitivity-report task](../../docs/research/PROPYLENE_SENSITIVITY_REPORT.md) extends `compare-runs` with frozen input differences, diagnostic contour-distance changes and explicit comparison blockers. Missing/bounded values preserve each side's reason and bound metadata; zero-baseline and unrepresentable ratios remain null with an explanation. All existing run/evidence/semantics checks still apply. Eight new synthetic tests bring the suite to 74 passing tests. Actual propylene runs and results remain pending.

## Readable local review handoff

After actual four-case observations exist, `review_handoff.py --runs-dir outputs/propylene --output outputs/propylene/review-handoff.html` rechecks them and exports a self-contained HTML handoff for local review. It preserves warnings, output units, comparison blockers, bound/missing values and unresolved qualification gates, with case/engine/evidence and checked-comparison hashes. It accepts no trusted prebuilt comparison file, embeds no raw evidence and refuses overwrites. See the [plan, workflow and limits](../../docs/research/PROPYLENE_REVIEW_HANDOFF.md). All 82 tests pass, including eight disposable synthetic handoff tests; actual physics results remain pending. No visual browser acceptance is claimed.

## Explicit reinspection after tooling changes

`archive.py reinspect-archive` verifies an archive and writes a separate current-inspection receipt without rewriting its historical evidence or provenance. It rejects a changed registered case or a record that fails current checks. See the [plan, receipt semantics and workflow](../../docs/research/PROPYLENE_ARCHIVE_REINSPECTION.md). All 90 qualification-tool tests pass, including eight new synthetic reinspection tests. This is record consistency only; actual ALOHA results and all physical-acceptance gates remain pending.

## Prepare a blank four-case capture folder

`python research/dispersion/prepare_capture.py --output outputs/propylene/session-01` creates a fresh local folder containing all four unrun capture records with unconfirmed output-semantics and transcription supplements, separate frozen input snapshots, empty evidence directories and a workflow guide. It does not fill observations or execute ALOHA. Existing destinations are refused; incomplete setup must be retried to a new folder. See the [plan and setup-manifest limits](../../docs/research/PROPYLENE_CAPTURE_FOLDER.md). All 98 tests pass, including eight disposable setup tests. Actual physics results remain pending.
