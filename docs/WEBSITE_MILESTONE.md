# First website milestone: D-001

10 November 2026. The user authorized implementation of the preview as a website dashboard and 3D map with clearly labelled demo assessments. This supersedes the earlier research-only boundary for this first product workflow.

## Implemented

- React/Vinext dashboard under `website/`, using the Sites starter and its Worker build integration.
- MapLibre geographic map at the documented approximate Adoshi tunnel anchor; OpenStreetMap roads and Mapterhorn 3D terrain, attributed in the map and evidence dialog.
- Fixed, hand-authored illustrative A/B areas; no concentration threshold or hazard distance. Changing any supported input invalidates and hides the area until a documented preset is restored.
- Cargo/asset inputs accommodating LPG, CNG and propylene; only the propylene D-001 fixture is supported. No new chemical source calculation.
- Immutable A/B input snapshots, selected fictional-site review, synthetic observations and browser-local persistence.
- Handover preview plus labelled HTML and JSON exports; printable HTML retains assumptions, missing information, observations, revisions and limitations. Map capture is included only for a current illustration.
- Separate public-information visual preview with unpublished/draft status. No role-based security, real agency users or notification service is implemented.

## Verification

Seven meaningful domain tests and TypeScript checks passed. The production build passes. Browser checks confirmed actual geographic/terrain rendering, 2D/3D controls, fixture invalidation/restoration, B with preserved A, simulated observation entry, a downloaded labelled HTML handover and persistence after reloading. Desktop and phone-width layouts were inspected; no horizontal document overflow was observed at checked widths.

The initial map integration exposed a worker-loading issue and a zero-height container caused by MapLibre CSS overriding the app's container positioning. The worker is served as an unchanged, version-pinned public module with its licence; a more specific layout rule fixes the container height. Rendering was checked after those repairs. A build-only check would not have caught the blank map.

## Private publication

[Open the private dashboard](https://avertiq-incident-workspace.architk760.chatgpt.site). Sites confirmed successful publication of synchronized source commit `932d7f8bcdacc55cdc8f41770a4b91b4c6f37c97`; deployment `appgdep_6af2bc53562c81918901a2baddb978e2`. This is an owner-private demo, not a public incident notification. The original Avertiq GitHub origin is unchanged.

## Remaining limits

Tile services need internet access; the device needs WebGL. The approximate pin is not verified accident location, and demo facilities are fictional. Elevation display does not qualify valley dispersion. No research solver changed and no existing research tests were rerun for this frontend work.

Next review should cover the actual incident-to-handover workflow with a prospective user, then a bounded supported model-integration case. Hosting status and the actual deployed URL must be confirmed by the Sites deployment result; creation of a Site alone is not publication.
