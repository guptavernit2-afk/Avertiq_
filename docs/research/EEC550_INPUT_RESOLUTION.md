# EEC550: inlet, timing and weather follow-up

**Phase-review update, 8 November 2026:** the [humidity/phase review](EEC550_PHASE_REVIEW.md) does not accept the proposed gas-only baseline under the current inlet conditions. The sensitivity matrix is held pending source-state and phase/enthalpy reconciliation. Original assumptions below remain planning history, not runnable inputs.

8 November 2026. Research only. This review supersedes the timing interpretation in the first input plan; no model configuration, installation or run was performed.

## Result

Some gaps can be resolved; others cannot be recovered from the available public files. We now have a documented coordinate frame, stronger case identification, a corrected comparison-time interpretation and an explicit weather baseline. The downstream inlet's actual centre height and the exact SMEDIS averaging interval remain unverified. Keep run_ready=false for a faithful reproduction. An exploratory calculation would require explicit assumption labels and separate reporting.

## Evidence acquired and checked

| Reference | Review locations | What it contributes |
|---|---|---|
| Nielsen & Jensen, 1991, Risø-M-2923 | Printed pp. 7–17, PDF pp. 10–20; scanned pages visually inspected | Test layout, removable fence, instrumentation, processing and gas-affected profiles |
| Jones et al., 1992, SRD/HSE R582 | Printed pp. 6–7 and Table 1 pp. 49–50; PDF pp. 9, 30–31; coordinate/timing pages visually inspected | Original axes and separate fence/no-fence intervals |
| Webber et al., 1994, AEA/CS/FLADIS volume 2 part 1 | Part IIIb sections 2.1–2.3 and Appendix 1; PDF pp. 50–51, 88–89 | Historical source modelling context; physical source height confirmation |
| Nielsen & Ott, Risø-R-845(EN) | Section 3.4 Lathen, PDF p. 27; Table 30, PDF p. 51 visually inspected | Provenance and limitations of meteorological estimates |
| SMEDIS protocol v2.0 | Appendix 3 PDF pp. 127–128; Appendix 5 FAQ p. 139 | Useful trial interval, averaging duration and response-table clarification |
| SMEDIS workbook, revision history and batch note | Existing originals and cell lineage | Current corrected inputs and downstream mixed source |

Four newly downloaded PDFs remain local and ignored; exact URLs, sizes and SHA-256 values are in the [manifest](../../data/public/external-download-manifest.json). Review is targeted, not a complete independent review of every report.

## 1. Inlet placement

**Resolved coordinate frame:** R582 identifies the release origin and Y axis toward magnetic north. Together with the workbook's X azimuth of 90 degrees, use local X east, Y magnetic north, Z upward. Keep this experimental frame; do not apply an unverified magnetic-declination correction or place it on Adoshi's map.

**Case mapping:** the SMEDIS catalogue identifies EEC550 as unobstructed and EEC551 as its fenced counterpart. Original EEC55 reports describe the removable-fence experiment; matching sensor coordinates and nozzle conditions strongly support this mapping. Adopt EEC55's unfenced portion as EEC550 for planning. The equivalent-source note itself still lacks a full EEC550 key; this is a documented cross-reference inference.

**Confirmed physical height:** workbook B17 and the AEA example both put the original nozzle 0.5 m above ground. Neither proves the centre height of the fully vaporised window 5 m away.

**Retain the source note:** 5 m downstream, 18.1 m/s, 196 K, 20 mol% propane, rectangle 0.78 m wide by 0.39 m high. Its centre height and exact meaning of downstream were not found in reviewed material. The older AEA circular-to-square source mapping is a different model interface; it cannot fill in this rectangular-window height.

Proposed exploratory interpretation, clearly assumed:
- Put the window 5 m along the original 30-degree horizontal jet, normal to that jet. Centre = (2.500, 4.330, 0.500) m. Vertical extent = 0.305 to 0.695 m.
- Use uniform inlet composition, temperature and speed only as a top-hat approximation; original profiles/turbulence remain missing.
- At 18.1 m/s, the assumed velocity components are (9.050, 15.675, 0) m/s.
- A ground-touching rectangle, centre Z=0.195 m, is an alternative geometry sensitivity, not a measured lower bound.
- A displacement along measured downwind instead gives XY=(1.523,4.763) m. Treat this only as a separate interpretation sensitivity, not the default replacement for jet direction.
- If results materially depend on these interpretations, no unique validation claim is supportable until source documentation is recovered.

Equations: for azimuth a clockwise from local north, displacement = s*(sin(a),cos(a)); horizontal source-plane transverse direction = (cos(a),-sin(a)). All sensor coordinates stay fixed in the original frame. A wind from south (180 degrees) must produce positive Y flow; a wind from west (270 degrees) must produce positive X flow.

## 2. Measurement timing

**Correction to the earlier plan:** the physical EEC55 experiment contains a fenced phase, a fence-removal transition and an unfenced phase. R582 used sensor-dependent steady periods: for example, sensor 19 at (13.9,28.1) m has its unfenced interval listed as 303–516 s on that analysis's time axis. This is not a 150-second interval and is not proved to be the SMEDIS processing window.

REDIPHEM Table 30 lists Lathen 55 on **6 September 1989 at 08:30**, flow **3 kg/s**, full-release duration **360 s**. This supports the date/year and longer-release interpretation, but its clock reference/time zone is not established. Its older 3.2 m/s wind value must not supersede revised SMEDIS wind.

SMEDIS B27 and B48 both list 150 s. Preserve those fields, but the 150 s release-duration entry conflicts with the full-trial summary; do not infer that the original full release lasted only 150 s or that observation averaging began at release onset. The protocol defines averaging within the useful trial portion and allows sensor-dependent time ranges. Exact SMEDIS start/end times and alignment to the original recording remain unavailable.

**Adopted comparison policy:**
1. Treat the first comparison as a developed, unobstructed, continuous-plume mean comparison.
2. First establish the clean-air boundary layer, then establish the unfenced plume. Start a labelled model averaging window only after receptor means and mass balance stabilize under predeclared criteria.
3. Average for 150 s of model time, with the inlet maintained throughout this window. Record the simulation's own start/end independently of historical clock time.
4. This is a conditional stationary comparison, not a replay of the fence drop or recovery of the missing historical window. A deterministic RANS mean cannot reproduce wind meander or sensor fluctuation histories simply by running 150 s.
5. If exact historical timing or transition behaviour is required, obtain original time series, fence-event log and SMEDIS processing indices before running that comparison.

The old 3 kg/s * 150 s = 450 kg calculation is arithmetic over the listed interval only, not measured full-trial consumption or tank inventory. Do not implement a fresh 150-second pulse and score its startup-diluted mean against developed experimental concentrations.

## 3. Weather assumptions

**Use revised SMEDIS values as the primary input record:** wind 2.73 m/s at 6 m, wind-from 197.73 degrees, roughness 0.006 m, temperature 283.05 K, pressure 102500 Pa, RH 99%, flat ground. The revision history explicitly supersedes 3.19 m/s. Historical modelling examples use different wind values; do not replace the revised value with them.

**Why estimated values need care:** the REDIPHEM report says Lathen stability was generally estimated from wind/cloud information, and L from stability/roughness, rather than direct flux measurements. Do not count class D, L=-90 m and estimated friction velocity as three independently measured constraints. Pressure provenance is also mixed across historical descriptions; retain workbook pressure as the selected database input, not a newly verified barometer reading.

**Adopted simplified baseline:** neutral class-D atmosphere, zero imposed background sensible heat flux, a neutral log wind profile matched to U(6 m)=2.73 m/s and z0=0.006 m. This is a modelling choice, not proof that the historical atmosphere was exactly neutral. Gas-induced density/thermal buoyancy remains active.

With a stated kappa=0.4 and zero displacement height:
U(z) = u_star/kappa * ln((z+z0)/z0)
u_star = kappa*2.73 / ln((6+0.006)/0.006) = 0.15806 m/s.

Thus using estimated u_star=0.190 in that same profile would give U(6)=3.28166 m/s, not 2.73. Retain 0.190 in the evidence record; use the derived 0.15806 only in this chosen neutral setup. Changing kappa or wall/profile convention requires recomputation.

**Mandatory sensitivities and remaining setup:**
- Compare a consistent weakly unstable atmosphere using estimated L=-90 m; specify its similarity functions, temperature profile and heat flux together before implementation. Do not merely insert L into a neutral inlet.
- Keep ideal wind-from 210 degrees as a separate directional case. Measured downwind is 17.73 degrees, with U at 6 m = (0.83137,2.60033,0) m/s in local XY.
- Freeze turbulence closure, transport parameters and inlet turbulence before measurement scoring. The recorded standard deviation of speed alone is insufficient to reconstruct full turbulent kinetic energy and dissipation.
- Carry 99% humidity as evidence. A dry, single-phase simplification must be declared and its thermodynamic consequences assessed; no condensation, ground heat flux or surface temperature data were recovered.
- Select ground thermal boundary treatment explicitly before execution. Zero imposed external heat flux is a simplified reference, not a measured surface condition.
- Verify that the no-gas profile does not drift through the domain before evaluating gas predictions.

**Auxiliary-profile caution:** the FAQ calls prefilled model-response-table profiles undisturbed. This does not establish that every sensor block in the experimental workbook is ambient: its downstream temperature sensors show cold plume signatures, and the original Risø report distinguishes in-plume and reference masts. Keep original values; use neither blanket classification nor all downstream temperatures as inlet atmosphere. The upstream mast is a consistency check, not grounds for silently overwriting corrected site averages.

## 4. What remains needed

The [ADMLC dataset page](https://admlc.com/datasets/) links the original REDIPHEM archive. On this review the public redirect reached a **Download not available** page, despite HTTP 200. No archive was obtained; do not record HTML as a successful dataset download. Original Risø report acquisition succeeded through DTU's public backend after the browser fetch failed.

Prepare a future data request for:
- EEC55 campaign/run notes, sensor setup and time series; the no-fence averaging indices used to produce EEC550.
- Exact equivalent-window centre height, origin/direction, profile, turbulence and reference pressure/humidity.
- Background meteorology, stability derivation and ground thermal information.
- Sensor definitions/calibration/detection limits and concentration basis.

No messages were sent and no access has been promised. Useful report leads: Nielsen 1990 Risø-M-2882; Heinrich & Scherwinski 1991 TÜV/BMFT 13RG8807; Gabillard et al. 1993 GDF/CERMAP 93I.593. These are leads, not documents verified in full.

## Readiness decision

| Item | Outcome |
|---|---|
| Local axis orientation | Resolved by primary analysis; magnetic north reference retained |
| EEC55/EEC550 relation | Strongly supported cross-reference; adopted for planning |
| Equivalent-window dimensions/state | Documented; retained |
| Actual equivalent-window elevation/trajectory | Unresolved; candidate assumptions and sensitivities recorded |
| Mean duration | Confirmed as 150 s in SMEDIS |
| Exact experimental averaging start/end | Unresolved; stationary comparison policy recorded |
| Weather hierarchy and neutral baseline | Defined with estimate provenance and numerical consistency check |
| Thermal/humidity/turbulence details | Open before execution |
| Faithful reproduction ready | No |
| Model results or accuracy claim | None |

[Short reading version](EEC550_SHORT_PLAN.md) · [Original comparison plan with follow-up corrections](EEC550_COMPARISON_PLAN.md) · [Updated structured input record](../../data/public/eec550-input-plan.json)
