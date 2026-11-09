# Latest completed checkpoint

9 November 2026.

**Built:** integrated 2D conservative heat/phase/buoyancy research solver. No app.

- Density, pressure, temperature and phases evolve with mass/energy transport.
- Gravity and pressure drive both velocity components.
- Hydrostatic reference stays at rest; wall/gravity and total-energy budgets pass.
- 232 package tests and 552 independent checks passed.
- The 2D-to-1D thermal-flow regression matches at recorded precision.

**Next:** open-domain atmosphere/source setup, numerical refinement and runtime/scaling before EEC550 comparison. Current runs are tiny closed-box tests, not field predictions.

[Short results and commands](THERMAL_2D_SUMMARY.md) | [Model equations](THERMAL_2D_MODEL.md)
