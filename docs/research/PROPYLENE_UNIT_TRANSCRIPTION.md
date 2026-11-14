# Preserve units and reporting limits when transcribing results

This milestone prepares manual result capture while ALOHA is pending. No propylene model output has been calculated or imported. The conversion tool only changes the representation of values supplied in a future observed record; it does not calculate a release, concentration or threat distance.

## Bounded conversion rules

| Recorded quantity | Accepted unit tokens | Stored unit |
|---|---|---|
| Total airborne mass | `kg`, `g`, `lb` (avoirdupois) | kg |
| Source duration | `s`, `min`, `h` | s |
| Contour distance | `m`, `km`, `ft`, `yd`, `mi` (international units) | m |
| Receptor concentration | `ppm`, for the existing gas-volume basis only | ppm |

Length and mass factors are attributed in the [conversion record](../../research/dispersion/unit-conversion-evidence.json) to [NIST Handbook 44, Appendix C](https://www.nist.gov/system/files/documents/2024/01/14/NIST%20HB%2044%202024%20Appendix%20C%20General%20Tables%20of%20Units%20of%20Measurement.pdf), SRC-102. These use 0.3048 m/ft, 0.9144 m/yd, 1609.344 m/mi and 0.45359237 kg/lb. Survey units, troy pounds and unspecified tons are unsupported. The factors are exact unit relationships; the displayed model numbers remain rounded observations. Extra decimal digits after conversion do not create additional measurement precision.

No mg/m3-to-ppm, percent-LEL, gas-volume/mass, source-state or pressure/temperature conversion is attempted. A unit from the wrong dimension is rejected. Source rate and input/weather fields are outside this output-only converter.

## Reported scalars, bounds and missing values

Each transcribed item carries a `relation`:

- `reported`: a displayed scalar. This does not mean an exact physical measurement. `reason` must be null.
- `gt`, `ge`, `lt`, `le`: a reporting bound (`>`, `>=`, `<`, `<=`). Preserve the actual reason supplied by the model.
- `unavailable`: no number; retain the observed reason. Never enter zero as a placeholder.

For example, a **synthetic illustration** of `> 10 km` normalizes to a lower bound of 10000 m with the `gt` relation retained. Its scalar `downwind_m` stays null, not 10000. A receptor reported below a concentration bound likewise remains null in the scalar comparison. Differences and ratios involving it remain null; this tool does not implement interval comparisons or claim a censored point is safe.

Source mass and duration still require reported scalars because the existing qualification contract checks those against prescribed input totals. A bounded or unavailable source summary is retained in the original capture but cannot pass normalization for this contract.

## Workflow after actual output exists

Prepare the unconfirmed supplement now if useful:

```powershell
python research/dispersion/propylene.py transcription-template --case baseline --output outputs/propylene/transcription-unconfirmed.json
```

It contains nine targets: two source-summary values, four receptor concentrations and three contour distances. All reading fields start null. After a real run, fill the supplement and place it under `transcription` in the local observed JSON described in [propylene preparation](PROPYLENE_PREPARATION.md). Set its status to `recorded_from_output` only after transcribing evidence.

Each item requires the generated `target`, `value_text`, `unit`, `relation`, `reason`, `evidence_sha256` and `evidence_location`. Use the latter to identify the actual page, section or graph label. The hash must refer to a raw file in the observation's evidence inventory. The tool verifies those files through the existing inspector; a matching hash does not prove transcription accuracy, so human review remains necessary.

`value_text` is a string, preserving digits such as `1.00` or `1e3`. It must be an unambiguous nonnegative decimal/scientific token, without units, commas or inequality signs. Keep those meanings in their separate fields and retain the original rendering in raw evidence. Unavailable values use null. The tool rejects malformed/non-finite numbers, unsupported units, unknown/duplicate targets and incomplete inventories.

After all required run metadata and [output semantics](PROPYLENE_OUTPUT_SEMANTICS.md) have been captured:

```powershell
python research/dispersion/propylene.py normalize-run --case baseline --observed outputs/propylene/baseline-capture.json --output outputs/propylene/baseline.json
python research/dispersion/propylene.py inspect-run --case baseline --observed outputs/propylene/baseline.json --output outputs/propylene/baseline-checked.json
```

`normalize-run` writes a new observation beside the original so relative evidence paths remain valid. It fills only the named scalar output fields/reasons and sets an explicit pending-qualification label and false qualification flags. Raw transcription, warnings, method, timestamps and other metadata are retained. It does not mark a run completed or fill missing observed inputs. The full record inspector must pass before anything is written. Source-mass/duration tolerance remains the previously registered rule; no tolerance was relaxed to make converted values pass.

The source file is not modified; an existing output is never overwritten. Use a fresh filename. If the raw evidence or record is incomplete, preserve it and resolve the problem rather than creating expected values.

## Inspection and archive behaviour

When a `transcription` supplement is present, `inspect-run` recomputes conversions and requires scalar values and reasons to agree. Replacing a bound with an exact number, or changing its recorded reason, fails inspection. Both raw tokens and conversion details appear in the checked report and survive the [private archive workflow](PROPYLENE_EVIDENCE_ARCHIVE.md). Archive provenance includes the conversion table and checking module.

Legacy normalized records without this supplement remain inspectable and explicitly report `raw_unit_transcription_not_supplied`. Their units have not been independently reconstructed from raw tokens. This optional compatibility path is not an automatic unit-verification claim; structured output semantics and human evidence review still apply before comparing results.

## Verification

All 59 research-tool tests pass, including 12 new synthetic tests. They cover known conversions, all four cases, bounded/missing readings, rejected scalar substitution, null comparison ratios, unsupported dimensions, original-file preservation, CLI validation/overwrite/path handling and archive retention. Tests use disposable synthetic records only. Frozen cases, existing unrun templates and public preparation reports are unchanged.

Actual physics results, ALOHA source-state equivalence and the dashboard adapter remain pending. No computer control was used.
