# EEC550 phase check: short report

**Follow-up:** the [source/energy review](EEC550_SOURCE_ENERGY_SUMMARY.md) defines conditional component ledgers and selects a local 0D HEM route with ThermoPack properties. No numerical energy solution or replacement CFD source has been produced.

8 November 2026. Research and property arithmetic only.

**Decision: the proposed gas-only OpenFOAM setup is not suitable as the EEC550 physical baseline unchanged.**

- **Propane:** at 196 K, the calculated partial pressure is 20.5 kPa, above saturation of about 15.7 kPa. The assumed all-gas state needs reconciliation.
- **Water:** ambient air was listed at 99% RH. If that moisture enters the cold source, it cannot all stay gaseous; condensation/ice and latent heat need consideration.
- **Solver:** transporting water vapour alone does not model those phase changes. OpenFOAM may still be usable with an appropriate reviewed configuration.

These checks do not measure actual droplets or ice, and they are not a full equilibrium calculation.

**Next:** reconcile the source's water inventory, pressure and enthalpy, then assess an energy-conserving phase-changing model or a justified gas-only downstream state.

The nine-case sensitivity study is held pending that decision. No coding, installations or simulations.

[Evidence and calculations](EEC550_PHASE_REVIEW.md) · [Calculation record](../../data/public/eec550-phase-screen.json)
