# Latest completed checkpoint

9 November 2026.

**Built:** a 1D conservative thermal/phase-coupled flow prototype.

- Species, momentum and total energy transported conservatively.
- Heat changes pressure/temperature/phases through a UV equilibrium closure.
- Contact-resolving flux fixes a spurious-motion defect exposed by the no-heat control.
- 210 package tests and 210 independent thermal checks passed.
- Acoustic pressure error roughly halves with each grid refinement.

**Boundary:** this is not yet integrated into the 2D buoyant solver, and is not an EEC550 release prediction. No app.

[Short results and commands](THERMAL_PHASE_SUMMARY.md) | [Model equations](THERMAL_COUPLING_MODEL.md)
