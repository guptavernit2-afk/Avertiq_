# First dispersion prototype: model decision

9 November 2026. User authorized dispersion prototyping and numerical checks, with no app. This implementation is a **transport verification prototype**, not the EEC550 field-dispersion model.

## Selected model and purpose

Run a local Python/NumPy **one-dimensional conservative finite-volume advection-diffusion solver for a source-mixture mass fraction**, followed by the existing pressure/enthalpy equilibrium closure. Prescribe constant velocity, constant diffusivity and a constant reference mass density. Use periodic boundaries for closed-budget verification.

This is a deliberately limited, self-run numerical stepping stone. It introduces spatial transport and mixing without pretending that a gas-only plume model represents the cold multiphase source. The transported mixture has two fixed endpoints: the declared H00 source and declared ambient wet air. Thermodynamic reconstruction permits changing gas/liquid/ice partition.

**It is not suitable for EEC550 receptor predictions.** No momentum equation, buoyancy, variable-density continuity, turbulent atmosphere, jet entrainment, open-boundary release or terrain is solved. Computed x/time are coordinates of the synthetic transport experiment, not accident distances or travel times. The nine-case field-comparison study stays held.

## Equations and mass basis

Let z be the fraction of source-origin mass in a parcel, between zero and one. With constant prescribed u and diffusivity K:

    dz/dt + d(u z)/dx = d(K dz/dx)/dx

Transport equal reference mass per uniform cell. For each total chemical component i and thermal enthalpy, reconstruct on a one-kilogram mixture basis:

    a_i(z) = z a_i,source + (1-z) a_i,ambient       [mol/kg]
    h(z)   = z h_source + (1-z) h_ambient         [J/kg]

The source endpoint is the calculated source flow divided by its total mass flow, not 3 kg/s propane alone. The ambient endpoint includes its declared vapour water. Solve local PH equilibrium at 102500 Pa for these component amounts and h. Phase masses sum to that one-kilogram basis; latent effects are already in phase enthalpies and must not be added again.

The PH-returned density and volume are **diagnostics only**. They generally differ between cells and from the fixed transport reference density. Substituting that varying density into the same fixed-density mass budget would be inconsistent. This prototype does not claim that the reconstructed cells jointly satisfy compressible continuity or momentum. That limitation is the principal next-model gate.

## Finite-volume scheme and stability

Update each cell average using differences of one shared interface flux. Use upwind advection and centred diffusive flux:

    z_j,new = z_j - dt/dx (F_j+1/2 - F_j-1/2)
    F_j+1/2 = u z_upwind - K (z_j+1 - z_j)/dx

For nonnegative K and either sign of u, the explicit update has nonnegative weights when:

    C = abs(u) dt/dx
    D = K dt/dx^2
    C + 2 D <= 1

This sufficient monotonicity restriction follows directly from the update weights: the centre coefficient is 1-C-2D and neighbour weights are nonnegative. Reject invalid/nonfinite inputs and unstable requested steps; do not repair instability by clipping z after a step. Periodic interface fluxes cancel in the global sum, conserving sum(z dx) up to floating-point roundoff. Affine reconstruction then conserves every total component and thermal enthalpy in the reference-mass accounting.

First-order upwind introduces numerical diffusion. Added physical diffusivity is a synthetic test parameter, not a calibrated turbulence model. Grid refinement and exact-solution error must distinguish numerical smearing from intended diffusion.

## Verification checkpoints

1. Uniform-field preservation, zero-time identity, finite/positive inputs and bounds.
2. Periodic scalar conservation and reconstructed total-component/enthalpy budgets.
3. Positive and negative advection; one-cell translation at C=1 with K=0 when applicable.
4. Periodic Fourier-mode benchmark against the analytical advection-diffusion solution:

       z(x,t) = mean + amplitude exp(-K k^2 t) sin(k (x-u t))

   If initialized as cell averages, compare against analytical cell averages, including the sinc(k dx/2) factor. Report the initialization/measurement convention.
5. Refinement at matched physical final time, numerical stability and explicit CFL rejection.
6. PH composition/energy conservation, endpoint recovery and changing phase partition using the existing closure checks.

A passed mathematical test verifies this defined discretization and coupling. It does not establish physical phase-relaxation rates, experimental dispersion accuracy or operational safety.

## Upgrade path toward EEC550

The next physical-model decision must introduce compatible variable-density continuity, momentum and buoyancy; energy and component transport; a documented turbulence/atmosphere treatment; and local gas/liquid/ice closure with consistent enthalpy references. Common phase motion/temperature remains a conditional approximation until particle/relaxation applicability is justified.

Only after empty-atmosphere, conservative transport, phase-transition, mesh/time-step/domain checks should an open-domain flat-ground source case be compared against EEC550 sensors. Source placement, averaging history and concentration-basis unknowns remain declared assumptions. No terrain or propylene/Adoshi validation follows from this propane transport exercise.

## Primary numerical references

- [Clawpack Riemann book: advection](https://www.clawpack.org/riemann_book/html/Advection.html): conservation-law formulation and constant-speed translation solution.
- [Clawpack Riemann book: finite-volume methods](https://www.clawpack.org/riemann_book/html/Approximate_solvers.html): shared-interface flux conservation, CFL interpretation and first-order upwind numerical smearing. The combined diffusion restriction above is derived for this prototype, not quoted as a universal solver criterion.

[Source and phase limitations](WORKBENCH_V1.md) | [Existing handoff plan](EEC550_DISPERSION_HANDOFF.md)
