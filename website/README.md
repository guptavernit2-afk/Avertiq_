# Avertiq incident workspace

D-001 training dashboard: approximate Adoshi map anchor, real geographic terrain/roads, fictional nearby places and prepared A/B assessment illustrations. Saved inputs, immutable input revisions, assessment jobs and event history now persist in a **local SQLite-backed D1 database**, rather than browser storage. Unsaved edits remain browser drafts. No physics engine, live tracking, agency login, dispatch or public notification is connected. Do not enter private operational information.

## Run locally

Requires Node 24+ and npm. From this directory:

```powershell
npm ci
npm run db:migrate:local
npm run dev
```

Open the URL printed by the server. For a built production preview:

```powershell
npm run build
npm run db:migrate:local
npm run start -- --port 5174
```

MapLibre is pinned to 6.17.0. The predev/prebuild step copies its unchanged module worker and BSD licence into generated public assets. This avoids development middleware being injected into worker scope. Keep `sites()` and the Worker build integration when modifying the Vite configuration.

## Verify

```powershell
npm test
npm run typecheck
npm run build
```

Tests cover fixture invalidation, real SQLite reopen persistence, concurrent version conflicts, immutable input revisions, job transitions, unsupported/missing inputs, interrupted-job recovery, malformed/cross-origin requests, demo labels and export geometry suppression. Browser checks cover the actual save/assess/history path; passing TypeScript alone does not establish those behaviours.

The local-only migration command tracks applied migrations and can be rerun without replaying applied SQL. `wrangler.local.json` uses the same placeholder database ID as the framework preview. Local state is ignored under `.wrangler/state`; deleting that directory deletes the local database. It is not a cloud backup or an agency service. Browser storage from the earlier demo is not silently imported. See [backend milestone](../docs/BACKEND_MILESTONE.md) for the API, storage design and limits.

## Walkthrough

1. Load D-001 from the local database. The first load creates assumed preset A inputs, with assessment status `not-run` and no area.
2. Choose **Run demo assessment**. Only exact supported presets produce a completed illustrative area; no physical calculation runs.
3. Change cargo or another input. The old area disappears immediately. Choose **Save incident**, then run the demo assessment; unsupported inputs return their reason without geometry.
4. Load preset B, save and assess. Open **Activity & revisions** to see saved input snapshots, jobs and queued/running/terminal events. Clicking a historical input snapshot loads a draft; it does not replace history.
5. Add a synthetic observation or review, then **Save incident**. These do not recalculate the assessment or create a new input revision unless the inputs also changed.
6. Export a labelled JSON/HTML handover including saved backend history. Unsaved drafts are identified; unavailable/stale/failed assessments have no map geometry.
7. Reload the browser or restart the local server: saved inputs, jobs and history remain. **Restore initial draft** retains all database history.

The public preview is a draft visual only. It provides neither a published incident notice nor a security boundary.

## Geography and service dependencies

- Approximate pin: 18.76449685 N, 73.3465372 E, from the collected OSM tunnel midpoint. Not verified accident coordinates; decimal precision is not position accuracy. See `../data/public/tunnel-anchor.metadata.json`.
- Basemap: © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), ODbL. Live raster service at tile.openstreetmap.org. No bulk download/offline tile cache. Review [tile policy](https://operations.osmfoundation.org/policies/tiles/) and use an appropriate provider before production traffic.
- Terrain: [Mapterhorn](https://mapterhorn.com/) tile service, [underlying attribution](https://mapterhorn.com/attribution). Terrain is geographic context; no effect on gas movement is calculated. Availability/resolution depend on the source coverage.
- Rendering: MapLibre GL JS, BSD-3-Clause; generated worker distribution retains its licence. Fonts: Google Fonts DM Sans / Manrope, with system fallbacks.

External tiles require internet access and WebGL. Loading failures show an explicit map message; no silent synthetic map or solver-result substitution occurs. A physical metric scale on the basemap is not a calculated hazard distance. Prepared polygons and fictional places carry no measured field meaning.

## Source and hosting

Authored application lives here in the Avertiq repository. `.openai/hosting.json` retains the private Site identity. Sites publication uses a separate sanitized release checkout under the parent repository's ignored `outputs/` directory, preserving the original GitHub origin. Never store source credentials in project files. Publish only an archive matching the exact synchronized source commit.

Future calculation results must satisfy `../docs/ASSESSMENT_CONTRACT.md`; unsupported physics stays unavailable.

## Local backup and restore

Use the [backup/recovery guide](../docs/LOCAL_BACKUP_RESTORE.md) for `db:inspect`, `db:backup`, `db:verify` and `db:restore`. Restore creates a separately verified database and refuses existing/live destinations. Backups preserve the saved incident and history; dashboard handover JSON is not a restore file.

Current completion and remaining work: [final backend handoff](../docs/BACKEND_HANDOFF_2026-11-14.md). The latest CLI suite has 34 tests; recent browser verification is pending the user's availability.
