# What the first propylene outputs will mean

14 November 2026. Documentation and capture-contract preparation only. No actual propylene results exist; no ALOHA process, UI or DLL was used.

The next evidence gate needs more than a concentration number: we must know whether it describes outdoor or indoor air, a time-averaged maximum or an instantaneous peak, and which location and observation window it uses. This milestone makes that distinction explicit before the four runs arrive.

## Documented interpretation

The installed 5.4.7 help describes the concentration-at-point graph as ground-level indoor and outdoor averaged concentrations over the first hour after release begins. Its toxic averaging description is a few minutes; this review does not establish one exact interval for every dispersion method. A maximum on that averaged curve is not an instantaneous peak. Relative downwind/crosswind receptors follow the wind direction; fixed east/north receptors instead refer to geographic offsets. Toxic threat zones indicate threshold exceedance at some time, not a simultaneous cloud snapshot.

The installed pages and their byte hashes are recorded in [output semantics evidence](../../research/dispersion/output-semantics-evidence.json). NOAA's [concentration-graph explanation](https://response.restoration.noaa.gov/oil-and-chemical-spills/chemical-spills/resources/ask-dr-aloha-working-concentration-graph.html), SRC-101, also distinguishes the outdoor and indoor maxima reported in Text Summary and the first-hour plot. Neither source establishes the output of our unrun propylene case.

## Bounded capture policy for this suite

Capture each scalar receptor value from the reported **outdoor maximum of averaged concentration**, retaining its raw evidence. If a value is unavailable, keep null with the observed reason. Do not digitize a guessed peak or substitute an indoor maximum. If the model provides a materially different output, preserve it separately and review a revised output contract rather than relabelling it to pass.

The physical case inputs and the four existing unrun observation templates are unchanged. This is an additional interpretation contract, not a new model result or a change to source assumptions.

| Supplement field | Required meaning/value after actual capture |
|---|---|
| `schema_version`, `status` | `1`, `recorded_from_output` |
| `receptor_statistic` | `reported_maximum_of_time_averaged_concentration` |
| `receptor_environment` | `outdoor` |
| `receptor_coordinates` | `relative_downwind_crosswind`; retain the requested 50/100/200/500 m, crosswind zero |
| `receptor_height_m` | `0` |
| `window_start_s`, `window_end_s` | `0`, `3600`, measured from release start |
| `averaging_basis` | `aloha_toxic_minutes_exact_interval_unresolved` |
| `averaging_seconds` | null; this policy does not guess 300 seconds or borrow the flammable averaging interval |
| `contour_statistic` | `threshold_exceeded_at_some_time` |
| `threshold_use` | `numerical_diagnostic_no_health_authority` |
| `evidence_sha256` | Nonempty, unique hashes referring to the run's checked raw evidence |
| `capture_notes` | Where the outdoor maxima, coordinate frame and time basis were read; explain unavailable outputs and any ambiguity |

**The 600-second source duration is not the 3600-second output window.** Nor does the first-hour plot imply a one-hour averaging period. The 1000/100/10 ppm contours remain numerical diagnostics without health or evacuation authority. This scalar capture does not supply a time series, animation or terrain-dependent plume.

## Prepare now; fill only after observing output

```powershell
python research/dispersion/propylene.py output-semantics-template --output outputs/propylene/output-semantics-unconfirmed.json
```

The [saved supplement](../../research/dispersion/templates/output-semantics-unrun.json) contains null fields and `unconfirmed` status. It cannot pass as observed metadata. Once real evidence supports the declared meanings, place the completed object under `output_semantics` in the local observation JSON. The helper does not populate or attach confirmed answers automatically.

To avoid contradictory legacy descriptions, the existing `basis` strings must also use these canonical descriptions when the supplement is supplied:

- `statistic`: `reported_maximum_of_time_averaged_concentration`
- `averaging_description`: `Toxic display: few minutes; exact interval unresolved`
- `time_window_description`: `First hour after release start (0-3600 s)`

The existing unit/basis, ground height and display-mode checks still apply. Use `operator_notes`, `mapping_review` and `capture_notes` for additional interpretation instead of changing those canonical meanings. Merely entering the required strings is not evidence: a human must check them against the raw output. Hash references bind files, not the truth of the transcription.

## Inspection, comparison and archives

`inspect-run` retains legacy records without a supplement, marking structured output semantics as missing. It rejects a supplied but incomplete, unsupported or contradictory supplement. Neither path closes the case's `output_height_and_time_basis` applicability gate automatically.

`compare-runs` now withholds numerical differences/ratios unless both records have consistent structured semantics as well as matching selected method and legacy basis. Matching metadata permits only diagnostic comparisons within the same audited engine/method; it does not establish a matched exact averaging interval for comparison with another model or measurements. Different capture notes or raw-file hashes do not by themselves change the output meaning.

The [archive workflow](PROPYLENE_EVIDENCE_ARCHIVE.md) preserves the supplement and includes its checking module and documentation record in provenance. Earlier archives remain historical evidence; code/configuration changes require reinspection and do not silently update their original reports.

## Verification and remaining work

Eight new synthetic tests bring the package to 47 passing tests. They cover missing/unsupported semantics, indoor and instantaneous substitutions, source-duration/window confusion, invented averaging seconds, conflicting descriptions, evidence references, comparison withholding, unconfirmed templates and archive provenance. All original case/template checks continue to pass. These are tooling tests, not physical validation.

Actual output capture, exact method-specific averaging, source temperature/phase compatibility, chemical/property identity and other mapping gates remain pending. Qualified physics and the dashboard adapter remain disabled.
