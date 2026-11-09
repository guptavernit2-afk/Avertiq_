# Conservative heat/phase coupling: model decision

9 November 2026. Scope: a small **one-dimensional compressible research prototype**, no product app.

## Why a separate coupled prototype

The preceding 2D solver uses frozen endpoint density and div(u)=0. Simply replacing that density with a PH result would violate its continuity constraint when heating or phase change changes volume. A material-cell isobaric heat/shear exchange calculation would be useful as an operator test, but would not complete conservative spatial flow coupling.

This milestone instead uses fixed-volume finite-volume cells, conserved component masses, momentum and **internal plus kinetic energy**, closed by a new UV equilibrium inversion. It is a separate 1D prototype; the existing 2D buoyancy code is not yet thermally coupled.

## Conserved equations and pressure work

With total energy density E = rho*e + rho*u^2/2, the one-dimensional equations are:

    d(rho*Y_i)/dt + d(rho*Y_i*u)/dx = 0
    d(rho*u)/dt + d(rho*u^2 + p)/dx = 0
    dE/dt + d[u*(E+p) - k*dT/dx]/dx = 0

Here Y_i counts each chemical component across gas, liquid and ice phases. There is one common velocity and temperature. Pressure work belongs in the energy flux u*(E+p); enthalpy must not be substituted for internal energy in E. Conduction redistributes energy through equal and opposite interface fluxes. Latent effects are already in the equilibrium phase enthalpies; there is no additional latent-heat source.

The conservative momentum flux replaces the previous velocity-form approximation for this 1D stage. Periodic shared-interface fluxes telescope, conserving component mass, momentum and total energy in the absence of external sources. Conservation alone does not establish flux accuracy or physical validity.

## Contact-resolving numerical flux

Use HLLC as the default approximate Euler interface flux, with Rusanov retained as an explicit comparison option. Both update every conserved component and total energy with a single shared interface flux. HLLC adds the contact wave between left/right acoustic-wave estimates; species star states scale with star density, while star total energy follows the Rankine-Hugoniot pressure-work relation.

The decisive regression is a stationary equal-pressure, zero-velocity composition/density interface with no conduction. The exact solution remains stationary. HLLC should preserve that case to the EOS/numerical tolerance. Rusanov diffuses conserved mixture states across the interface and can create spurious pressure changes with this nonlinear caloric/phase closure; conservation alone does not detect the error.

Compare every heated case with its matched zero-conduction control. Quantify pressure and velocity drift in the control before attributing a response to heat transfer. HLLC contact resolution does not guarantee pressure-equilibrium preservation for an advecting, numerically mixed general-EOS contact. The implementation is not validated for strong shocks, EOS nonconvexity or large phase-transition waves. Candidate states remain subject to UV-domain and positivity checks; failed steps are reduced or refused, not repaired by pressure clipping.

## UV equilibrium inversion

The public API is:

    EquilibriumUV(properties).solve(rho, component_mol_per_kg, e_J_kg)

The composition must describe exactly one kg of material. The target specific volume is v = 1/rho. For each trial pressure inside 50000–200000 Pa, call the existing solid-aware pressure/enthalpy solver with:

    H_target = e + p*v

Its returned volume defines residual V_PH(p) - v. A bounded pressure root enforces the requested volume; the recovered state then satisfies e = H - p*V. The inner PH solve preserves the existing melting lever rule and reviewed 180–300 K temperature domain.

Some trial pressures would require temperatures outside that domain. They are inadmissible bracket samples, not clipped states. Failure to find a valid bracket is an explicit failure. Positive finite density, finite internal energy, normalized component amounts, recovered volume and internal-energy residuals are numerical gates.

The code uses pressure hints to find nearby roots efficiently, with a bounded search fallback. It is not a general ThermoPack UV flash or an extension of the underlying property range.

## Sound speed and heat capacity

The numerical flux requires an equilibrium acoustic speed at fixed total composition. Using the UV pressure function:

    c^2 = (dp/drho)_e + p/rho^2 * (dp/de)_rho

Central finite differences evaluate the partial derivatives. Reject nonpositive or nonfinite c^2 and unavailable neighbouring states. A dry ideal-gas calculation must recover sqrt(gamma*p/rho); derivative-step refinement is checked. The internal-energy perturbation has a fixed physical J/kg scale, so arbitrary shifts of the enthalpy reference do not change the perturbation scale.

Constant-volume heat capacity is evaluated from central UV energy perturbations:

    cv = (de/dT)_rho

A resolved constant-temperature latent plateau returns infinite effective cv for timestep calculation, not an infinite value to serialize into JSON. This is a local numerical derivative, not an experimental transport property.

## Required numerical checks

- UV round trips for moist/ice, propane-condensing, warm and melting states.
- Pressure bracketing across the reviewed domain; invalid/unbracketable inputs fail closed.
- Component, volume and internal-energy residuals; energy-reference invariance.
- Dry-gas analytic sound speed and cv; derivative-step sensitivity.
- Uniform-state preservation, stationary equal-pressure composition contacts and conservative interface budgets.
- Heating at constant volume changes pressure/phase amounts consistently.
- Nonzero-conduction cases versus zero-conduction controls, with pressure and energy fluxes active.
- Grid/time sensitivity and phase/domain admissibility before any quantitative dispersion claim.

First-order finite-volume fluxes can smear contacts and redistribute kinetic/internal energy. Total-energy accounting must retain that redistribution, not independently reset temperature. Solver timestep restrictions and admissibility checks remain necessary; pressure or phase amounts must not be clipped to conceal an unstable step.

## Scientific and deployment limits

The reduced ideal-gas/pure-condensate equilibrium model still neglects gas nonideality, mutual solubility, slip, deposition, nucleation and finite phase rates. Its native condensed-volume and reference-saturation approximations are inherited. Numerical EOS stability is not experimental validation.

This prototype does not yet combine heat/phase feedback with the 2D buoyant atmospheric model. It does not provide an open-domain release, turbulence, ground heat transfer, terrain, EEC550 sensor comparison or an Adoshi hazard map. A future multidimensional low-Mach implementation must derive the EOS-compatible divergence constraint and couple pressure/momentum/energy consistently; the 1D conservative benchmark supplies regression evidence for that work.

## Primary references

- [Clawpack Euler equations](https://www.clawpack.org/riemann_book/html/Euler.html): conservation variables, momentum/pressure work and acoustic structure. Its ideal-polytropic EOS is not adopted for moist propane.
- [Castro hydrodynamics](https://amrex-astro.github.io/Castro/docs/Hydrodynamics.html): a primary example of HLLC among approximate solvers for general-EOS hydrodynamics. Its more complete implementation and accuracy claims are not adopted.
- [NASA enthalpy definition](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/enthalpy-2-2/): the distinction H=U+pV used to derive the UV inversion. No caloric-constant approximation from that introduction is used.
- [PeleLM low-Mach model](https://amrex-combustion.github.io/PeleLM/manual/html/Model.html): illustrates the need for an EOS-derived thermal/compositional divergence constraint. Its reacting ideal-gas formulation is not adopted.

[Existing thermodynamic limits](EEC550_EQUILIBRIUM_VERIFICATION.md) | [Prior frozen-density flow](VARIABLE_DENSITY_MODEL.md)
