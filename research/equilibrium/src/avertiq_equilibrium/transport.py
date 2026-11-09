"""Conservative 1D kinematic scalar dispersion and equilibrium diagnostics.

This is a fixed-reference-mass advection/diffusion verification prototype.
Prescribed velocity/diffusivity do not respond to equilibrium density.
It is not compressible, buoyant, terrain-dependent or EEC550 field dispersion.
"""
import math
import numpy as np
from .cases import provenance
from .equilibrium import Equilibrium
from .properties import Properties, COMPONENTS, PROPANE, WATER
from .study import build_source, ambient_stream


def _finite(value, name):
    if isinstance(value, (bool, str, bytes)):
        raise ValueError(f"{name} must be numeric")
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be finite") from exc
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def solve_scalar(initial, *, length_m=100., velocity_m_s=1.,
                 diffusivity_m2_s=.05, duration_s=10., cfl=.8):
    """Periodic upwind advection + centred diffusion, forward Euler in time.

    f_new = f - C*(f-f_upwind) + D*(f_right-2*f+f_left)
    |C|+2D <= cfl <= 1 makes each update a convex combination.
    No clipping or source/sink is applied.
    """
    f = np.asarray(initial, dtype=float)
    if f.ndim != 1 or len(f) < 4 or not np.isfinite(f).all():
        raise ValueError("Initial scalar needs at least four finite cell averages")
    if (f < 0).any() or (f > 1).any():
        raise ValueError("Initial source mass fraction must lie in [0,1]")
    length = _finite(length_m, "length")
    velocity = _finite(velocity_m_s, "velocity")
    diffusion = _finite(diffusivity_m2_s, "diffusivity")
    duration = _finite(duration_s, "duration")
    cfl = _finite(cfl, "CFL")
    if length <= 0 or diffusion < 0 or duration < 0 or not 0 < cfl <= 1:
        raise ValueError("Positive length, nonnegative diffusion/time and CFL in (0,1] required")
    dx = length/len(f)
    rate = abs(velocity)/dx+2*diffusion/dx**2
    steps = max(1, math.ceil(duration*rate/cfl))
    if steps > 1000000:
        raise ValueError("Requested run exceeds one million explicit steps")
    dt = duration/steps
    courant = velocity*dt/dx
    fourier = diffusion*dt/dx**2
    original = f.copy()
    initial_sum = float(f.sum())
    for _ in range(steps):
        left, right = np.roll(f, 1), np.roll(f, -1)
        advective = (f-left) if velocity >= 0 else (right-f)
        f = f-courant*advective+fourier*(right-2*f+left)
        if not np.isfinite(f).all() or f.min() < -1e-12 or f.max() > 1+1e-12:
            raise RuntimeError("Scalar positivity/finite-state gate failed")
    residual = float(f.sum()-initial_sum)
    relative = abs(residual)/max(abs(initial_sum), 1.)
    if relative > 1e-10:
        raise RuntimeError("Periodic scalar mass conservation failed")
    return {
        "x_m": ((np.arange(len(f))+.5)*dx).tolist(),
        "initial_fraction": original.tolist(), "final_fraction": f.tolist(),
        "configuration": {"cells": len(f), "length_m": length,
                          "velocity_m_s": velocity, "diffusivity_m2_s": diffusion,
                          "duration_s": duration, "boundary": "periodic"},
        "numerics": {"scheme": "first-order upwind advection; central diffusion; forward Euler",
                     "steps": steps, "dt_s": dt, "dx_m": dx,
                     "courant": courant, "fourier": fourier,
                     "positivity_weight_sum": abs(courant)+2*fourier,
                     "leading_upwind_numerical_diffusivity_m2_s": abs(velocity)*dx*(1-abs(courant))/2,
                     "numerical_diffusivity_note": "Leading modified-equation estimate, not extra physical diffusion; refine grid/time to assess error"},
        "diagnostics": {"scalar_sum_residual": residual,
                        "relative_scalar_mass_residual": relative,
                        "minimum_fraction": float(f.min()), "maximum_fraction": float(f.max()),
                        "passed": True},
    }


def run_transport(properties=None, *, cells=100, length_m=100.,
                  velocity_m_s=1., diffusivity_m2_s=.05, duration_s=10., cfl=.8):
    """Synthetic pulse transport followed by local per-kg PH diagnostics.

    A uniform reference mass per cell is assumed for transport. Conserved
    component mol/kg and thermal h/kg are affine functions of f. PH density
    is diagnostic only; variable-volume expansion/momentum are not solved.
    """
    if isinstance(cells, bool) or not isinstance(cells, int) or not 8 <= cells <= 1000:
        raise ValueError("cells must be an integer from 8 to 1000")
    length = _finite(length_m, "length")
    if length <= 0:
        raise ValueError("length must be positive")
    x = (np.arange(cells)+.5)*length/cells
    initial = .8*np.exp(-.5*((x-.25*length)/(.06*length))**2)
    transport = solve_scalar(initial, length_m=length, velocity_m_s=velocity_m_s,
                             diffusivity_m2_s=diffusivity_m2_s,
                             duration_s=duration_s, cfl=cfl)
    p = properties or Properties()
    source = build_source(p, "H00")
    ambient = ambient_stream(p)
    source_n = source.state.component_amounts()/source.state.mass_kg
    source_h = source.state.enthalpy_J/source.state.mass_kg
    eq = Equilibrium(p)
    points = []
    max_energy = 0.
    max_component = 0.
    for position, fraction in zip(transport["x_m"], transport["final_fraction"]):
        n = fraction*source_n+(1-fraction)*ambient.mol_per_kg
        target = fraction*source_h+(1-fraction)*ambient.enthalpy_J_kg
        state = eq.ph(102500., n, target)
        diagnostics = eq.diagnostics(state, n, target)
        energy = abs(diagnostics["energy_residual_J_kg"])
        component = diagnostics["maximum_component_relative_residual"]
        if not math.isfinite(energy) or energy > 1 or component > 1e-8:
            raise RuntimeError("Local equilibrium conservation failed")
        max_energy = max(max_energy, energy)
        max_component = max(max_component, component)
        phases = {"propane_liquid": state.propane_liquid_mol*p.mw[PROPANE],
                  "water_liquid": state.water_liquid_mol*p.mw[WATER],
                  "water_ice": state.ice_mol*p.mw[WATER],
                  "gas": float(state.gas_mol@p.mw)}
        points.append({"x_m": position, "source_mass_fraction": fraction,
                       "temperature_K": state.temperature_K,
                       "gas_propane_mole_fraction": float(state.gas_mol[PROPANE]/state.gas_mol.sum()),
                       "component_mol_per_kg": dict(zip(COMPONENTS,n.tolist())),
                       "thermal_enthalpy_J_kg": state.enthalpy_J,
                       "phase_mass_fractions": {k: float(v/state.mass_kg) for k,v in phases.items()},
                       "diagnostic_equilibrium_density_kg_m3": state.mass_kg/state.volume_m3,
                       "diagnostics": diagnostics})
    f0 = np.asarray(transport["initial_fraction"])
    f1 = np.asarray(transport["final_fraction"])
    before_n = f0[:,None]*source_n+(1-f0[:,None])*ambient.mol_per_kg
    after_n = f1[:,None]*source_n+(1-f1[:,None])*ambient.mol_per_kg
    before_h = f0*source_h+(1-f0)*ambient.enthalpy_J_kg
    after_h = f1*source_h+(1-f1)*ambient.enthalpy_J_kg
    return {
        "schema_version": 1, "model": "1D periodic prescribed-coefficient scalar advection-diffusion",
        "status": "synthetic_kinematic_transport_verification_not_field_dispersion",
        "field_prediction_ready": False, "CFD_validation_claim": False,
        "assumptions": [
            "Synthetic Gaussian sampled at cell centres then treated as discrete cell averages; no experimental initial condition.",
            "First-order upwind adds numerical diffusion; analytical convergence tests quantify discretization error.",
            "Fixed reference mass per cell; uniform prescribed velocity and diffusivity.",
            "Local equilibrium is postprocessed from conserved mass fraction and thermal enthalpy.",
            "Equilibrium density is diagnostic only; no pressure, expansion, momentum or buoyancy coupling.",
            "Periodic boundaries recirculate material; not an open atmospheric domain.",
            "No terrain, gravity current, turbulence closure, phase slip or finite-rate physics.",
            "No EEC550 receptor comparison, Adoshi footprint or operational safety inference.",
        ],
        "source": source.metadata, "ambient": ambient.metadata,
        "transport": transport, "equilibrium_cells": points,
        "conservation": {
            "component_sum_residual_mol_per_kg_cells": dict(zip(COMPONENTS,(after_n.sum(axis=0)-before_n.sum(axis=0)).tolist())),
            "thermal_enthalpy_sum_residual_J_per_kg_cells": float(after_h.sum()-before_h.sum()),
            "maximum_local_energy_residual_J_kg": max_energy,
            "maximum_local_component_relative_residual": max_component,
        },
        "provenance": provenance(),
    }
