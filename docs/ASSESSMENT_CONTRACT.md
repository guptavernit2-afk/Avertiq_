# Assessment contract for the website build

Proposed data/interface requirements, 10 November 2026. No product endpoint or live integration is implemented. The first walkthrough uses fixtures; physics results must satisfy separate readiness checks.

## Input and result records

| Record | Required content |
|---|---|
| Incident | ID, transport/storage asset type, source location/accuracy/CRS, reported time and timezone, chemical identity/composition with mass/mole basis, evidence references and owner |
| Scenario revision | Immutable input snapshot; measured/reported/assumed/unavailable status per value; separate synthetic-data flag; changes from prior revision |
| Source | Direct defined source or tank-discharge calculation; rate/state/geometry/time history and units; uncertainty and phase basis |
| Weather | Speed and units, wind-from direction/reference, measurement height/time/location, stability/turbulence inputs, origin and data-age/representativeness limits |
| Model run | Engine/version, scenario type, configuration hash, property source, input revision, start/completion time, solver status, supported and omitted physics |
| Evidence | Reference IDs/URLs or permitted files, retrieval/measurement time, transformations, model verification and experimental-comparison status |
| Result | Quantity/unit/basis, geometry or field asset, CRS, threshold and authority/reference, assessment height, time/period, averaging window and valid input domain |
| Review | Author/reviewer, status, limitations, review time; approval of a result distinct from approval of an operational action |

Store physical location in documented coordinates and preserve transformation history. Use a metric frame for physics; export web geometry with declared axis order. Never calculate metres directly from degree differences. A view's terrain exaggeration must not alter physical geometry.

## Distinct assessment types

| Type | Quantity | Additional metadata |
|---|---|---|
| `illustrative_fixture` | No physical hazard quantity | Fixture ID, synthetic flag and matching demo preset. Unsupported input edits invalidate the fixture |
| `gas_concentration` | Declared gas-phase mol/volume fraction, ppm or supported mass concentration | Species, height, instantaneous/averaged/envelope meaning and concentration conversion basis |
| `flammability` | Declared concentration criterion, optionally percent LEL | Chemical LEL source/conditions and interpretation; not a probability of ignition |
| `thermal_radiation` | Incident flux in kW/m2; dose only if an identified method computes it | Fire scenario, target/view geometry, duration and supported shielding assumptions |
| `blast_overpressure` | Peak excess pressure in Pa/kPa, with original units retained | Explosion method, ignition/participating cloud/congestion assumptions; impulse/duration only if calculated |

Output status is independent of type: proposed `queued`, `running`, `completed`, `failed`, `unsupported`, `stale`. Scientific evidence status is also independent: `illustrative`, `numerically_verified`, `benchmarked`, `experimentally_compared`, plus a documented scope. These proposed labels are not a universal certification ladder: one comparison cannot qualify every scenario.

Never substitute an illustrative polygon after a solver fails while retaining a calculated label. Invalid/missing results have a visible reason. A new standalone run with changed wind is not automatically the continued trajectory of the old cloud. Time animation requires actual compatible time-resolved outputs.

## From model layers to authority review

Intersect a declared assessment with attributed roads and places, then show why each was flagged and which revision was used. Unknown occupancy, contacts, access and capacity stay unknown. Deduplicate overlapping geometries before any population count; publish a count only with a defensible population source and method. No intersection result independently determines evacuation, safe ingress or road reopening.

The [PHMSA ERG page](https://www.phmsa.dot.gov/training/hazmat/erg/emergency-response-guidebook-erg), SRC-078, describes initial-phase transportation-response guidance. Link a verified chemical-specific reference where appropriate; do not transform guidebook distances into computed plume contours or claim the US guidebook is an Indian operating authorisation.

## Internal and public views

Proposed product roles: incident commander/control-room reviewer, modelling/hazmat specialist, field contributor, transport-data contributor and public reader. Final permissions and local agency assignments require user/agency review; no account integration exists.

An indexed [NIDM training report](https://nidm.gov.in/pdf/trgReports/2021/January/Report_06-08January2021sc.pdf), SRC-076, describes the Information and Media Officer's communication role and Incident Commander approval of released information. Indexed [NDMA IRS guidelines](https://nidm.gov.in/PDF/guidelines/Incident_Response_System.pdf), SRC-075, identify command, operations, planning and logistics roles. Direct retrieval timed out, so this is targeted role evidence, not full guideline or legal-compliance review.

Our design inference is a public-message workflow of draft -> review -> approval -> publication, with author, approving officer, publication time, superseded version and affected localities. Keep private shipment/contact records, staff tasks and unreviewed experimental model outputs out of the public view. Mark stale public updates and preserve the last approved version. No messages, alerts, dispatches or government/public notifications were sent as part of research.

## First-build acceptance

Complete D-001 from incident to inputs to map to observation/revision to readable handover. Preserve revision A after B. Attach illustration/evidence labels to screens, layers and exported views. Show missing inputs, invalidate fixtures after unsupported edits, and provide an explicit reason for unavailable physics layers. This allows a useful website build without pretending that blast, radiation or valley dispersion are already implemented.
