# Physics requirements for chemical-truck assessments

Reviewed 10 November 2026. Model requirements and proposed selection decisions, not implemented hazard calculations. Reference IDs resolve in the [source register](../../data/source-register.csv).

The user confirmed **LPG, CNG and the Mumbai-Pune incident chemical (reported propylene)** as the chemical scope, including light- and heavy-gas behaviour and storage. See the [chemical/storage matrix](CHEMICAL_AND_STORAGE_SCOPE.md). The earlier one-propylene-truck walkthrough is the first interface case, not the entire research scope.

## Start with the source, not a radius

The release calculation needs chemical/composition, tank dimensions/orientation, inventory/fill, temperature, absolute pressure, opening/pipe details, location relative to liquid level, source direction/height and time history. Record shutdown and transfer separately from release to the atmosphere. Tank pressure must be distinguished from gauge pressure; inputs must be thermodynamically consistent.

A pressurised liquid release may flash, entrain air, carry droplets or rain out. The mass leaving a tank is not necessarily the same as the airborne vapour source. A direct-source case may bypass vessel-discharge calculation only if it declares which downstream source it represents. The existing H00 record is a conditional **propane** equivalent-source study, not a propylene tanker-hole model. Existing equilibrium closure does not establish discharge coefficients, droplet slip, breakup or phase-relaxation rates.

[NOAA technical documentation](https://response.restoration.noaa.gov/sites/default/files/ALOHA_Tech_Doc.pdf), SRC-062, separates source, dispersion, VCE and thermal models. Its reviewed edition is **5.4.4, November 2013**; [NOAA's product page](https://response.restoration.noaa.gov/oil-and-chemical-spills/chemical-spills/response-tools/aloha.html), SRC-082, lists **5.4.7**. Never identify a reference edition as the version actually run; no ALOHA run occurred here.

## Scenario branches and outputs

| Branch | Additional scenario information | Expected calculation output | Current Avertiq status |
|---|---|---|---|
| Unignited gas release | Source state/geometry/history, wind profile, stability/turbulence, surface conditions | Gas concentration versus x/y/z/time; averaging and gas-phase basis | Research prototypes only; no field-ready plume |
| Flash-fire assessment | Applicable dispersed flammable cloud and ignition assumption | Flammable-cloud extent with declared criterion | Not implemented; not a blast-radius substitute |
| Jet fire | Sustained burning source, geometry/orientation, fuel properties | Incident heat flux versus target location and relevant duration | Not implemented |
| Pool fire | A physically supported liquid pool, spreading/evaporation and ignition | Pool/flame behaviour and heat flux | Not implemented; do not assume a persistent ambient propylene pool |
| BLEVE / fireball | Applicable pressurised-vessel failure state and participating inventory | Model-specific fireball radiation/duration; other failure effects separately | Not implemented; collision alone does not establish this branch |
| Vapour-cloud explosion (VCE) | Participating flammable cloud, ignition timing/location, congestion/confinement, reactivity | Peak overpressure; impulse/duration where supported | Not implemented |
| Mechanical vessel burst / fragments | Vessel pressure/state, failure mechanism and geometry | Separate applicable mechanical/fragment consequences | No selected model; must not be implied by VCE contours |

These branches are proposed project requirements, not assigned probabilities. Do not merge different scenarios into one purported instantaneous event. Consequence contours alone are not a probabilistic risk assessment.

## Defensible model routes

**Dispersion:** retain the custom coupled solver for controlled verification. Consider an established applicable consequence workflow for initial flat-ground comparison. [HSE RR1168](https://www.hse.gov.uk/research/rrhtm/rr1168.htm), SRC-068, evaluates a named DRIFT version for pool vapour, flashing jets and instantaneous flashing releases. That establishes scenario-specific evaluation practice, not suitability of our code or access to a freely redistributable DRIFT service.

**Radiation:** the reviewed NOAA technical model uses a solid-flame approach with incident flux represented by `q = E * F * tau`: emitting-surface flux, geometric view factor and atmospheric transmission. Model flame size/shape and duration, rather than equating a fireball's physical radius with a heat-exposure contour. A point-source approximation, if ever used, needs a stated applicability range and benchmark; the older prototype's equation is not accepted by inheritance. Source: SRC-062, section 6.

**Explosion:** NOAA's reviewed VCE method is BST-based and assumes an unconfined cloud. [DNV's 3D explosion description](https://www.dnv.com/siteassets/images/pdf-documents/phast-3d-explosions---flyer.pdf), SRC-069, describes Multi-Energy/BST approaches using cloud interaction with congested regions and outputs including overpressure and impulse. Select a method for the actual scenario. Whole tanker inventory is not automatically participating cloud mass; a universal TNT factor is not selected. A tunnel or partially confined accident needs a separate applicability review.

**Terrain:** neither a Gaussian ellipse drawn in JavaScript nor a free-field footprint draped over elevation satisfies valley dispersion. See the [terrain plan](TERRAIN_AND_VALIDATION.md). No universal all-physics production engine is selected.

**LPG/CNG screening candidate:** [Sandia HyRAM+](https://energy.sandia.gov/programs/sustainable-transportation/hydrogen/hydrogen-safety-codes-and-standards/hyram/), SRC-089, is a relevant candidate to audit for methane/propane release, jet-flame and selected overpressure calculations before writing new formulas. Its public [Python API description](https://raw.githubusercontent.com/sandialabs/hyram/master/src/hyram/README.md), SRC-093, makes an integration feasibility study plausible. It is not accepted as a terrain, mixed-LPG or propylene model here. See the [bounded audit plan](CHEMICAL_AND_STORAGE_SCOPE.md#engine-candidate-hyram).

## Chemical identity and thresholds

[NOAA CAMEO](https://cameochemicals.noaa.gov/report?key=CH4355), SRC-004, identifies propylene as CAS 115-07-1 / UN 1077 and lists LEL 2 vol% and UEL 11.1 vol%. It reports no AEGL or ERPG values, while displaying PAC-1/2/3 of 1500/2800/17000 ppm attributed to DOE 2024. These are source-specific reference values, not newly approved operating thresholds. [NIST propene data](https://webbook.nist.gov/cgi/cbook.cgi?ID=C115071&Mask=1C), SRC-066, provides an independent phase-data reference for future property checks. Do not substitute propane or propylene oxide.

[DOE's current PAC portal](https://apps.emhub.energy.gov/pacteel), SRC-072, says updated 26 October 2026. Its landing page was reviewed, but a current chemical-specific propylene record was **not obtained**. Therefore NOAA's DOE-2024 values are not certified as the latest DOE values. [DOE's PAC explanation](https://www.energy.gov/nnsa/protective-action-criteria-pac-aegls-erpgs-teels), SRC-073, explains the inclusion of AEGL/ERPG/TEEL sources. Preserve endpoint type, revision and duration; PAC must not be relabelled AEGL. [EPA's reviewed AEGL table](https://www.epa.gov/aegl/access-acute-exposure-guideline-levels-aegls-values), SRC-074, did not return CAS 115-07-1 in the accessible page; this is not a search of every unpublished assessment.

| Reference convention | Values recorded for comparison design | Handling in Avertiq |
|---|---|---|
| ALOHA flammable LOCs | 60% LEL and 10% LEL defaults | Model-reference settings accounting for patchiness; not universal evacuation boundaries |
| ALOHA radiation LOCs | 10, 5 and 2 kW/m2 defaults | Preserve exposure-duration context; not universal injury or operating guarantees |
| ALOHA overpressure LOCs | 8, 3.5 and 1 psi defaults | Excess/peak pressure; effects depend on circumstances; not fragment contours |

References: [flammable LOCs](https://response.restoration.noaa.gov/oil-and-chemical-spills/chemical-spills/resources/flammable-levels-concern.html), SRC-065; [radiation LOCs](https://response.restoration.noaa.gov/oil-and-chemical-spills/chemical-spills/resources/thermal-radiation-levels-concern.html), SRC-063; [overpressure LOCs](https://response.restoration.noaa.gov/oil-and-chemical-spills/chemical-spills/resources/overpressure-levels-concern.html), SRC-064. No row is adopted as an Indian regulatory criterion or automatic response instruction.

For a matching gas-phase volume/mole basis, `vol% = 100 * mole_fraction` and `ppm = 1e6 * mole_fraction`. With the cited 2 vol% LEL, the arithmetic reference is 20000 ppm: 10% LEL is 2000 ppm, not 10 vol%. This is a unit conversion, not a detector calibration. Do not convert aerosol-inclusive mass fraction directly to gas ppm. Mass-concentration conversion additionally needs molecular weight, temperature, pressure and an applicable EOS.

## Verification before a calculated layer is enabled

1. Freeze one scenario/input sheet, property sources, model/version, thresholds, units and sampling definitions.
2. Check component mass, energy references, phase limits, coordinate/wind conventions and rejected inputs. Match source terms before comparing final distances.
3. For numerical flow, check source resolution, boundaries, domain, mesh/time sensitivity and physical runtime feasibility at matched conditions. Do not extrapolate 1 ms startup to a developed plume.
4. Reproduce a documented applicable reference case; record differences from its version/chemistry/scenario. A reviewed NOAA example is not a measured propylene tanker accident.
5. Freeze the experimental comparison recipe and evaluate actual measurements where applicable. A PHAST comparison is benchmarking; synthetic observations cannot validate a physical model.
6. Export metadata through the [assessment contract](../ASSESSMENT_CONTRACT.md), including unsupported effects and review status. A failure leaves the layer unavailable with a reason.

No custom blast or fire implementation is approved as correct by this specification. Next calculation work should select and finish one bounded case rather than adding several untested formulas to the map.
