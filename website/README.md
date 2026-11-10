# Avertiq incident workspace

D-001 training dashboard: approximate Adoshi map anchor, real geographic terrain/roads, fictional nearby places and prepared A/B assessment illustrations. No physics engine, live tracking, agency login, dispatch or public notification is connected. Records are stored only in the current browser. Do not enter private operational information.

## Run locally

Requires Node 24+ and npm. From this directory:

```powershell
npm ci
npm run dev
```

Open the URL printed by the server. For a built production preview:

```powershell
npm run build
npm run start -- --port 5174
```

MapLibre is pinned to 6.17.0. The predev/prebuild step copies its unchanged module worker and BSD licence into generated public assets. This avoids development middleware being injected into worker scope. Keep `sites()` and the Worker build integration when modifying the Vite configuration.

## Verify

```powershell
npm test
npm run typecheck
npm run build
```

Tests cover invalidation on unsupported edits, preserved A/B snapshots, round-trip persistence, rejection of forged records, explicit non-calculated output, safe report text and removal of stale map images. Browser checks must also cover actual WebGL terrain rendering, mobile reflow and the observation/handover walkthrough; passing TypeScript alone does not establish those behaviours.

## Walkthrough

1. Review the assumed release and simulated weather inputs in preset A.
2. Explore 2D/3D terrain and fictional places; mark a demo review.
3. Change cargo or another input. The prepared area disappears and the assessment becomes outdated.
4. Restore a preset, then load B. A remains in revision history.
5. Add a synthetic observation. It does not recalculate the assessment.
6. Prepare a handover and download HTML or the labelled JSON record. Open the HTML in a browser to print/save as PDF.

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
