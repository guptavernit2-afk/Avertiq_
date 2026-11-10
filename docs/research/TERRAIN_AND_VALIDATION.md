# Terrain dispersion: data, model routes and evidence gates

Reviewed 10 November 2026. This is a research plan and capability review. No terrain-flow or dense-gas field comparison was executed.

## What a valley calculation actually requires

Terrain must enter the computational geometry and wind/transport solution, rather than only the map renderer. A useful model must represent the applicable atmospheric boundary layer, density effects, source momentum/temperature, turbulent mixing and finite-width lateral flow. Pooling/phase change, obstacles and transient weather require explicit capability decisions. A two-dimensional vertical slab cannot represent arbitrary valley branching or crosswind spread.

[NOAA's limitations](https://response.restoration.noaa.gov/oil-and-chemical-spills/chemical-spills/response-tools/alohas-limitations.html), SRC-011, explicitly exclude terrain steering, wind shifts and hazardous fragments. ALOHA remains a potential flat-ground screening/benchmark reference within its assumptions, not a valley engine. [LLNL's dense-gas research](https://narac.llnl.gov/research-and-development/dense-gas-transport-in-complex-environments), SRC-012, distinguishes SLAB-style empirical modelling from Aeolus CFD for structures and terrain, and reports Thorney Island evaluation. That supports the need for a different model class; it does not establish public access or our model's validity.

## Candidate routes, with access and applicability left visible

| Route | Primary evidence reviewed | Proposed role and unresolved dependency |
|---|---|---|
| Existing Avertiq custom solver | Local numerical results and implementation | Verification research baseline; needs long-run feasibility, 3D/transport, terrain and field comparisons |
| ALOHA | SRC-011 and SRC-062 | Potential flat-ground reference; no terrain steering; no service API assumed |
| Phast / CFD add-on | [DNV product description](https://www.dnv.com/services/phast/), SRC-009 | Candidate reviewed source/consequence workflow; distinguish base product from 3D CFD add-on; mentor version/modules/licence/export rights unknown |
| FLACS | [Terrain import](https://knowledge.gexcon.com/docs/terrain-import), SRC-070; [grid guidance](https://knowledge.gexcon.com/docs/grid-guidelines), SRC-071 | GeoTIFF terrain import is documented; this alone does not establish dense multiphase validity for steep Adoshi terrain. Need installed version, physics limits, licence and matched validation |
| Aeolus | SRC-012 | Evidence that terrain-capable dense-gas CFD exists; no deployment/API entitlement obtained |
| OpenFOAM platform | Earlier source/phase review in [validation plan](../VALIDATION.md) | Existing gas-only selection was rejected for H00; atmospheric features do not supply a reviewed propane/water/ice model. New OpenCFD atmospheric pages returned 403, so no fresh capability acceptance |

Do not transfer one vendor's mesh rules to another solver. Gexcon's reviewed grid guidance is tied to its modelling/validation practice; it discusses scenario-dependent resolution sensitivity. A universal cells-per-source threshold is not established here.

## Available geographic context and actual gaps

Existing acquisition details and checksums: [geography/weather record](GEOGRAPHY_WEATHER.md) and [download manifest](../../data/public/external-download-manifest.json).

| Input | Available | Additional work before physical use |
|---|---|---|
| Incident pin | Current mapped tunnel anchor; accident coordinates unverified | Confirm a demo pin, accuracy and provenance; do not label it surveyed accident position |
| Elevation | Local GLO-30 N18 E073 surface-model tile; header/georeferencing checked | Clip justified extent; inspect no-data, units, acquisition epoch, vertical reference and slope; create qualified computational geometry |
| Terrain resolution | About one-arc-second source spacing, not detailed road-cut geometry | Review whether finer terrain, barriers, drains, structures or tunnels determine the relevant physics; avoid adding visual detail as measured geometry |
| Wind/weather | 72 hourly ERA5 regional records, returned grid point about 10 km from anchor | Obtain appropriate local wind/stability/turbulence information; quantify sensitivity; gridded historical wind does not establish valley flow |
| Roads and facilities | Tunnel feature only, not a complete verified network | Acquire a dated, attributed corridor extract; review missing roads and facility coordinates; separate mapped feature from confirmed accessibility/capacity |
| Occupancy/resources | No real local occupancy, shelter capacity, hospital capacity or response-team availability | Partner verification; otherwise show unknown or explicitly synthetic demo values |

The GLO-30 raw GeoTIFF is not automatically a web terrain tileset or CFD mesh. Maintain transformations from original CRS/vertical datum to a documented local metric frame and web coordinates. Keep physical heights and vertical exaggeration separate. [MapLibre's terrain example](https://maplibre.org/maplibre-gl-js/docs/examples/3d-terrain/), SRC-079, documents rendering; it does not calculate gas transport. Basemap/elevation attribution and hosting terms remain separate from the rendering library.

## Validation ladder: finish one level before claiming the next

1. **Numerical verification:** conservation, pressure/gravity controls, inlet/outlet behaviour, coordinate transformations, source resolution and mesh/time/domain sensitivity. Existing results cover parts of this level; unresolved grid dependence remains.
2. **Flat-ground dense-gas field comparison:** use EEC550 with its declared conditional source, actual receptor coordinates/heights, gas concentration basis and 150 s averaging. Review start/end sampling, finite-width/crosswind and source-height assumptions before running. Compare all 30 declared receptors, not a convenient subset. Keep EEC360's duplicate handling explicit and EEC560 held out from tuning. See [SMEDIS review](SMEDIS_REVIEW.md).
3. **Terrain wind comparison:** [DTU Bolund](https://www.bolund.vindenergi.dtu.dk/the_bolund_experiment), SRC-080, is a measured complex-terrain wind/turbulence benchmark. Its [blind-comparison page](https://www.bolund.vindenergi.dtu.dk/blind_comparison), SRC-081, links boundary/topography and measurement material. This is a candidate acquisition, not downloaded/verified data here; check archive integrity, terms and frame definitions. Success would test terrain wind, not propylene dispersion.
4. **Dense-gas slope/obstacle comparison:** the existing SMEDIS inventory includes DAT638/DAT648 as candidate scaled, transient SF6 slope cases with zero listed mean wind. Preserve original/scaled columns and applicable similarity assumptions. DAT647's filename/header mismatch remains unresolved. These are not direct valley/propylene validation. No terrain case is accepted without a consistent source and accessible measurements.
5. **Site-specific evaluation:** require relevant local geometry, wind and release/measurement evidence. Neither a Bolund wind match nor an EEC550 concentration match establishes accuracy for an Adoshi tunnel/valley accident.

[HSE RR1165](https://www.hse.gov.uk/research/assets/docs/rr1165.pdf), SRC-067, illustrates version-specific dense-gas model evaluation and statistical performance measures, including a factor-of-two comparison. Use it as a protocol reference, not a regulator's certification of our model. Do not transplant arc-maximum statistics directly to individual receptors without documenting the difference.

For our planned receptor evaluation, freeze sample inclusion, zeros/detection limits, concentrations/units, averaging and error definitions before calculating scores. Report individual discrepancies and sensitivity; do not select a threshold or tuning case after seeing which result looks best. No universal numerical pass mark or percentage accuracy is adopted in this review.

## Practical decision

Build the first website with attributed terrain context and labelled fixture assessments. Run calculation development as bounded work packages: first a supported flat-ground source/concentration comparison, then a separately qualified terrain route. Terrain-aware predictions stay unavailable until those additional requirements are met. This is an implementation sequence, not a claim that the larger physics scope has been dropped.
