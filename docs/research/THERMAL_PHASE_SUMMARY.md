# Conservative heat and phase feedback: short report

9 November 2026. **Implemented, executed and tested; no app.**

## Completed

A separate **1D compressible finite-volume flow prototype** now conserves five component masses, momentum and total internal-plus-kinetic energy. Heat flux changes internal energy; an equilibrium UV inversion recovers pressure, temperature and phase partition from the conserved state. Pressure then changes the momentum and energy fluxes.

This is actual spatial flow coupling, not a PH temperature reset or a separate heat-exchange operator. It is **not yet integrated into the 2D buoyant-flow prototype**.

| Checkpoint | Evidence |
|---|---|
| UV equilibrium closure | Volume and internal-energy inversion through the existing solid-aware PH model; melting and energy-reference tests |
| Acoustic/caloric closure | Equilibrium sound speed and heat capacity, with dry-gas analytical checks |
| Conservative flow and heat | HLLC Euler species/momentum/total-energy fluxes plus Fourier heat flux |
| Stationary-contact accuracy | Smooth and sharp equal-pressure composition contacts preserved without heating |
| Coupled feedback | Heat/control, fixed-volume heating and independently reconstructed cell thermodynamics |
| Verification | 210 package tests; 210 independent thermal checks; acoustic mesh-refinement benchmark |
| Records | Saved flow, controls, checks, acoustic results and source/runtime provenance |

## Results

The default synthetic periodic profile has 8 cells over 1 m and runs for **0.0003 s**, using a prescribed conductivity of 10 W/(m K). That coefficient is a research input, not a validated moist-propane transport property.

The more pronounced heat/control test uses **1000 W/(m K)** versus zero, with all other numerical settings matched. It changes maximum temperature by about **0.23177 K**, pressure by **98.52 Pa**, momentum density by **0.05750 kg/(m² s)** and condensate mass fraction by **3.422e-5**. Component mass, momentum and total energy remain conserved globally.

The default run's total-energy integral residual is about **5.82e-11 J/m²**, with maximum normalized conservation residual **2.85e-16**. These are accounting residuals, not model accuracy estimates.

The independent fixed-volume heating case adds 60000 J/kg to H00: pressure rises from 102500 to about 135223 Pa, temperature rises from 204.26 to 268.64 K, and ice decreases. Its energy budget includes that added heat explicitly.

A dry-N2 right-going small-amplitude acoustic wave gives pressure RMSE **0.004063 / 0.002063 / 0.001026 Pa** on 8/16/32 cells at matched time. This supports the basic numerical wave transport; it does not establish multiphase or field accuracy.

## Important defect caught and fixed

The initial Rusanov baseline conserved the totals but numerically mixed a stationary composition profile, producing about 492 Pa of spurious pressure drift. That exceeded the heat signal and was unacceptable as the main control.

The default was changed to contact-resolving **HLLC**. The matched zero-conduction smooth profile now has **zero recorded pressure, velocity and conservative-state drift**. Sharp stationary contacts and physical-flux consistency are also tested. Rusanov remains an explicit baseline option, not a hidden fallback.

This does not prove moving-contact, strong-shock or general nonconvex-EOS accuracy.

## Reproduce

From Avertiq_ with the existing environment and fresh output paths:

~~~powershell
.\.venv\Scripts\python.exe -m pytest research/equilibrium -q
.\.venv\Scripts\python.exe -m avertiq_equilibrium thermal-checks --output outputs/my-thermal-checks.json
.\.venv\Scripts\python.exe -m avertiq_equilibrium thermal-flow --output outputs/my-thermal-flow.json
.\.venv\Scripts\python.exe research/equilibrium/tools/acoustic_benchmark.py --output outputs/my-acoustic-check.json
~~~

Property verification gates both CLI commands. Failed checks refuse publication; JSON export and existing-output protection are tested. No new runtime dependency was added. CI runs the thermal checks, coupled case and acoustic benchmark.

[Equations and model limits](THERMAL_COUPLING_MODEL.md) | [Saved flow](../../data/public/thermal-phase-flow-v1/flow.json) | [Independent checks](../../data/public/thermal-phase-flow-v1/checks.json) | [Acoustic benchmark](../../data/public/thermal-phase-flow-v1/acoustic.json)

## Scope before EEC550

The EOS remains the reduced ideal-gas/pure-condensate equilibrium model, limited to 180–300 K and 50000–200000 Pa. Phase slip, rates, deposition and gas nonideality are omitted. Energy-reference invariance is checked; latent heat is already in the phase properties and is not added again.

The new conservative thermal solver has **no gravity or 2D integration**, no viscosity/turbulence, no open atmospheric release and no ground/terrain model. Conductivity is synthetic. The tiny periodic case is numerical verification, not an industrial release simulation.

Next: multidimensional thermal/buoyancy integration with compatible boundary conditions, momentum/energy and thermodynamics, followed by numerical refinement and atmosphere/source checks. EEC550 receptor comparison and operational accuracy claims remain outstanding.
