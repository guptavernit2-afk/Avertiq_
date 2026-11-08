# EEC550 input preparation and first local model

Reviewed 8 November 2026. User preference: use a model we can run ourselves without a paid licence. Scope: planning and source review only.

## Follow-up correction

Read the [input-resolution findings](EEC550_INPUT_RESOLUTION.md) before using this plan. Original trial reports establish magnetic-north axes and a fenced/unfenced sequence; REDIPHEM lists a 360 s full release, conflicting with SMEDIS B27=150 s. The first comparison is now a conditional developed-plume mean comparison, not a fresh 150 s pulse. Actual equivalent-inlet elevation and exact SMEDIS averaging indices remain unknown.

## Decision and boundaries

Select **OpenFOAM Foundation 14, multicomponentFluid**, as the first research comparison platform, conditional on the readiness gates below. Use a nonreacting, transient, variable-density gas calculation with energy, species transport and gravity. An ideal-gas mixture is a proposed thermodynamic approximation requiring property review; do not use a passive scalar in constant-density air or a small-density-change Boussinesq approximation for this cold dense inlet.

This choice is an engineering inference from the documented source and solver capabilities, not evidence of validated performance. The official solver reference documents compressible multicomponent flow, energy transport and optional buoyancy; the download site documents GPLv3 and Windows through WSL. Pin the exact 14 package/patch, operating system, property files and settings when installation is requested. Do not mix instructions from the OpenCFD fork with Foundation 14.

First compare dispersion over flat experimental ground. Do not model the pressurised nozzle, flashing droplets, ignition, propylene, Adoshi terrain or tunnels in this test. Do not claim realtime performance or that CFD automatically makes terrain predictions correct. Hardware requirements and practical run time remain unassessed; no installation or execution was performed.

## Why not start this case with SLAB?

EPA provides SLAB source code and examples, making it a useful later screening candidate. However, the reviewed user manual's horizontal/vertical jet initialization assumes pollutant mass fraction 1. Its source temperature handling clamps values below the pure substance's boiling point. Horizontal jets are initialized downwind, and ambient pressure is fixed at one atmosphere.

The preferred EEC55 dispersion-only source is instead 20 mol% propane in air at 196 K, colder than pure propane's listed normal boiling point of 231.1 K. Entering it as pure propane would change composition, temperature, density and buoyancy. The measured wind also differs from jet direction. Do not fabricate a pseudo chemical or alter its boiling point to bypass these restrictions.

SLAB could still test a separately reviewed pure-propane post-expansion two-phase source, but that requires flash-state and expanded-area inputs and tests a different source chain. The 15.5 mm physical nozzle is not automatically its expanded source area. This is deferred, not rejected as a model generally.

Manual evidence: printed pp. 43–45 and 49–53 (PDF pages 49–51 and 55–59, one-based). Targeted input review only, not a complete audit of the program. [EPA model page](https://www.epa.gov/scram/air-quality-dispersion-modeling-alternative-models), [SLAB manual](https://gaftp.epa.gov/Air/aqmg/SCRAM/models/nonepa/slab/SLAB.PDF).

PHAST remains a later mentor-run benchmark if access becomes available. Agreement between two models is not experimental validation.

## Evidence and provenance

Local originals:
- Workbook: data/raw/2026-11-08/smedis-extracted/batch1/eec550.xls, worksheet **Sheet 1**.
- Equivalent source: data/raw/2026-11-08/smedis-extracted/batch1/equivsrc.txt, dated 6 February 1998.
- Supporting variable definitions and revision history: see the [SMEDIS review](SMEDIS_REVIEW.md).
- Originals are ignored in Git; archive download URLs/hashes are in the [manifest](../../data/public/external-download-manifest.json). Input lineage is in the [structured record](../../data/public/eec550-input-plan.json).

These are experimental coordinates and weather, not Adoshi data. The follow-up REDIPHEM trial table supports 6 September 1989 at 08:30 for Lathen 55; time zone and exact observation-window alignment remain unverified. Use relative model time. Public availability does not establish unrestricted redistribution rights. Do not commit full measurement exports pending terms review.

## Inputs: physical release, retained as context

| Quantity | Original value | Workbook cell | Treatment |
|---|---|---|---|
| Chemical / molecular weight | propane / 44.1 g/mol | B6/B7 | Physical chemical properties |
| Normal boiling point | 231.1 K | B9 | Context, not inlet temperature |
| Nozzle diameter | 0.0155 m | B13 | Physical nozzle, not equivalent inlet |
| Physical release point | (0,0,0.5) m | B15:B17 | Original local coordinates |
| Jet azimuth / inclination | 30 degrees from N / 0 degrees | B18/B19 | Horizontal; convention needs confirmation |
| Phase field | 1.0 | B20 | Definitions describe pre-release liquid fraction; not post-flash quality |
| Exit temperature / pressure | 13.3 C / 10 atm | B21/B22 | 286.45 K; pressure absolute/gauge unresolved |
| Propane release rate | 3 kg/s | B23 | Do not equate to total mixed-inlet flow |
| Start / duration | 08:30:00 / 150 s | B24:B27 | Preserve original; full-trial summary lists 360 s; 450 kg is interval arithmetic only |
| Upstream concentration / effective MW | 1 / 98.8 g/mol | B44/B45 | Do not substitute for mixed-inlet fraction or propane MW |

Liquid-property strings in B8/B10 are retained in the structured record; they are not needed to bypass discharge physics in this dispersion-only test.

## Inputs: proposed downstream inlet

The batch note lists **EEC55**, not the full EEC550 identifier. Follow-up cross-references strongly support the unobstructed EEC55-to-EEC550 mapping; adopt it for planning while retaining that the note has no explicit full key.

| Quantity | Note value | Proposed interpretation |
|---|---|---|
| Downstream distance | 5 m | Source-plane displacement; axis/reference unresolved |
| Velocity | 18.1 m/s | Mixed-source velocity; direction/profile need review |
| Propane molar concentration | 20% | Mole fraction 0.20, not mass fraction 0.20 and not %LEL |
| Temperature | 196 K | Fully vaporised mixture; do not clamp to pure-propane boiling point |
| Half-width | 0.39 m | Full width 0.78 m |
| Geometry statement | height = half-width | Height 0.39 m; area 0.3042 m2 |

**Missing:** source-plane centre height, displacement direction (along jet or wind), velocity/composition profiles, inlet turbulence, air/humidity basis and timing relative to physical release. Do not automatically use physical nozzle height 0.5 m for the downstream rectangle. A box at the wrong elevation changes ground interaction.

Conditional arithmetic check, not a new measurement: assume dry air MW=28.965 g/mol, ideal mixture and pressure 102500 Pa. Mixture MW=31.992 g/mol; propane mass fraction = (0.20*44.1)/31.992 = about 0.2757. Density = p*M/(R*T), using M in kg/mol. Total flow = density*area*velocity; propane flow = total flow*propane mass fraction. This gives about 3.05 kg/s propane, close to the nominal 3 kg/s but not identical. Preserve the rounded source note; do not adjust its area/concentration to force agreement. Review pressure, humidity and rounding before defining a conservation tolerance.

## Inputs: atmosphere and ground

| Quantity | Value | Cell | Treatment |
|---|---|---|---|
| Measured wind-from | 197.73 degrees | B29 | Primary directional evidence |
| Direction standard deviation | -999 | B30 | Missing marker, not physical |
| Ideal wind-from | 210 degrees | B31 | Separate directional sensitivity only |
| Experimental X-axis azimuth | 90 degrees from N | B32 | Y is magnetic north per R582; retain local frame |
| Corrected wind / height | 2.73 m/s at 6 m | B33/B34 | Preserve measurement correction |
| Friction velocity | 0.190 m/s, estimated | B35 | Uncertain, not independently exact |
| Roughness length | 0.006 m | B36 | Not wall-function sand-grain height |
| Monin–Obukhov length | -90 m, estimated | B37 | Suggests instability; reconcile with class D |
| Stability class | D | B38 | Alternative atmosphere description, not interchangeable with L |
| Cloud description | morning haze lifting | B39 | Do not invent cloud octas |
| Ambient temperature | 9.9 C = 283.05 K | B40 | Free atmosphere |
| Ambient pressure | 1.025 bar = 102500 Pa | B41 | Different from release pressure |
| Relative humidity | 0.99 = 99% | B42 | Review water-vapour/condensation sensitivity |
| Ground slope / fences | 0% / 0 | B43/B28 | Flat unobstructed benchmark |

Under the meteorological wind-from convention, measured downwind is 17.73 degrees from N; this differs from the 30-degree jet by 12.27 degrees. Ideal wind aligns them. Do not silently rotate measurements to erase this difference. R582 confirms the local magnetic-north frame; use the transform and cardinal-direction checks in the follow-up findings.

Choose a single consistent atmospheric-boundary-layer (ABL) formulation. The follow-up defines a simplified neutral baseline matched to corrected wind and roughness, with derived u_star=0.15806 m/s (kappa=0.4); estimated L=-90 m is a separate consistent unstable sensitivity. A tentative closure is transient RANS k–epsilon with reviewed ground functions and thermophysical transport. Reconcile measured U, estimated friction velocity, roughness and estimated L; they need not fit one neutral log law exactly. The neutral formula U(z)=u*/kappa*ln((z+z0)/z0) is only a diagnostic, not the final unstable profile. Test an empty domain before adding gas so boundary-condition drift is not mistaken for plume physics. Record ground temperature/heat exchange and water treatment as unresolved assumptions; high humidity plus a cold source warrants review. Do not initialize the atmosphere with temperatures measured inside the plume.

## Observations and matching

- **Primary:** Sheet 1 A95:E124: 30 records of X, Y, height, mean concentration (%) and standard deviation (%). Heights are 0.05, 1, 2 and 4 m. Preserve original rows, zeros and units. No duplicate coordinate triples were found.
- Mean averaging duration is 150 s (B48). Exact start/end and instrument time alignment need confirmation; a 150-second release does not prove that every reported concentration used t=0–150 s.
- Predict at actual sensor coordinates/heights; compare mole/volume percent on the documented basis, not mass percent, ground-level maxima or an arbitrary polygon.
- Conversion: x_propane=(Y_propane/M_propane)/sum(Y_i/M_i); concentration percent=100*x_propane. Check the instrument basis before final scoring.
- Reported standard deviation is concentration variability, not a standard error or a 95% confidence interval. A RANS mean prediction does not reproduce measured temporal fluctuations automatically.
- Supplementary arc summaries: A89:D92, distances 32/45/54/64 m at 0.05 m height. These derive from sensors; do not count as independent additional validation points.
- Auxiliary wind/temperature records remain available. Identify upwind/background sensors before using them to constrain atmosphere.
- Detection limits and measurement uncertainties are not yet established. Keep zero observations; do not insert arbitrary epsilon values for logarithmic scores.

## Mathematics and checks before judging accuracy

1. **Source and unit checks:** separate physical propane mass flow from mixed inlet flow; track mole-to-mass conversion, dimensions and source plane displacement. Document any discrepancy.
2. **Conservation:** integrate propane storage plus boundary outflow and compare with integrated inlet flux, accounting for open-boundary inflow/background. Confirm species sum to one, bounded nonnegative concentrations and sensible temperatures.
3. **Numerics:** use a 3D flat domain covering all sensors with upstream/lateral/top/outlet buffers. Choose dimensions and source resolution after mapping is confirmed; do not invent a final mesh here. Compare at least three sensible spatial resolutions, reduce time step, and enlarge domain. Demonstrate stable receptor predictions and mass balance. Resolve the 0.39 m inlet and 0.05 m sensors adequately.
4. **Averaging:** establish the ABL and developed unfenced plume, then average for 150 s with maintained inlet. The model window is not a recovered historical window. Do not score a fresh 150 s pulse or claim fence-removal dynamics without original timing records.
5. **Experimental scores:** retain a paired observed/predicted table with row IDs. Start with MAE (percentage points), RMSE and mean signed bias over all records; report results by height too. Define bias as mean(predicted-observed). Report factor-of-two and geometric metrics only on explicitly reported eligible positive pairs; show omitted count and zero behaviour separately.
6. **Supplementary comparisons:** arc peak concentration/width and vertical profiles after matching their definitions. Do not move the cloud centre or sensors to improve scores.
7. **Predeclare criteria:** numerical tolerances and experimental performance expectations must be recorded before evaluation with mentor/modeller input. No arbitrary universal pass mark is claimed. If tuning is needed, label EEC550 developmental and keep EEC560 excluded.

Example RMSE definition: sqrt(mean((predicted-observed)^2)), in concentration percentage points. Numerical convergence is verification; comparison with measured gas concentrations is validation. Neither alone validates the discharge model, Adoshi incident reconstruction or terrain routing.

## Readiness and next work

| Gate | Status | Required evidence |
|---|---|---|
| Source and original observations preserved | Prepared locally | Workbook/archive hashes; cell lineage |
| Family mapping and inlet placement | Mapping supported; actual window placement open | Original trial documentation or recorded modelling interpretation/sensitivity |
| Measurement basis/window | Open | Instrument definition and timing, or explicit conditional comparison |
| ABL, humidity, heat and inlet turbulence | Open | Consistent documented setup and sensitivity plan |
| Solver availability and thermophysical capability | Documentation reviewed | Later pin package/version and prove no-gas/species/gravity behaviour |
| Mesh, domain, time and conservation tolerances | Open | Set before evaluated run |
| Accuracy, numerical results, model validation | Not performed | Reproducible run records and discrepancy report |

Next research action: obtain original BA-Propane/EEC trial documentation through SMEDIS references, resolve these inputs and review the complete input sheet. If evidence remains unavailable, retain a clearly labelled sensitivity study; do not call its assumed geometry a faithful reproduction.

## Model references

- [Foundation 14 solver reference](https://cpp.openfoam.org/v14/classFoam_1_1solvers_1_1multicomponentFluid.html): multicomponent flow, energy and optional buoyancy.
- [Foundation download and licence](https://openfoam.org/download/): free GPLv3 software; select release 14 and pin package at installation.
- [Official Windows route](https://openfoam.org/download/windows/): WSL2/Ubuntu instructions; nothing installed in this task.
- EPA SLAB links above. [Earlier SMEDIS review](SMEDIS_REVIEW.md) records experimental sources and limitations.

## Sensitivity study planned

The [version-1 sensitivity plan](EEC550_SENSITIVITY_STUDY.md) defines nine core physical cases, assumption labels, timing diagnostics, proposed numerical screening limits and comparison rules. It develops the conditional comparison route without resolving the original missing evidence. No execution is authorized by this planning update and no model has been run.
