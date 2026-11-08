# Mathematics and validation plan

## Calculation chain

Tank/release conditions -> source term -> atmospheric dispersion -> threshold envelope -> geographic intersections.

For inventory M, track release to the environment separately from transfer to receiving tankers:

dM/dt = -release_rate(t) -transfer_rate(t)

The source model must handle the applicable phase and thermodynamic regime. A pressurised liquid discharge is not automatically identical to the airborne gas source.

A dispersion model estimates concentration as a function of position and time. Threshold polygons must identify hazard, threshold/unit, averaging time, assessment height, model assumptions and prediction period.

## Model decision

OpenFOAM Foundation 14 multicomponentFluid is selected conditionally for the first local EEC550 dispersion-only research comparison; see the [input/model plan](research/EEC550_COMPARISON_PLAN.md). No engine or equations have been selected for production use. Evaluate an established applicable source/dispersion workflow and integration/licensing constraints before implementation. Use reviewed ALOHA runs as references; do not assume an ALOHA automation API exists.

The original project's mass-based blast/fireball rings and geometric ellipse are not validated propylene release models.

## Test ladder

1. Verification: units, mass conservation, valid domains, coordinate transformations, wind-from convention, reproducibility, and numerical convergence where applicable.
2. First research comparison: prepare and verify the EEC550 flat-ground mixed-source setup; compare matching sensor concentrations only after source/averaging gates are reviewed. Relevant official ALOHA examples can be separate screening checks with assumptions and version differences documented.
3. Matched PHAST comparison: use the same source inputs and assessment definitions; report stage-by-stage differences.
4. Experimental validation: select applicable SMEDIS cases using measured source, weather and concentration records. Keep evaluation cases separate from tuning cases.
5. Sensitivity: vary justified uncertain inputs and report resulting changes; do not attach unsupported probability/confidence claims.
6. Tabletop review: evaluate provenance, missing-data handling, observation conflicts, assessment updates and handover clarity.

## Selected experimental starting point

The [SMEDIS review](research/SMEDIS_REVIEW.md) recommends EEC550 as the initial unobstructed propane case, EEC360 as a smaller-source comparison after duplicate-record handling is agreed, and EEC560 reserved from future fitting. Start with documented downstream equivalent sources for dispersion-only tests. Source-model validation remains separate. All selections are conditional on engine capability and agreed input/measurement handling. No model runs or accuracy claims exist.

## EEC550 follow-up

The [input-resolution review](research/EEC550_INPUT_RESOLUTION.md) confirms the local magnetic-north coordinate frame and shows that the original trial contained fenced and unfenced phases. REDIPHEM lists a 360 s full release; SMEDIS B27 lists 150 s. Preserve that discrepancy. The conditional first comparison uses a developed unfenced plume and a separate 150 s model averaging window, not a fresh 150 s pulse. Exact historical averaging indices and actual downstream inlet elevation remain unverified. A neutral weather baseline is declared separately from estimated unstable sensitivity; thermal/humidity/turbulence setup still needs review. No results exist.

## PHAST comparison checklist

Ask the mentor for:
- Product/version and available modules, including any CFD extensions.
- Agreed chemical property basis and complete tank/release input sheet.
- Wind height, stability method, surface conditions and other atmosphere settings.
- Source coordinates/height/orientation and concentration definitions.
- Thresholds, units, averaging time, receptor height and assessment period.
- Permitted input/output exports and report redistribution terms.

Compare source rate and state first, then concentration/distance results and threshold geometry. If possible, also compare dispersion with an identical defined source to separate source-model differences from dispersion-model differences.

PHAST agreement is model benchmarking, not experimental validation. Differences may result from legitimate assumptions and should be explained rather than hidden or tuned away.

## Metrics and gates

Record absolute/relative errors where meaningful for release rate, threshold distance and selected measurement locations/times. Handle zero values and below-detection observations explicitly. Add time-step/grid sensitivity when applicable.

The [EEC550 sensitivity design](research/EEC550_SENSITIVITY_STUDY.md) proposes internal numerical screening tolerances and a materiality triage rule before any run. These are study choices, not experimental accuracy requirements or SMEDIS pass marks. Review implementation-specific settings and experimental performance expectations before evaluation. No completed runs, pass results or accuracy claims exist.

## Terrain boundary

Version 1 displays terrain and flags features for investigation. An ALOHA/free-field footprint over terrain remains subject to its original assumptions. Do not validate terrain-dependent gas movement using a visual overlay or synthetic detector points.

Actual Adoshi plume validation requires field release/weather/concentration records not currently available.
