# Equilibrium implementation: short report

8 November 2026.

**Implemented and run:** a standalone thermodynamic calculation in research/equilibrium. No app or CFD.

**Verification:** 38 tests and 34 property/numerical checkpoints passed, including mass/energy conservation, phase limits and ice melting.

The original PR/water-ice property combination failed its reference check. The implemented reduced model instead combines ThermoPack propane/gas properties with a consistent IAPWS/NIST water saturation and latent-heat closure. Its assumptions remain explicit.

**Primary conditional result:** about **204.3 K**, with approximately **0.0577 kg/s water ice** and no remaining liquid propane. The dry control gives about **199.4 K**. These are model-dependent results, not recovered experimental states.

Holding the same conditional feed at 196 K requires approximately **496 kW of heat removal** in the audit calculation; that is an implied discrepancy, not evidence of real heat loss.

The nine CFD cases remain held pending scientific review of the reduced model and source assumptions.

[Full verification report](EEC550_EQUILIBRIUM_VERIFICATION.md) · [Run instructions](../../research/equilibrium/README.md)
