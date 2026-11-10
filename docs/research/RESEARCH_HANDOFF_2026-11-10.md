# Research handoff: what we know and what we can build

Reviewed 10 November 2026. This closes a bounded evidence-and-design review, not all physics research. No new solver, experimental comparison or product application was run or implemented in this review.

## Project direction

Avertiq supports chemical transport and storage incident assessment: an incident record, attributed source/weather information, separate consequence assessments, nearby-place review, observations, revisions and authority-approved handover/public information. The user confirmed **LPG, CNG and reported propylene** as the focus, covering light/heavy release behaviour; no fourth chemical is selected. The longer-term physics scope includes unignited gas dispersion, applicable fire radiation and blast overpressure, and eventually terrain-dependent dispersion. These are separate conditional scenarios, not automatic simultaneous consequences of a collision.

The first build remains [D-001](../PRODUCT_BRIEF.md): one stationary propylene tanker, a complete five-screen workflow and labelled illustrative assessments. Live fleet tracking, operational dispatch and validated terrain/fire/explosion predictions are not prerequisites for that interface milestone and are not delivered by this research review.

## Evidence available now

| Area | Evidence actually available | Important limit |
|---|---|---|
| Incident background | Attributed public chronology and reported quantities | No verified exact accident pin, release history or complete tanker record |
| Chemical | Propylene identity and published reference properties; NIST phase-data reference | No reviewed propylene implementation or full tanker-discharge model |
| LPG / CNG scope | Primary composition/storage references; pure-methane and pure-propane model/validation leads | Actual mixture/source records, full validation-report review and engine audit remain; no new three-fuel engine |
| Geography/weather | Existing OSM tunnel anchor, local GLO-30 tile, 72 hourly ERA5 records | Approximate regional context; no measured valley wind or complete verified local road/facility inventory |
| Source research | Conditional propane/air/water equilibrium, phase and mixing calculations | Not the historical source and not automatically transferable to propylene |
| Flow research | Conservative transport, thermal/phase/buoyancy coupling, open boundaries and recorded grid/time studies | 2D slab, no finite-width/crosswind spread, no terrain model, unresolved spatial convergence |
| Numerical verification | Latest saved milestone reports 295 package tests; saved atmospheric record contains 283 passed checks | Existing results, not rerun in this documentation review; numerical checks are not field validation |
| Atmospheric comparison | EEC550 selected with 30 receptor records; EEC360 handling issues and EEC560 holdout documented | No experimental prediction score exists |
| Fire and explosion | Primary-source model families, inputs, endpoint meanings and limitations reviewed below | No Avertiq fire-radiation or explosion assessment engine exists |
| Product | Scope, scenario and walkthrough acceptance criteria | No product application; conversation mockup is an illustration |

The saved main atmospheric refinement record explicitly says `field_comparison_ready: false` and `matched_duration_s: 0.001`. The finer vertical aperture check does not resolve the remaining horizontal, domain, time or dimensionality issues. See [actual results](OPEN_ATMOSPHERE_SUMMARY.md).

## Research collected in this review

- [Physics requirements](PHYSICS_REQUIREMENTS.md): discharge/source distinction; gas, ignition, fire and explosion branches; model choices; units and threshold handling.
- [Terrain and validation plan](TERRAIN_AND_VALIDATION.md): terrain data, weather gaps, staged field/terrain comparisons, model capability and acquisition limits.
- [Assessment interface](../ASSESSMENT_CONTRACT.md): what a model result must carry before the website can show it as a calculation.
- [Chemical and storage scope](CHEMICAL_AND_STORAGE_SCOPE.md): confirmed three-group scope, surrogate limits, CNG/LNG distinction, storage input matrix and a bounded HyRAM+ engine audit proposal.
- [Source register](../../data/source-register.csv): 33 additional targeted primary-source records, SRC-062 through SRC-094, with date, review/access status and limitations. Some official pages were accessible only through indexed excerpts, and several linked reports were not retrievable; their rows say so.

This is a curated collection of relevant information, not a claim to have collected every possible dataset. External documents are linked and briefly paraphrased, not republished. Existing raw datasets, experiment sheets and generated solver results remain unchanged.

## Decisions for the first website

1. Use a map-centered incident workspace with explicit evidence status, data age, revision history and handover. Treat nearby-place intersections as review flags, not evacuation orders.
2. Separate map layers for gas concentration, flammability criteria, thermal radiation and blast overpressure. Disabled or unsupported scenarios show their reason; absence of a contour never means absence of hazard.
3. Use 3D terrain for geographic context initially. Do not bend a flat-ground footprint along a valley and call it terrain-dependent physics.
4. Start with illustrative D-001 fixtures. Later accept reviewed, versioned external results or a qualified engine through the same assessment contract. Do not assume an ALOHA/Phast automation API, export entitlement or redistribution permission.
5. Preserve the existing custom solver as research. Compare an established applicable workflow before treating further custom CFD development as the shortest route to usable predictions.
6. Keep public information separate from internal records. Draft, review, approval and publication are proposed product states; no agency connection, official endorsement or emergency-service integration exists.
7. Use chemical/composition and asset-type fields that can accommodate LPG, CNG and propylene. Preserve D-001 as the first propylene walkthrough; do not silently replace it or enable unsupported chemical models. Prioritize an applicable methane/propane engine audit before extending custom CFD for every fuel.

## Work that remains, with a concrete finish condition

| Workstream | Next bounded task | Exit evidence | Blocks first fixture-based website? |
|---|---|---|---|
| Product data | Confirm approximate demo anchor against existing geographic record; prepare attributed local roads/place fixtures | Labelled demo pin and redistributable fixture package; no invented real sites | Required during build |
| Propylene source | Review property basis and one physically consistent tanker/direct-source sheet | CAS-specific properties, units, phase assumptions and independent calculation/benchmark | No; blocks calculated propylene assessment |
| CNG / LPG models | Audit one pure-methane reference case and one pure-propane surrogate case, with explicit mixture limits | Pinned engine, fully reviewed applicable validation, reproduced runs and runtime/licence record | No; blocks calculated CNG/LPG layers |
| Flat-ground dispersion | Resolve source, horizontal grid, domain/reflection, long-run cost and atmospheric transport/dimensionality | Reproducible convergence/sensitivity evidence and supported model domain | No; blocks receptor comparison |
| Experimental comparison | Freeze EEC550 source/sampling rules, then predict all declared receptors | Matched averaging/basis/coordinates; discrepancy table, exclusions and untuned holdout strategy | No; blocks experimental accuracy claims |
| Fire radiation | Select one applicable fire scenario/model and benchmark recipe | Matched reference run, duration/view geometry, property and numerical checks | No; blocks radiation layer |
| Blast | Select appropriate VCE or vessel-failure scenario; review ignition and congestion assumptions | Versioned method, participating fuel definition and reference comparison | No; blocks blast layer |
| Terrain | Select an applicable 3D flow/dispersion route and licensed validation data | Terrain wind comparison followed by relevant dense-gas terrain comparison | No; blocks valley-prediction claims |
| Operational deployment | Obtain agency/user review, real data agreements and system requirements | Reviewed operating responsibilities, access controls, stale-data behaviour and acceptance | No; blocks operational use |

Do not describe these open items as completed research. Literature review can end here for the first interface; calculation development and validation continue as separate milestones. A reliable completion date for all physics is not established.

## Mentor / partner information still required

These requests can be prepared now; no messages were sent.

- Which deliverable is expected first: training workflow, matched consequence calculations, or validated valley dispersion? Agree one acceptance case for each required physical outcome.
- Confirm cargo composition and tanker geometry/state, inventory, opening/pipe details, source height/direction and release duration; identify which values are measured versus assumptions.
- Confirm Phast version, modules/add-ons, access, an agreed input sheet and permitted exports. A standard Phast result is not evidence that a CFD add-on was used.
- Agree consequence thresholds, exposure/averaging times, assessment height, uncertainty reporting and the intended approving authority. Reference software defaults are not adopted Indian operating criteria.
- Obtain source/receptor/weather records for comparisons and resolve EEC550 source-height/averaging-history gaps. Seek local wind and higher-resolution terrain/obstacle data for valley work.
- Review the current phase-equilibrium/common-motion assumptions and whether the planned implementation route is feasible on available hardware.

## Closeout check

Documentation review checks CSV structure and source IDs, internal links, scope consistency and saved numerical-evidence flags. The [audit record](../../data/public/research-handoff-2026-11-10-audit.json) records check counts and document hashes. No new physics accuracy, new test-suite pass, PHAST result, ALOHA run, downloaded terrain experiment or complete official/legal review is claimed. Commit/push status is reported separately after Git operations succeed.
