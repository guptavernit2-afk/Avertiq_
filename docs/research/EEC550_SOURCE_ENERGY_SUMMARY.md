# EEC550 source and model decision: short report

**Implementation follow-up:** the [standalone calculation is now implemented and verified](EEC550_EQUILIBRIUM_SUMMARY.md), using a revised water-property closure. This earlier planning record is preserved as history; conditional numerical results now exist, while historical source uncertainty remains.

8 November 2026. Research only.

**Choose a small homogeneous-equilibrium model first:** conserve mass and energy, then calculate temperature and the amounts of propane vapour/liquid and water vapour/liquid/ice.

**Local route:** free ThermoPack fluid/ice properties plus an explicit solid-aware calculation. Its ordinary two-phase PH call does not supply the complete moist/ice model. Implementation comes later; nothing was installed or run.

What the source audit established:
- The rounded window implies about 3.05 kg/s propane, compared with the nominal 3 kg/s.
- Conditional moist-air interpretations carry about 0.058 kg/s water, whose latent heat could matter.
- We must solve temperature from the energy balance; simply raising it to remove supersaturation would not close that balance.

The historical inlet remains non-unique. We have closed conditional mass ledgers and defined the energy calculation, not produced a corrected experimental temperature or phase split.

Next milestone: implement and verify this thermodynamic calculation before returning to the nine CFD sensitivity cases. No coding or simulations yet.

[Full findings](EEC550_SOURCE_ENERGY_RECONCILIATION.md) · [Structured plan](../../data/public/eec550-source-energy-plan.json)
