# Variable-density flow and buoyancy: short report

9 November 2026. **Implemented and executed; no product app.**

## Completed checkpoints

- 2D staggered-grid flow with density-dependent inertia/pressure correction.
- Conservative volume-fraction advection and variable density.
- Gravity, velocity advection and optional viscosity.
- Variable-coefficient pressure projection enforcing incompressibility.
- 173 passing package tests, including 14 engine tests, independent runner tests and CLI gates.
- 22 independent numerical checks passed: projection, buoyancy/control, hydrostatic rest, density relation and mass budgets.
- Matched-time 12/24/48-cell-per-axis comparison executed.

## Results

The default H00/ambient endpoint densities are approximately 1.94259 and 1.25569 kg/m3. In a synthetic 10 x 10 m periodic-horizontal, closed-wall box, the dense-material centroid drops about **0.02672 m over 0.25 s** on a 24 x 24 grid.

Default maximum discrete divergence is approximately **1.14e-15 /s**; relative mass residual is zero at recorded precision. These values establish numerical consistency, not physical accuracy.

The independent arbitrary-density projection check reaches divergence about 1.11e-14 /s. A separate synthetic-density dense blob descends relative to its zero-gravity control; hydrostatic and equal-density controls remain at rest. Tests also cover a light blob rising and projection's weighted kinetic-energy behaviour.

At 12/24/48 cells per axis, endpoint-case centroid drops are **0.02549 / 0.02672 / 0.02708 m**. This is encouraging mesh behaviour, not a certified convergence order or error bound. Time-step/domain/physical-model sensitivity remains before quantitative flow claims.

## What the model actually solves

Alpha is dense-material **volume fraction**; density is alpha*rho_dense+(1-alpha)*rho_air. It differs from the mass fraction in the previous 1D solver. Density changes with conservative material transport and affects velocity/gravity/projection.

The endpoint densities come from the existing source and ambient thermodynamics, but remain frozen during flow. The model does not yet evolve composition/enthalpy and recompute PH density. Doing that consistently requires a thermodynamic volume-change/divergence constraint, rather than simply overwriting density.

Velocity-form momentum advection and constant kinematic viscosity are documented approximations; this is not a discretely conservative momentum/total-energy multiphase scheme. Reduced pressure has an arbitrary gauge and is not absolute thermodynamic pressure. No atmosphere, turbulence closure, release inlet, terrain, phase slip or deposition is represented.

## Reproduce

From Avertiq_ with the existing environment:

~~~powershell
.\.venv\Scripts\python.exe -m pytest research/equilibrium -q
.\.venv\Scripts\python.exe -m avertiq_equilibrium flow-checks --output outputs/my-fresh-flow-checks.json
.\.venv\Scripts\python.exe -m avertiq_equilibrium flow --output outputs/my-fresh-flow.json
~~~

Choose fresh paths. Property verification gates execution; failed flow checks refuse publication. CI runs both commands. No new dependencies were added.

[Model equations and method references](VARIABLE_DENSITY_MODEL.md) | [Saved run](../../data/public/variable-density-flow-v1/flow.json) | [Independent checks](../../data/public/variable-density-flow-v1/checks.json) | [Grid comparison](../../data/public/variable-density-flow-v1/grid-comparison.json)

## Before EEC550

This closes the **frozen-endpoint hydrodynamics** checkpoint. Next requires compatible component/energy/EOS coupling and momentum consistency, then open-domain atmosphere/inlet settings and numerical refinement. The nine-case EEC550 study stays held. This run does not validate a field plume, sensor predictions, Adoshi conditions or operational safety.
