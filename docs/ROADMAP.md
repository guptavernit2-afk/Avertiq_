# Short roadmap

Updated 15 November 2026. First interface and physical-model readiness have separate finish lines. The first D-001 dashboard and local incident backend are implemented; see the [backend milestone](BACKEND_MILESTONE.md). The six-item local backend hardening plan is complete with 34 passing application/backup tests; see the [final backend handoff](BACKEND_HANDOFF_2026-11-14.md). Physical model qualification remains open.

The first [physics qualification package](research/FIRST_PHYSICS_QUALIFICATION.md) now contains frozen propylene/reference input sheets, an installed-model hash manifest and 90 passing qualification-tool tests. The [propylene preparation milestone](research/PROPYLENE_PREPARATION.md) adds four unrun v2 cases and guarded observed-record checks. The propane software reference matches all four preregistered values; propylene calculations remain pending; no calculated dashboard layer is enabled.

## Confirmed direction

Chemical transport and storage incident assessment for **LPG, CNG and reported propylene**, including light/heavy release behaviour. The wider physics target includes applicable gas dispersion, fire radiation, blast overpressure and terrain-dependent dispersion. No fourth chemical is selected. The first product case remains one stationary propylene-tanker training walkthrough, D-001.

## Work packages

| Order / stream | Work | Evidence of completion |
|---|---|---|
| Research handoff | Completed bounded evidence/design review | [Handoff](research/RESEARCH_HANDOFF_2026-11-10.md), chemical/storage matrix, physics requirements, result contract and 33 additional source records with access limits |
| First website and backend - implemented demo | D-001 inputs, map/context, observations, local database, revision/job/event history and handover | Labelled illustrative A/B assessments, saved immutable inputs, version conflict/retry checks, failure recovery, provenance exports and verified fresh-database restore; no qualified physics |
| Chemical model selection | Audit a supported methane CNG-reference and propane LPG-surrogate workflow; review propylene property/source route separately | Version-specific validity, input sheet, reference reproduction, licence/dependencies and measured runtime; no assumed mixture support |
| Dispersion qualification | Resolve existing numerical/model limitations or select a demonstrably applicable alternative | Source/grid/domain/time/boundary evidence; developed plume; suitable atmosphere and finite-width/crosswind treatment |
| Experimental comparison | Compare EEC550 with frozen source/sampling rules | All declared receptors, matched gas basis/units/heights/averaging, discrepancy report and explicit unresolved assumptions |
| Fire / explosion | Complete one bounded applicable scenario at a time | Reviewed source/ignition/failure assumptions, model/version and matched reference evidence before enabling each layer |
| Terrain physics | Qualify a 3D wind/dispersion route | Measured terrain-wind test and relevant dense-gas terrain comparison, plus site-data and runtime assessment |
| User / agency evaluation | Tabletop review, then requirements for operational deployment | Workflow feedback, verified partner data, reviewed responsibilities/access and acceptance; no automatic evacuation or safe-route claim |

## Current calculation limits

Existing research implements conditional propane equilibrium and coupled 2D thermal/phase/buoyancy flow with open boundaries. The saved checkpoint reports 295 tests and 283 atmospheric checks; no rerun is claimed for this documentation update. Main grid/time studies cover 0.001 s and do not establish spatial convergence. The slice omits lateral spread and projected crosswind. No EEC550 field comparison, terrain prediction, fire-radiation assessment or blast calculation has been accepted.

A 3D landscape is geographic context initially. The first website uses labelled fixtures; it must not present the research solver as a validated real-time three-fuel engine. Unavailable calculations stay unavailable with reasons.

## Immediate handoff

Use the [product brief](PRODUCT_BRIEF.md), [assessment contract](ASSESSMENT_CONTRACT.md), [chemical/storage scope](research/CHEMICAL_AND_STORAGE_SCOPE.md), [physics requirements](research/PHYSICS_REQUIREMENTS.md) and [terrain/validation plan](research/TERRAIN_AND_VALIDATION.md). No further generic literature collection blocks the fixture-based build. Actual source sheets, mentor module/version choices and appropriate validation still gate calculated results. No completion date for all physics is established.

The [propylene source-state review](research/PROPYLENE_SOURCE_STATE.md) supports the declared equilibrium-gas assumption independently. Actual discharge phase/temperature and ALOHA internal source-state mapping remain unverified; no propylene dispersion result exists.

The [ALOHA Direct Source investigation](research/ALOHA_DIRECT_SOURCE_REVIEW.md) confirms that the prescribed airborne mass-rate input subset matches documented Direct Source semantics. Internal source temperature/pressure/phase/enthalpy remain unverified; the reviewed mapping/weather interfaces do not resolve them. A guarded source-treatment report now preserves that distinction.

The [local evidence archive milestone](research/PROPYLENE_EVIDENCE_ARCHIVE.md) adds guarded capture and verification for future completed propylene records. Only disposable synthetic archives were tested; no actual propylene outputs or public physics adapter exist.

The [output-meaning milestone](research/PROPYLENE_OUTPUT_SEMANTICS.md) distinguishes outdoor averaged maxima, first-hour observation windows and diagnostic threshold envelopes. Comparisons now require evidence-linked structured metadata; exact averaging and actual propylene outputs remain pending.

The [unit-transcription milestone](research/PROPYLENE_UNIT_TRANSCRIPTION.md) adds checked output-unit conversions while preserving reporting bounds and unavailable values. It prepares evidence capture only; no propylene results have been generated.

The [qualification-tool CI workflow](../.github/workflows/dispersion.yml) now checks the synthetic regression suite and preparation commands from fresh Windows/Linux checkouts on Python 3.11/3.13. This guards the existing evidence workflow while ALOHA is pending; a passing CI job does not supply physics results or close qualification gates.

The [evidence JSON intake checks](../research/dispersion/README.md#unambiguous-evidence-json-intake) reject duplicate fields and numeric overflow/underflow before inspection, comparison or archiving. This closes demonstrated record-handling gaps while preserving all pending physics gates.

The [sensitivity-report plan and contract](research/PROPYLENE_SENSITIVITY_REPORT.md) prepares baseline/variant input differences, receptor/contour comparisons and explicit withholding reasons. Synthetic tests exercise the report; actual baseline and sensitivity runs remain pending.

The [local review-handoff plan and workflow](research/PROPYLENE_REVIEW_HANDOFF.md) adds a readable HTML export from rechecked four-case records, preserving warnings, withheld comparisons and pending gates. Only disposable synthetic exports have been tested; no actual propylene handoff or model results exist.

The [explicit archive-reinspection workflow](research/PROPYLENE_ARCHIVE_REINSPECTION.md) can record current checks separately when archive provenance is older, preserving historical bytes and all physics gates. Only disposable synthetic archive/receipt tests have run.
