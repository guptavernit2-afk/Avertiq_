# Backend workflow before expanding the dashboard

**11 November update:** the first local D-001 backend slice is implemented. See [implementation, API, tests and remaining limits](BACKEND_MILESTONE.md). The sections below retain the design baseline from before that work; browser-only storage statements describe the earlier version.

10 November 2026. The user found the first dashboard too raw and the purpose/results difficult to understand. This is a proposed next work package, not an implemented backend or accepted physical model. Continue locally; no further hosting/deployment without an explicit request.

## What actually runs today

- The website server serves the React application. Its existence does not mean an incident-assessment API exists.
- Incident inputs, illustrative presets, observations, reviews and history live in browser state/local storage. HTML/JSON reports are generated in the browser.
- The map retrieves geographic tiles from external services. It does not ask a physics engine to calculate the displayed assessment.
- The independent Python research package calculates conditional propane source/flow studies. It is not connected to the website and is not a field-ready LPG/CNG/propylene assessment service.
- Database/auth/connector scaffolding inherited from the starter is not an implemented incident database, agency login or live data connection.

## The intended assessment chain

Incident record -> attributed input revision -> input/applicability checks -> source representation -> selected physical scenario -> supported model run -> reviewed result record -> map and explanation -> handover.

The source calculation describes what actually enters the environment, including state, rate, direction and time history. A scenario then selects unignited dispersion, an applicable ignited release/fire, or an applicable explosion/failure branch. A collision alone does not activate every branch. Model availability and validation scope determine which calculations can run.

The website must explain each step: what was entered, what remains unknown, why a model was selected, whether a calculation actually ran and what its output means. A backend response with only a polygon will leave the current usability problem unresolved.

## Proposed responsibilities

| Backend responsibility | Required behaviour | Website explanation |
|---|---|---|
| Incident and asset records | Persist chemical/composition, transport/storage type, location accuracy and reports | What happened and where; measured/reported/assumed/missing labels |
| Scenario revisions | Preserve immutable input snapshots and changes | What changed since the previous assessment |
| Input checks | Check units, completeness and physically consistent source/model requirements | Which missing values block a calculation and why |
| Source adapter | Distinguish direct defined source from tank/cascade discharge calculation | What release is being assessed; no invented tank measurements |
| Model selection | Match chemical/state/scenario to a supported method and its evidence | Why this model applies; unavailable effects and reasons |
| Assessment job | Track queued/running/completed/failed/unsupported/stale against one input revision | Whether there is a result, a failure, or an unresolved prerequisite |
| Result storage | Keep quantity/basis/units, time/averaging/height, provenance and geometry | What the layer represents and how to interpret it |
| Place review | Associate attributed places and review records with the selected assessment | Why a place is flagged; occupancy/access unknowns; no automatic evacuation |
| Handover | Export the incident, assumptions, result status, history and pending decisions | A readable account of what is known and what needs action/review |

These are design responsibilities, not new API endpoints. The [assessment contract](ASSESSMENT_CONTRACT.md) specifies result metadata. The [chemical/storage scope](research/CHEMICAL_AND_STORAGE_SCOPE.md) and [physics requirements](research/PHYSICS_REQUIREMENTS.md) retain the model gates.

## First bounded backend milestone

Connect **one D-001 incident** through persistent incident/revision records, an assessment job and an explicitly illustrative result adapter. Return the same labelled A/B fixtures through that path first, preserving current invalidation and export protections. That demonstrates the software/data chain without claiming a physical calculation. Do not rename that result a simulation merely because a server returned it.

Then integrate one supported calculation through a separate adapter after its source/applicability/reference checks are met. LPG/CNG mixture assumptions, propylene-specific source work, developed-plume validation and terrain physics remain explicit dependencies. Replacing fixture output with the existing 1 ms research field would not establish a usable incident assessment.

Acceptance for the software milestone: create and reload a persisted incident; preserve A after B; show a clear missing-input/unsupported reason; associate every job/result with its exact revision; prevent stale or failed results being displayed as current; carry evidence and synthetic labels through the map and handover. Multi-user agency operation, live telemetry and operational approval require subsequent requirements and implementation.

## Recommended interface direction

Lead the incident page with a short situation summary, a step-by-step assessment status, the important unknowns and a readable result explanation. Keep the map tied to that explanation. Use one complete scenario to test whether a new reader can answer: what happened, what the system used, what it produced and what remains undecided.

This plan recommends clarifying and building the first backend slice before adding more dashboard features. It does not require finishing every future fire/blast/valley model before improving the workflow.
