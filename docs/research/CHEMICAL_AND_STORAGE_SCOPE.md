# LPG, CNG and propylene: chemical and storage research scope

Confirmed by the user on 10 November 2026: the mentor named LPG, CNG and the chemical in the Mumbai-Pune accident. The existing incident evidence reports **propylene**; it does not identify a measured cargo composition. Cover lighter- and heavier-than-air release behaviour and storage as well as transport. No fourth chemical was named, so hydrogen, ammonia, chlorine and CO2 are not silently added to the accepted scope.

## Three fuel groups, not three interchangeable pure gases

| Confirmed group | Identity / composition | Useful starting reference | Density distinction | Release/storage modelling need |
|---|---|---|---|---|
| LPG | Commercial mixture primarily propane and butane; obtain actual composition | UKHSA LPG information, SRC-083; NIOSH LPG reference, SRC-086 | Ambient vapour generally heavier than air; cloud density still changes with phase, temperature and entrainment | Pressurised liquefied inventory; liquid/vapour opening, flashing/two-phase source, blowdown and applicable fire/failure scenarios |
| CNG | Compressed natural gas, methane-dominant mixture; not LNG | DOE AFDC, SRC-084; NOAA methane, SRC-085 | Methane is a lighter-than-air reference at comparable conditions; pressurised/cold near-source behaviour cannot be classified from molecular weight alone | High-pressure gas release, choked/underexpanded near field as applicable, real-gas state, momentum/buoyancy and time-varying vessel/cascade discharge |
| Propylene / propene | Pure-species reference CAS 115-07-1; actual product purity still needed | NOAA CAMEO, SRC-004; NIST, SRC-066 | Published ambient relative-vapour-density reference is above air | Pressurised liquefied source, flashing/phase behaviour and separately selected ignition/failure scenarios |

Sources: [UKHSA LPG](https://www.gov.uk/government/publications/liquefied-petroleum-gas-lpg-health-effects-and-incident-management/liquefied-petroleum-gas-lpg-general-information), [DOE CNG/LNG distinction](https://afdc.energy.gov/fuels/natural-gas-basics), [NOAA methane](https://cameochemicals.noaa.gov/chemical/8823), [NOAA propylene](https://cameochemicals.noaa.gov/report?key=CH4355).

Reference properties are not actual tanker measurements. Pure propane is a potential **declared surrogate** for some LPG studies; pure methane is a potential **declared surrogate** for CNG. Neither substitution is an accepted full-mixture model by default. Do not use propane's LEL, saturated pressure or experimental agreement as a propylene or arbitrary-LPG value. A single `light/heavy` switch is not a physical source model.

For an ideal-gas diagnostic only, density depends on pressure, mixture molecular weight and temperature (`rho = p * M / (R * T)`). Real-gas, droplets and condensed phases require the appropriate EOS/phase accounting. The cloud density relative to ambient, its momentum and the atmosphere determine its evolution. NOAA's density note explicitly warns that gas from pressurised/refrigerated storage may initially behave differently from its ambient relative-vapour-density label.

## Transport and storage must be explicit scenario types

| Asset / event family | Information needed beyond chemical name | Proposed first research case |
|---|---|---|
| LPG/propylene road tanker | Tank geometry/orientation, fill/state, damaged opening and pipe details, release direction/height, intervention history | One stationary unignited release with declared direct source or reviewed discharge calculation |
| Fixed LPG/propylene storage | Actual vessel type and protection, connected piping, inventory/state, nearby obstacles/vessels, terrain and ignition/external heating assumptions | One vessel/connection leak; fire and vessel-failure branches assessed separately |
| CNG cylinder/cascade on vehicle or storage site | Vessel number and volumes, connected/isolated banks, real-gas pressure/temperature, regulators/valves/relief path and effective opening | One defined gas leak with time-dependent source; do not model the whole cascade as instantaneously discharged without justification |
| Storage congestion/enclosure | Buildings/roofs/ventilation, obstructions, ignition and occupied receptor details | Separate applicability review before using unconfined explosion or outdoor-dispersion results |

Pressurised liquefied-gas BLEVE/fireball treatment is not automatically the correct mechanical-burst treatment for ambient CNG. Physical burst/fragment consequences, combustion overpressure and fire radiation are separate calculations. Do not call every storage failure a BLEVE or every delayed ignition an explosion. Geometry, phase and scenario conditions select the applicable model.

The first website can use an asset-type field and chemical/composition records without enabling every assessment. Preserve the established propylene D-001 walkthrough; add LPG and CNG presets only when their own fixture/input sheets are clearly documented. Storage interfaces and actual source calculations remain subsequent bounded implementation work.

## Engine candidate: HyRAM+

The [Sandia product page](https://energy.sandia.gov/programs/sustainable-transportation/hydrogen/hydrogen-safety-codes-and-standards/hyram/), SRC-089, identifies methane and propane alongside hydrogen, and lists unignited buoyant jets, jet flames/radiative flux and selected enclosure/unconfined overpressure models. It gives a **6.1** citation and separately links a **6.0** technical manual and **5.1** validation report. These are different versions; no installed version is claimed.

The official [API README](https://raw.githubusercontent.com/sandialabs/hyram/master/src/hyram/README.md), SRC-093, exposes physics entry points for fluid/source, mass-flow, plume, flame and overpressure work. This is a real software integration lead, not an assumed ALOHA API. It was read at mutable upstream `master`, not installed or pinned. [Upstream COPYING](https://github.com/sandialabs/hyram/blob/master/COPYING.txt), SRC-092, identifies GPLv3; review the selected release and third-party notices before integration/distribution.

**Proposed priority:** audit one pure-methane CNG-reference case and one pure-propane LPG-surrogate case for applicability and runtime before expanding custom CFD. No terrain capability, arbitrary mixture support, propylene support or existing-water/ice-source compatibility was established. The toolkit's QRA defaults are not local incident probabilities and will not be presented as such.

Evidence leads retained honestly:

- [CNG validation reference, SAND2019-13408](https://doi.org/10.2172/1763555), SRC-090: identified through Sandia's official index; full-text retrieval failed. No accuracy number or applicable pressure range is accepted from the title.
- [Propane validation, SAND2021-3244](https://www.osti.gov/servlets/purl/1821534), SRC-091: indexed abstract describes a propane surrogate and comparisons of flame dimensions with published experiments. Full text could not be retrieved in this review. This does not establish LPG-mixture, valley or all-hazard accuracy.
- The linked newer technical/validation reports also failed direct retrieval. They remain required reading for a version-specific audit, not completed evidence.
- [HSE RR1229](https://www.hse.gov.uk/Research/rrhtm/rr1229.htm), SRC-094, is a supplementary pipeline fireball/jet-model comparison lead; its official summary was reviewed. Pipeline evidence is not silently reclassified as tanker/storage validation.

Bounded audit exit: pinned version and dependency/licence record; documented supported fuel/state/geometry; reproduced reference inputs/outputs; meaningful numerical checks; runtime; explicit rejection of unsupported cases. Until then the engine remains a candidate. This review did not install, run or benchmark HyRAM+.

## Indian storage/transport standards: discovery, not compliance certification

The [OISD statutory-reference catalogue](https://oisd.gov.in/list-of-oisd-standards-in-various-statutory-regulations), SRC-087, identifies LPG-installation and small-bottling standards. Only an indexed catalogue excerpt was available; controlled editions and full requirements were not reviewed. Do not copy standards from unofficial mirrors or infer a universal separation distance from their titles.

The [PESO circular catalogue](https://www.peso.gov.in/web/index.php/en/circular), SRC-088, includes current CNG cylinder, dispensing and pressure-vessel items. Use Gas Cylinders Rules and Static and Mobile Pressure Vessels (Unfired) Rules as regulatory leads for a qualified, asset-specific review. The catalogue is not a consolidated rulebook, and this review does not determine which provisions apply to a particular facility or certify compliance. Preserve licence/certificate references as attributed asset records when a partner supplies them.

Do not mix workplace limits, IDLH, PAC, flammability fractions and model comparison criteria. [NIOSH's LPG IDLH basis](https://www.cdc.gov/niosh/idlh/68476857.html), SRC-086, specifically illustrates a flammability-based endpoint rather than a general population AEGL. Thresholds need a chemical, basis, source, revision and exposure/averaging context before use.

## What this changes in the project

The full research target is now three confirmed groups across transport/storage, with light/heavy behaviour and applicable dispersion/fire/explosion branches. Existing propane work is useful but covers only a reduced part of that target. First build D-001; then qualify a CNG light-gas case and an LPG heavy-gas case through their own input/validation records. Choose terrain work separately. No schedule or completed three-fuel physics engine is implied.
