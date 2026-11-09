# Integrated 2D thermal, phase and buoyancy model

9 November 2026. Scope: a small conservative two-dimensional research prototype; no product application.

## Formulation selected

Use a new 2D compressible finite-volume formulation that combines the preceding thermal UV closure with gravity. Retain the frozen-endpoint incompressible solver as a separate regression baseline. Its divergence-free projection is not used to overwrite density after a PH calculation.

The eight conserved cell quantities are five total component mass densities, horizontal momentum, vertical momentum and total energy including gravitational potential. With upward coordinate z, downward gravity of magnitude g and potential phi = g*z:

    rho = sum_i(rho*Y_i)
    E = rho*e + rho*(u*u+w*w)/2 + rho*phi
    d(rho*Y_i)/dt + div(rho*Y_i*v) = 0
    d(rho*u)/dt + div(rho*u*v + p*e_x) = 0
    d(rho*w)/dt + div(rho*w*v + p*e_z) = -rho*g
    dE/dt + div((E+p)*v - k*grad(T)) = 0

Component amounts include all gas, liquid and ice phases. A common velocity and temperature and instantaneous equilibrium remain model assumptions. There is no Boussinesq density approximation.

Density is determined by the conserved component masses. Internal energy is recovered by subtracting both kinetic components and phi from specific total energy. The existing bounded UV inversion then recovers absolute pressure, temperature and phase partition. Changes in thermal energy and phases therefore affect pressure, momentum and subsequent density transport; density is not reset independently of mass conservation.

## Gravity-compatible energy flux

A Riemann problem must use the gas energy, not a different gravitational offset on each side. Before constructing a face flux, remove each cell's rho*phi_cell from its conserved energy. Construct the Euler/HLLC gas flux, including transverse momentum, then add phi_face times the numerical total-mass flux to the energy flux.

For a static gravitational field this includes gravity work through potential-energy transport. Do not add a second -rho*g*w energy source to an energy variable that already includes gravitational potential. At the discrete level, the gas-energy change implied by this convention is tied to the same mass flux that moves potential energy.

Thermal conduction contributes equal-and-opposite shared face energy fluxes. Latent heat is already in the equilibrium phase properties; do not add it again. Negative caloric reference energies are permitted. They do not imply an inadmissible state; EOS domain and thermodynamic reconstruction supply the admissibility checks.

## Hydrostatic reference and well balancing

Unbalanced discretization can generate motion larger than the weak buoyant signal. The prototype therefore uses one declared fixed isothermal ambient hydrostatic reference, not an arbitrary frozen initial condition.

For the gas-only reference composition and temperature, let b = rho_reference/p_reference, which is constant for the adopted ideal-gas mixture. Set:

    p_reference(z_face) = p_bottom*exp(-g*b*z_face)
    rho_reference_cell = (p_bottom_face-p_top_face)/(g*dz)
    p_reference_cell = rho_reference_cell/b

The cell pressure and density are exact averages of that isothermal exponential profile. Their face pressure difference satisfies the discrete hydrostatic balance exactly. At g=0 use the uniform limit. An expm1-style difference avoids unnecessary cancellation.

For each shared face construct:

    F_balanced(Q) = F_numerical(Q) - F_numerical(Q_reference)
                    + F_physical_reference_face

The reference physical flux is zero except for normal momentum pressure. Apply the full vertical momentum source -rho*g. At the declared reference state, numerical deviations vanish and the reference pressure gradient cancels reference gravity. This is a prototype-specific fixed-reference flux/residual correction, not a claim to implement a published higher-order reconstruction scheme.

The correction is conservative because both cells share the same corrected face flux. For a fixed smooth physical hydrostatic reference it is a truncation-error correction that decreases on refinement. It must not be used to make an arbitrary nonhydrostatic state stationary. Supplied background data must remain compatible with the declared hydrostatic construction and EOS.

## Boundaries and budgets

Use horizontal periodicity and reflecting, impermeable, thermally insulating top and bottom boundaries. Wall-normal mass, energy and tangential-momentum fluxes are zero. Wall pressure exerts a vertical force.

The vertical wall traction is the *corrected numerical face pressure*: numerical wall momentum flux for Q minus that for the reference, plus reference face pressure. A vertical momentum budget must include this traction and the full gravitational impulse. It is incorrect to require vertical momentum to remain constant in a box subject to gravity and wall forces.

The closed domain conserves total component masses and total energy including potential. Internal-plus-kinetic energy alone can change as potential energy changes. Numerical integrals in the 2D section are per unit out-of-plane depth; they are not tanker inventory or release-rate measurements.

A zero-gravity comparison must remove gravitational potential from the initial energy and rebuild the reference. Removing g while retaining an initially stratified pressure field does not create a stationary control. Test uniform zero-gravity rest separately from the force-response comparison.

## Numerical acceptance checks

- Preserve the declared hydrostatic reference without spurious background motion.
- Preserve uniform zero-gravity states and stationary composition contacts as applicable.
- Verify directional HLLC fluxes and transverse momentum transport.
- Verify component masses, horizontal momentum and closed total-energy budgets.
- Verify vertical momentum against wall traction and gravitational impulse.
- Rebuild TP/UV thermodynamics independently from conserved density/internal energy, including phase/component budgets.
- Compare heat-on/off and gravity-on/off cases at matching settings and correctly transformed initial data.
- Check acoustic and conductive timestep bounds, positivity, failed EOS states and finite output; reject rather than clip.
- Record mesh/time/domain sensitivity before any quantitative flow-accuracy claim.

The finite-volume flux, source and face-potential convention must be tested together. A correct EOS or conserved scalar sum by itself does not establish correct buoyant flow.

## Limits before EEC550

This is a short, synthetic closed-box verification stage. It has no open atmospheric boundary, actual release inlet, wind shear, atmospheric turbulence, calibrated conductivity, ground heat exchange or terrain. The inherited reduced equilibrium model remains limited to 180–300 K and 50000–200000 Pa, and omits phase slip, finite phase rates, deposition and gas nonideality.

The exact reference preservation applies to the declared background, not every possible hydrostatic state. Conservative gravity/energy accounting does not establish long-time low-Mach accuracy, moving-contact accuracy, strong-wave behaviour or field dispersion validation. Future atmospheric release work still needs appropriate boundaries, atmosphere/source assumptions, transport closures and numerical studies before the EEC550 receptor comparison.

## Primary method references

- [Clawpack Euler equations](https://www.clawpack.org/riemann_book/html/Euler.html): conservative momentum, pressure work and internal-plus-kinetic energy.
- [Clawpack HLLC reference implementation](https://raw.githubusercontent.com/clawpack/riemann/master/riemann/euler_1D_py.py): contact-restoring jump relations; its ideal-gas Roe averaging is not adopted.
- [Edelmann et al. (2021), well-balanced gravity treatment](https://arxiv.org/abs/2102.13111): documents the risk of spurious flow near hydrostatic balance and the importance of gravitational energy and well balancing. Its stellar tests, higher-order reconstruction and low-Mach flux are not adopted or claimed as validation of this prototype.

[UV and thermal model](THERMAL_COUPLING_MODEL.md) | [Previous frozen-density model](VARIABLE_DENSITY_MODEL.md)
