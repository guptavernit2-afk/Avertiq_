# Integrated 2D heat, phase and buoyancy: short report

9 November 2026. **Implemented, executed and tested in Avertiq_. No app.**

## Delivered

Heat/phase feedback is now integrated with two-dimensional gravity-driven flow in a new conservative formulation. The previous frozen-density projection solver remains a regression baseline; it is not used to overwrite density after a flash.

The coupled solver evolves five component masses, horizontal and vertical momentum, and internal-plus-kinetic-plus-gravitational-potential energy. A UV equilibrium closure recovers pressure, temperature and gas/liquid/ice partition from conserved density, composition and internal energy. Those properties then affect the next flow and heat fluxes.

| Checkpoint | Evidence |
|---|---|
| Integrated 2D physics | Euler/HLLC fluxes, Fourier conduction, gravity and UV phase feedback |
| Gravity/energy consistency | Potential-energy mass flux; no duplicate gravity heat source |
| Hydrostatic balance | Analytic isothermal cell-average reference and conservative shared-flux correction |
| Boundaries and forces | Periodic horizontal; reflecting, insulating vertical walls; wall traction and gravity included in momentum budget |
| Numerical tests | 232 package tests passed |
| Independent verification | 552 checks, including per-cell thermodynamic reconstruction, gravity/heat controls and exact 1D reduction |
| Reproducibility | Saved fields, controls, budgets and source/runtime provenance; CLI and CI commands |

## Measured numerical results

The default synthetic case uses a **4 x 4 grid over 1 x 1 m**, gravity 9.81 m/s², conductivity 10 W/(m K), and runs **0.0003 s** in four steps. Conductivity is a prescribed research parameter, not validated industrial transport data.

- Default maximum normalized boundary/source budget residual: **1.30e-16**.
- Default total-energy integral residual: approximately **-2.91e-11 J per metre of out-of-plane depth**.
- Hydrostatic-reference maximum speed: **1.90e-14 m/s**.
- Nontrivial zero-gravity 2D-to-1D thermal-flow reduction: **zero recorded normalized conservative difference**.

A stress control compares conductivity **1000 W/(m K)** with zero while gravity is active. Maximum differences are **0.24879 K** in temperature, **89.94 Pa** in pressure, **1.554e-5** in condensate mass fraction, and **0.02604 kg/(m² s)** in momentum density. These show numerical heat/phase/flow feedback, not validated transport-property predictions.

The gravity control changes vertical velocity by up to **0.002782 m/s**. It uses matched physical initial density/composition/pressure/velocity, with total energy rebased for the different potential convention. Its initial pressure gradient is not balanced in zero gravity, so the zero-gravity counterpart is **not** expected to remain at rest. Separate hydrostatic and uniform-rest checks establish the resting baselines.

Vertical momentum is not constant in a gravity/wall box: the default net change is about -0.0003083 kg/s per unit depth, explained by upward wall-pressure impulse plus downward gravitational impulse. The independent checker verifies that budget instead of incorrectly asserting zero change.

## Reproduce

From Avertiq_ using the existing environment and fresh output paths:

~~~powershell
.\.venv\Scripts\python.exe -m pytest research/equilibrium -q
.\.venv\Scripts\python.exe -m avertiq_equilibrium thermal2d-checks --output outputs/my-thermal2d-checks.json
.\.venv\Scripts\python.exe -m avertiq_equilibrium thermal2d --output outputs/my-thermal2d.json
~~~

Both commands run the property-verification gate first; failed checks refuse publication. JSON export and existing-output protection are covered. No new runtime dependency was added.

[Equations and reference construction](THERMAL_2D_MODEL.md) | [Saved coupled run](../../data/public/integrated-thermal2d-v1/flow.json) | [Independent checks and controls](../../data/public/integrated-thermal2d-v1/checks.json)

## What is checked

Tests cover hydrostatic rest, zero-gravity stationary contacts, heat/phase feedback, component and total-energy budgets, vertical source/wall forces, axis interchange, nonzero-velocity 1D reduction and caloric-reference invariance with gravity and heat active.

Each final control cell is independently reconstructed through TP equilibrium, checking volume, internal energy after subtracting both kinetic components and gravitational potential, and phase/component mass densities. Ice/liquid melting coexistence is treated explicitly. Deliberately corrupted energy and arbitrary invalid hydrostatic-reference data are rejected.

The fixed reference is the declared ideal-gas isothermal ambient profile. This is not universal preservation of every possible moist multiphase hydrostatic state. Its shared-flux correction is conservative and reference-specific, not a claim to implement a published high-order solver.

## Before EEC550

This closes the **2D thermal/phase/gravity integration** checkpoint. It does not establish an atmospheric release calculation.

Still required: mesh/time/domain and long-time accuracy/scaling studies, suitable open inlet/outlet boundaries, source geometry and atmosphere/turbulence treatment, reviewed conductivity/phase-relaxation assumptions, and the locked EEC550 receptor/averaging comparison. The current tiny case is deliberately short; its runtime and numerical formulation have not been established for a 150-second field comparison.

The inherited equilibrium domain remains 180–300 K and 50000–200000 Pa. Instantaneous common-phase velocity/temperature, ideal gas and pure condensates remain approximations; slip, finite phase rates, deposition, viscosity/turbulence, ground heat and terrain are absent. No industrial accuracy, EEC550 validation, Adoshi footprint or operational safety claim follows.
