"""Independent conservation, EOS feedback and heat-control checks.

These are numerical checks of the bounded 1D conservative Euler/HEM prototype,
not validation of thermal buoyant 2D flow or EEC550 atmospheric dispersion.
"""
import math
import numpy as np

from .cases import provenance
from .properties import Properties, COMPONENTS
from .study import build_source
from .equilibrium_uv import EquilibriumUV
from .equilibrium import Equilibrium


def _integrals(values, length):
    values = np.asarray(values, dtype=float)
    if values.ndim != 2 or values.shape[1] != 7 or not np.isfinite(values).all():
        raise RuntimeError("Thermal check: seven finite conservative columns required")
    return values.sum(axis=0)*(length/len(values))


def run_thermal_checks():
    from .thermal_flow import initialize_profile, solve_thermal_flow
    checks = []
    def bounded(name, measured, tolerance, units):
        measured = float(measured)
        passed = bool(math.isfinite(measured) and abs(measured) <= tolerance)
        checks.append({"name": name, "measured": measured, "maximum_absolute": tolerance,
                       "units": units, "passed": passed})
        if not passed:
            raise RuntimeError(f"Thermal check failed: {name}: {measured}")
    def positive(name, measured, minimum, units):
        measured = float(measured)
        passed = bool(math.isfinite(measured) and measured > minimum)
        checks.append({"name": name, "measured": measured, "must_exceed": minimum,
                       "units": units, "passed": passed})
        if not passed:
            raise RuntimeError(f"Thermal check failed: {name}: {measured}")

    p = Properties()
    tp_equilibrium = Equilibrium(p)
    initial = initialize_profile(p, cells=8, length_m=1.)
    options = dict(properties=p, length_m=1., duration_s=3e-4)
    without_heat = solve_thermal_flow(initial, conductivity_W_m_K=0., **options)
    with_heat = solve_thermal_flow(initial, conductivity_W_m_K=1000., **options)
    # Constant-pressure heterogeneous stationary material contacts must not be
    # mistaken for a physical thermal pressure response. The HLLC flux resolves
    # the contact wave; the no-conduction control should therefore stay at rest.
    control_pressure_drift = max(abs(cell["pressure_Pa"]-102500.)
                                 for cell in without_heat["cells"])
    control_speed = max(abs(cell["velocity_m_s"]) for cell in without_heat["cells"])
    control_conserved_drift = float(np.max(
        abs(np.asarray(without_heat["final_conserved"])-initial)/np.maximum(abs(initial),1.)))
    bounded("stationary heterogeneous contact pressure drift", control_pressure_drift,
            1e-3, "Pa")
    bounded("stationary heterogeneous contact velocity drift", control_speed,
            1e-7, "m/s")
    bounded("stationary heterogeneous contact conserved drift", control_conserved_drift,
            1e-8, "maximum normalized conserved-column residual")

    # Uniform composition/pressure/velocity: no pressure-wave or heat source.
    uniform = np.broadcast_to(initial[0], initial.shape).copy()
    uniform_case = solve_thermal_flow(uniform, conductivity_W_m_K=1000., **options)
    bounded("uniform conservative state preserved",
            np.max(abs(np.asarray(uniform_case["final_conserved"])-uniform)/np.maximum(abs(uniform),1.)), 1e-10,
            "maximum normalized conserved-column residual")

    # Independently assemble a velocity-reversal case, preserving internal energy.
    moving = uniform.copy()
    rho = moving[:,:5].sum(axis=1)
    old_ke = .5*moving[:,5]**2/rho
    velocities = np.where(np.arange(len(moving)) < len(moving)//2, 2., -2.)
    moving[:,5] = rho*velocities
    moving[:,6] += .5*rho*velocities**2-old_ke
    momentum_case = solve_thermal_flow(moving, conductivity_W_m_K=0., **options)
    q_after = np.asarray(momentum_case["final_conserved"])
    ke_before = float(np.sum(.5*moving[:,5]**2/rho)/len(moving))
    ke_after = float(np.sum(.5*q_after[:,5]**2/q_after[:,:5].sum(axis=1))/len(moving))
    positive("velocity-reversal kinetic energy transfer to internal energy",
             ke_before-ke_after, 1e-8, "J/m2")
    internal_before = float(moving[:,6].mean())-ke_before
    internal_after = float(q_after[:,6].mean())-ke_after
    bounded("kinetic loss equals internal-energy increase",
            (internal_after-internal_before)-(ke_before-ke_after), 1e-7, "J/m2")

    for label, state, original in (("no_heat", without_heat, initial),
                                    ("heat", with_heat, initial),
                                    ("uniform", uniform_case, uniform),
                                    ("momentum", momentum_case, moving)):
        final = np.asarray(state["final_conserved"])
        before, after = _integrals(original,1.), _integrals(final,1.)
        for i, component in enumerate(COMPONENTS):
            bounded(label+" conserved component "+component, after[i]-before[i],
                    1e-10*max(abs(before[i]),1.), "kg/m2")
        # Initial momentum can be zero: use an absolute tolerance.
        bounded(label+" total momentum", after[5]-before[5], 1e-8, "kg/(m s)")
        bounded(label+" total internal-plus-kinetic energy", after[6]-before[6],
                1e-9*max(abs(before[6]),1.), "J/m2")
        for index, cell in enumerate(state["cells"]):
            rho_cell = float(cell["density_kg_m3"])
            positive(label+f" cell {index} density", rho_cell, 0., "kg/m3")
            fractions = cell["phase_mass_fractions"]
            if not all(math.isfinite(v) and 0 <= v <= 1 for v in fractions.values()):
                raise RuntimeError("Thermal check failed: inadmissible phase fraction")
            if abs(sum(fractions.values())-1.) > 1e-9:
                raise RuntimeError("Thermal check failed: phase fractions do not sum to one")
            e_from_conserved = final[index,6]/rho_cell-.5*(final[index,5]/rho_cell)**2
            bounded(label+f" cell {index} internal-energy reconstruction",
                    cell["internal_energy_J_kg"]-e_from_conserved, 1e-6, "J/kg")
            # Rebuild the thermodynamic state through the independent TP path.
            # At ice/liquid coexistence, temperature and pressure alone do not
            # fix the lever fraction; use the reported split and test its energy.
            n_cell = np.array([cell["component_mol_per_kg"][c] for c in COMPONENTS])
            water_condensed = fractions["water_ice"]+fractions["water_liquid"]
            kwargs = {}
            t_cell = cell["temperature_K"]
            tm = p.melting_temperature(cell["pressure_Pa"])
            if (fractions["water_ice"] > 0 and fractions["water_liquid"] > 0):
                if abs(t_cell-tm) > 1e-6:
                    raise RuntimeError("Thermal check failed: water coexistence away from melting")
                t_cell = tm
                kwargs = {"water_phase":"ice",
                          "ice_fraction":fractions["water_ice"]/water_condensed}
            rebuilt = tp_equilibrium.tp(t_cell,cell["pressure_Pa"],n_cell,**kwargs)
            bounded(label+f" cell {index} independent TP volume closure",
                    rebuilt.volume_m3*rho_cell-1.,2e-8,"relative volume")
            rebuilt_e = rebuilt.enthalpy_J-rebuilt.pressure_Pa*rebuilt.volume_m3
            bounded(label+f" cell {index} independent H-PV energy closure",
                    rebuilt_e-e_from_conserved,.02,"J/kg")
            phase_component_mass_density = rebuilt.component_amounts()*p.mw*rho_cell
            bounded(label+f" cell {index} phase-component conservative density",
                    np.max(abs(phase_component_mass_density-final[index,:5])),
                    1e-9,"kg/m3")

    heat_q = np.asarray(with_heat["final_conserved"])
    control_q = np.asarray(without_heat["final_conserved"])
    heat_redistribution = float(np.max(abs(heat_q[:,6]-control_q[:,6])))
    positive("conduction redistributes energy relative to no-heat control",
             heat_redistribution, 1e-6, "J/m3")
    momentum_response = float(np.max(abs(heat_q[:,5]-control_q[:,5])))
    positive("conduction pressure response feeds back into momentum",
             momentum_response, 1e-8, "kg/(m2 s)")
    temperature_response = max(abs(a["temperature_K"]-b["temperature_K"])
                              for a,b in zip(with_heat["cells"],without_heat["cells"]))
    pressure_response = max(abs(a["pressure_Pa"]-b["pressure_Pa"])
                            for a,b in zip(with_heat["cells"],without_heat["cells"]))
    positive("conduction changes EOS pressure relative to no-heat control",
             pressure_response, 1e-4, "Pa")
    phase_response = max(abs(a["phase_mass_fractions"][phase]-b["phase_mass_fractions"][phase])
                         for a,b in zip(with_heat["cells"],without_heat["cells"])
                         for phase in ("water_ice","water_liquid","propane_liquid"))
    positive("conduction temperature response relative to numerical-mixing control",
             temperature_response, 1e-8, "K")
    positive("conduction phase response relative to numerical-mixing control",
             phase_response, 1e-12, "mass fraction")

    # Independent closed, fixed-volume H00 heating verifies real EOS pressure/
    # phase feedback rather than mistaking Rusanov contact mixing for heating.
    source = build_source(p).state
    n = source.component_amounts()/source.mass_kg
    rho = source.mass_kg/source.volume_m3
    e = (source.enthalpy_J-source.pressure_Pa*source.volume_m3)/source.mass_kg
    eos = EquilibriumUV(p)
    cold = eos.solve(rho,n,e)
    heated = eos.solve(rho,n,e+60000.)
    bounded("fixed-volume UV closure", heated.volume_m3-1./rho, 1e-9, "m3/kg")
    bounded("UV internal energy is H minus P V",
            heated.enthalpy_J-heated.pressure_Pa*heated.volume_m3-(e+60000.),
            1e-3,"J/kg")
    positive("fixed-volume heating raises pressure",
             heated.pressure_Pa-cold.pressure_Pa, 1000.,"Pa")
    positive("fixed-volume heating raises temperature",
             heated.temperature_K-cold.temperature_K, 1.,"K")
    ice_change = (cold.ice_mol-heated.ice_mol)*p.mw[-1]
    positive("fixed-volume heating changes ice partition", ice_change, 1e-5,"kg per kg")
    positive("phase feedback increases equilibrium gas moles",
             heated.gas_mol.sum()-cold.gas_mol.sum(),1e-5,"mol/kg")
    for i, component in enumerate(COMPONENTS):
        bounded("heated UV component "+component,
                heated.component_amounts()[i]-n[i],1e-10,"mol/kg")

    return {
        "schema_version":1,"passed":True,
        "scope":"Independent numerical checks of 1D conservative Euler/UV equilibrium coupling; not 2D buoyant thermal flow or experimental dispersion validation.",
        "checks":checks,
        "controls":{"without_heat":without_heat,"with_heat":with_heat,
                    "uniform":uniform_case,"momentum_reversal":momentum_case},
        "heat_control_response":{"maximum_energy_density_difference_J_m3":heat_redistribution,
                                 "maximum_temperature_difference_K":temperature_response,
                                 "maximum_momentum_density_difference_kg_m2_s":momentum_response,
                                 "maximum_pressure_difference_Pa":pressure_response,
                                 "maximum_condensate_mass_fraction_difference":phase_response,
                                 "conductivity_W_m_K":1000.,
                                 "meaning":"Synthetic stress parameter, not inferred industrial conductivity; compare the same contact-resolving HLLC scheme with zero conduction.",
                                 "no_heat_pressure_drift_Pa":control_pressure_drift,
                                 "no_heat_maximum_speed_m_s":control_speed,
                                 "no_heat_normalized_conserved_drift":control_conserved_drift},
        "fixed_volume_heating":{"density_kg_m3":rho,"added_internal_energy_J_kg":60000.,
                                "cold":cold.as_dict(),"heated":heated.as_dict(),
                                "ice_mass_loss_kg_per_kg":ice_change},
        "provenance":provenance(),
    }
