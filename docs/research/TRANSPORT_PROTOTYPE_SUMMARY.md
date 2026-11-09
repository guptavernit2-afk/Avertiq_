# First transport prototype: short report

9 November 2026.

Implemented a self-run **1D finite-volume advection-diffusion prototype**, with local equilibrium phase postprocessing. No app.

- Conservative upwind advection, central diffusion, explicit positivity bound.
- Source mass fraction reconstructs component mol/kg and thermal enthalpy J/kg; PH computes local temperature and phases.
- 154 tests passed across the research package (18 transport tests).
- Fourier cell-average benchmark RMSE falls from 0.001719 to 0.000958 to 0.000597 on 40/80/160 cells.
- Default synthetic 100-cell pulse executed; largest local energy residual about 0.000004 J/kg. Component/enthalpy sums conserve to floating-point precision.

## Reproduce

From Avertiq_:

~~~powershell
.\.venv\Scripts\python.exe -m pytest research/equilibrium -q
.\.venv\Scripts\python.exe -m avertiq_equilibrium transport --output outputs/my-fresh-transport.json
~~~

Use a fresh output file. Property verification runs first. [Saved run](../../data/public/transport-prototype-v1/transport.json) and [refinement evidence](../../data/public/transport-prototype-v1/fourier-refinement.json).

**Limits:** prescribed velocity/diffusivity, periodic boundaries and fixed reference mass per cell. PH density is diagnostic and does not affect transport. This is a kinematic numerical prototype, not a buoyant dense-gas solver or an EEC550 field reproduction. First-order numerical smearing is reported separately from prescribed diffusion. No hazard polygons or sensor accuracy claims.

**Next:** variable-density continuity/momentum/buoyancy and atmosphere treatment must be selected and checked before an open-domain EEC550 comparison. This prototype supplies transport conservation and phase-closure regression cases, not that physical capability.

[Model decision and equations](DISPERSION_MODEL_DECISION.md)
