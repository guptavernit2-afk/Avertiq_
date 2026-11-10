# Initial scenario definitions

These are the historical propylene/Adoshi-inspired cases. The confirmed 10 November 2026 scope adds LPG/CNG and storage, as defined in the [chemical/storage matrix](research/CHEMICAL_AND_STORAGE_SCOPE.md). No numerical LPG-mixture or CNG input sheet is accepted yet; do not reuse a propane EEC550 source or the D-001 illustration as one.

All three cases are hypothetical training cases inspired by Adoshi. Numeric values remain unset until source-model selection and review.

| ID | Intent | Controlled comparison |
|---|---|---|
| ADV-001 | Smaller unignited release | Baseline tank and weather; documented smaller release assumption |
| ADV-002 | Larger unignited release | Same baseline where physically appropriate; one clearly identified release change |
| ADV-003 | Reduced release following intervention | Explicit changed source conditions; account for earlier material and transfers |

These are scenarios, not three reconstructed historical phases.

## Required input sheet

- Chemical identity and property-source version.
- Incident/source coordinates, source height, timestamp and coordinate reference system.
- Tank geometry, orientation, inventory and relevant thermodynamic state.
- Leak location, effective opening, phase and direction, or a documented direct-source input.
- Release duration/rate history and transfer history where applicable.
- Atmospheric inputs required by the chosen model: wind, height, temperature, stability information and surface assumptions.
- Hazard thresholds, concentration units, averaging time, assessment height and prediction period.
- Evidence status, synthetic flag and explanation for every input.
- Model/version, settings, operator/reviewer and run identifier.

Do not infer leak dimensions or phase from total cargo mass.

## Output meaning

Distinguish an envelope of possible threshold exceedance during a period from an instantaneous concentration snapshot. New independent runs do not automatically track an old cloud through changing weather.

Synthetic observation points are UI fixtures, never experimental validation evidence.
