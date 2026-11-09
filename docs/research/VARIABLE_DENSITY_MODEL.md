# Variable-density buoyancy prototype: model decision

9 November 2026. Scope: a locally runnable hydrodynamic research milestone, no product app.

## Selected formulation

Use a two-dimensional, variable-density incompressible projection model on a staggered (MAC) grid. Let alpha be the volume fraction of a dense reference material. Set

    rho(alpha) = alpha rho_dense + (1-alpha) rho_air
    div(u) = 0
    d(alpha)/dt + div(alpha u) = 0

The endpoint densities may be initialized from the existing conditional H00 and ambient equilibrium calculations. They remain frozen during this flow experiment. Alpha is a **volume fraction**, not the mass fraction transported by the earlier 1D prototype. The corresponding dense mass fraction is alpha*rho_dense/rho.

Because rho is affine in alpha, conservative alpha advection and a discretely divergence-free volume velocity give conservative density transport. Interface mixing here is volume-additive numerical mixing of fixed-density reference materials. It is not a new thermodynamic equation of state for moist propane.

This is a non-Boussinesq variable-density flow calculation: density enters inertia/pressure correction and the gravity response, rather than appearing only as a small perturbation in a constant-density force.

## Velocity and pressure

Use a velocity predictor with advection, optional documented viscosity, and gravity relative to a constant reference hydrostatic state:

    du/dt + u.grad(u) = -(1/rho) grad(pi)
                         + viscous approximation
                         + (rho-rho_ref)/rho * g_vector

Here g_vector points downward; pi is reduced dynamic pressure. Subtracting rho_ref*g from the original gravitational force is a pressure-reference transformation, not removal of gravity. Full density remains in the denominator. The hydrostatic reference must use the same rho_ref and sign convention everywhere.

For predictor velocity u_star, a variable-coefficient pressure correction satisfies

    div(beta grad(phi)) = div(u_star)/dt
    u_new = u_star - dt beta grad(phi)
    beta = 1/rho at faces

The same face beta, divergence and gradient must be used in the matrix and correction. Otherwise a small linear-system residual does not establish incompressibility. Pressure is determined up to a constant; fix a gauge with a compatible reduced linear system.

The predictor's velocity-form advection is an approximation to the momentum equation. It does **not** establish discrete conservation of rho*u across density interfaces. Report mass and divergence budgets separately from momentum/energy behaviour; do not call a velocity-form implementation a fully conservative multiphase solver. A constant-kinematic-viscosity Laplacian is also a documented approximation; it is not the full variable-density viscous stress divergence.

## Boundaries and numerical gates

- Periodic horizontal direction; impermeable top and bottom; free-slip tangential velocity.
- Enforce zero wall-normal predictor velocity before forming the pressure right-hand side, and after correction. With compatible boundary treatment the domain integral of the Poisson right-hand side is zero. Do not silently subtract a substantial incompatible mean.
- Use conservative upwind alpha fluxes and an explicit multidimensional positivity/CFL bound. Do not stabilize by clipping alpha, density or velocity.
- Base step limits on actual predicted velocities and any explicit viscous contribution; gravity can create velocity from an initially stationary field.
- Fail explicitly on nonfinite state, nonpositive density, failed pressure solve, unacceptable divergence or alpha bounds.
- Report initial/final dense-material volume and total mass, pressure residual, maximum divergence, velocities, alpha range and synthetic initial conditions. Document normalization and tolerances.

These closed/periodic boundaries deliberately isolate mathematical checks. They do not describe an atmospheric release or an exhaust/outflow boundary.

## Required tests and interpretation

1. Uniform density and zero velocity remain at rest after reference hydrostatic subtraction.
2. Arbitrary variable-density velocity is projected to the discrete divergence tolerance.
3. A vertical density profile remains hydrostatically at rest; pressure balances gravity without spurious circulation.
4. Dense synthetic material descends under downward gravity. A matching zero-gravity case remains stationary when started at rest.
5. Alpha and total mass conserve; positive/negative advection and wall conditions behave consistently.
6. Grid/time-step refinement and pressure tolerances must be reported before quantitative hydrodynamic accuracy claims.

Passing these tests verifies the implemented hydrodynamic approximation. It does not validate a dense-gas experiment.

## Thermodynamics boundary and next milestone

This model adds a genuine density-dependent velocity/pressure/gravity response absent from the earlier prescribed-flow transport prototype. It does **not** yet evolve conserved species and enthalpy with local phase-changing density feedback. Do not recompute density from a PH flash after projection while retaining div(u)=0: thermal/phase volume changes require a compatible continuity/EOS divergence constraint.

Before EEC550 comparison, add a reviewed thermodynamic/continuity coupling, component and energy transport, momentum consistency, appropriate atmospheric turbulence and inlet/outlet conditions, source-height/averaging assumptions and mesh/time/domain checks. Particle slip, phase rates and deposition remain unresolved. No EEC550 sensor accuracy, Adoshi footprint, terrain-flow or operational safety claim follows from this prototype.

## Primary method references

- [IAMR fluid equations](https://amrex-fluids.github.io/IAMR/docs_html/FluidEquations.html): distinguishes mass/momentum equations, passive/conservative scalar transport and the incompressible constraint. Its more complete implementation is a method reference, not software used in this prototype.
- [AMReX-Hydro projection methods](https://amrex-fluids.github.io/amrex-hydro/docs_html/Projections.html): variable-coefficient projection and compatible face-centred divergence/gradient correction.
- [PeleLM low-Mach model](https://amrex-combustion.github.io/PeleLM/manual/html/Model.html): illustrates why EOS-coupled composition/thermal evolution generally requires a derived, potentially nonzero velocity-divergence constraint. Its combustion closure is not adopted here.

[Previous transport limits](TRANSPORT_PROTOTYPE_SUMMARY.md) | [Equilibrium workbench](WORKBENCH_V1.md)
