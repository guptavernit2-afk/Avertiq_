# EEC550 source and weather: open-boundary prototype setup

9 November 2026. **Conditional 2D slab setup; no app and no field-validation claim.**

## Source selected

Use the existing **H00 calculated source**, not a replacement measurement:

| Quantity | Value / meaning |
|---|---|
| State | 204.260962 K, 102500 Pa, bulk density 1.942593 kg/m3 |
| Physical propane / total flow | 3.000000 / 10.845671 kg/s |
| Inlet speed | 18.1 m/s, horizontal along the assumed jet plane |
| Flow-consistent rectangle | Width 0.785440 m, height 0.392720 m, area 0.308458 m2 |
| Assumed centre height | 0.5 m; actual equivalent-window height remains historically unresolved |
| Thermodynamics | Gas plus water ice; all component mass is carried, not gas composition alone |

The reported rounded equivalent-source note remains **196 K, 20 mol%, 18.1 m/s, 0.78 x 0.39 m** in a separate record. H00 is an assumption-dependent equilibrium reconstruction, not an experimental correction. The configuration freezes its thermodynamic values against the tracked handoff.

The computational left boundary represents the equivalent window approximately 5 m along the original 30-degree jet from the nozzle. Computational x=0 is that downstream window, not the physical nozzle; no duplicate nozzle injection is included.

## 2D normalization and grid representation

The plane is vertical and aligned with the assumed jet heading, 30 degrees in the local magnetic-north coordinate frame. The solver is an infinite-slab approximation. The finite 0.785440 m width is used **only** to convert physical kg/s to kg/(m s) per metre of out-of-plane depth:

    component flow per depth = physical component flow / source width

Consequently the 2D propane input is about 3.8195 kg/(m s), not 3 kg/s injected independently through every metre of depth. Multiplying the per-depth result by the source width recovers the nominal physical source rate; this does not model finite-width side entrainment.

Each vertical boundary face receives the exact fractional overlap of its extent with the source window. Overlap lengths sum to the physical source height on every tested grid. Intersection centroids also preserve the gravitational-potential energy flux. The patch is not rounded to a whole cell.

Advective momentum and absolute pressure traction are recorded separately. Full prescribed normal momentum flux includes both; the earlier handoff's advective force is not the full pressure-bearing face flux. Energy flux includes enthalpy, kinetic energy and the actual gravitational-potential convention.

## Weather convention

Selected database values remain wind **2.73 m/s at 6 m**, wind-from **197.73 degrees**, roughness **0.006 m**, temperature **283.05 K**, pressure **102500 Pa**, and RH **99%**.

The documented neutral baseline uses the **shifted logarithmic profile**:

    U(z) = u_star / 0.4 * ln((z + 0.006) / 0.006)
    u_star = 0.1580603213 m/s

This preserves the earlier source/weather plan. The estimated 0.190 m/s friction velocity and L=-90 m are retained as evidence, not simultaneously forced into that neutral profile. Neutrality, the wall/profile convention and zero external heat flux are modelling choices. This prototype has no turbulence closure or maintained turbulent boundary layer.

The selected downwind heading is 17.73 degrees, oblique to the jet plane by -12.27 degrees. Projection gives **2.667639 m/s along the plane** and omits **-0.580176 m/s cross-plane** at 6 m. The original scalar speed is not silently reassigned to the projected component.

The raw wind angle is treated in the same local magnetic-north frame for this projection. Its independent compass datum was not recovered. No unverified declination correction is applied.

Humidity uses the adopted normalized liquid-water saturation closure for the atmospheric gas. The source retains its original H00 feed/energy interpretation. These conventions and the existing reference distinction remain explicit.

## Pressure datum and ground

The database pressure's measurement height is unknown. This setup **assumes 102500 Pa at ground**, while keeping H00 at 102500 Pa at the 0.5 m source centre. Hydrostatic ambient pressure there is approximately 102493.84 Pa, creating about **6.159 Pa source pressure excess**. That small excess is a datum artefact, not observed source thrust. The earlier zero-excess simplification is not enforced exactly here.

The ground is impermeable, free-slip and adiabatic in this inviscid prototype. This differs from a validated rough-wall atmospheric boundary layer. Ground heat transfer, turbulence and source turbulence are not reconstructed.

## Executable scope and validation

The versioned configuration is built by eec550_case.build_eec550_case(). The numerical domain defaults to **16 x 8 m**, with a **0.001 s smoke horizon**. The default has zero explicit thermal conductivity; positive overrides require an explicit synthetic-parameter label. Grid and time-step refinement are numerical checks only; this is not the developed 150 s comparison window.

validate_eec550_case() rejects inconsistent H00 ledgers, altered selected v1 meteorology, false sensor-readiness claims and inconsistent projection/geometry. Helpers provide projected point/cell-mean wind and exact source-face overlap. The focused case suite has **31 passing tests**.

The builder reads tracked first-party source/ambient records and records their normalized-text hashes; no original measurement workbook is redistributed or changed.

## Remaining comparison limits

This 2D plane cannot represent finite-width crosswind dispersion or evaluate all 30 original 3D receptors faithfully. Open boundaries are numerical approximations; reflection and backflow must be checked rather than called nonreflecting by assumption. Current short runs neither recover historical averaging indices nor resolve the 150/360 s duration discrepancy.

Do not score sensor concentrations or select a source/weather interpretation by best fit. A physical comparison still needs adequate dimensionality, turbulence/atmosphere treatment, spatial/time/domain convergence, computational scaling and reviewed phase assumptions.

[Input evidence](EEC550_INPUT_RESOLUTION.md) | [H00 handoff](EEC550_DISPERSION_HANDOFF.md) | [Integrated 2D equations](THERMAL_2D_MODEL.md)
