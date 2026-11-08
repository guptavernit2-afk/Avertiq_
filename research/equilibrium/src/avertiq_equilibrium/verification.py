"""Independent property checkpoints and numerical conservation checks."""
import math

import numpy as np

from .cases import feed, feed_energy, provenance
from .equilibrium import Equilibrium
from .properties import (Properties, NativePRProperties, PROPANE, WATER,
                         propane_reference_pressure, ice_reference_pressure)


def verify():
    p, native = Properties(), NativePRProperties()
    eq = Equilibrium(p)
    checks, candidates = [], []
    def add(name, actual, reference, absolute_tolerance):
        error = abs(actual-reference)
        checks.append({"check": name, "actual": float(actual),
                       "reference": float(reference),
                       "absolute_tolerance": float(absolute_tolerance),
                       "passed": bool(error <= absolute_tolerance)})
    for t in (196., 200., 230.):
        reference = propane_reference_pressure(t)
        add(f"C3 pure EOS pressure {t}K", p.pure_propane_saturation(t),
            reference, .005*reference)
        # Separate the error introduced by treating gas fugacity as ideal.
        add(f"C3 reduced ideal-gas saturation {t}K",
            102500.*p.saturation_fraction(t, 102500., PROPANE, "liquid"),
            reference, .05*reference)
        candidates.append({
            "temperature_K": t,
            "native_PR_ice_pressure_Pa": native.saturation_fraction(
                t, 102500., WATER, "ice")*102500.,
            "IAPWS_ice_pressure_Pa": ice_reference_pressure(t),
            "candidate_accepted": False,
        })
    for t, pressure in ((196., .08692625514), (230., 8.94735), (273.16, 611.657)):
        model = p.saturation_fraction(t, 102500., WATER, "ice")*102500.
        add(f"ice reference pressure {t}K", model, pressure, max(1e-9, pressure*1e-6))
    fusion = (p.condensed(273.16, 102500., WATER, "liquid")[0] -
              p.condensed(273.16, 102500., WATER, "ice")[0])/p.mw[WATER]
    add("water fusion enthalpy J/kg", fusion, 333426.516, 5000.)
    # Thermodynamic identity independently evaluated by finite differencing G.
    for i, phase, t in ((PROPANE, "liquid", 200.), (WATER, "ice", 210.),
                        (WATER, "liquid", 283.)):
        h, g, _ = p.condensed(t, 102500., i, phase)
        step = .001
        dg = (p.condensed(t+step, 102500., i, phase)[1] -
              p.condensed(t-step, 102500., i, phase)[1])/(2*step)
        add(f"h=G-T*dG/dT {i} {phase}", h, g-t*dg, .05)
    n = feed(p)
    for t in (190., 200., 210., 260., 280., 295.):
        state = eq.tp(t, 102500., n)
        recovered = eq.ph(102500., n, state.enthalpy_J)
        diag = eq.diagnostics(recovered, n, state.enthalpy_J)
        add(f"PH roundtrip {t}K", recovered.temperature_K, t, 1e-6)
        add(f"PH mass residual {t}K", diag["maximum_component_relative_residual"], 0., 1e-8)
        add(f"PH energy residual {t}K", diag["energy_residual_J_kg"], 0., 1.)
    tm = p.melting_temperature(102500.)
    si = eq.tp(tm, 102500., n, water_phase="ice")
    sl = eq.tp(tm, 102500., n, water_phase="liquid")
    target = .5*(si.enthalpy_J+sl.enthalpy_J)
    melting = eq.ph(102500., n, target)
    add("melting plateau temperature", melting.temperature_K, tm, 1e-8)
    add("melting plateau ice fraction", melting.ice_mol /
        (melting.ice_mol+melting.water_liquid_mol), .5, 1e-8)
    add("melting energy residual J/kg", (melting.enthalpy_J-target)/melting.mass_kg, 0., 1.)
    return {
        "schema_version": 1, "passed": all(c["passed"] for c in checks),
        "model": p.label, "provenance": provenance(),
        "meaning": "Property checkpoints and numerical verification; not experimental validation.",
        "tolerance_basis": ("Pre-case engineering screens: pure C3 pressure 0.5%, "
                            "ideal-gas reduced threshold 5%; water fusion 5 kJ/kg; "
                            "mass 1e-8 relative, energy 1 J/kg. Not accuracy guarantees."),
        "rejected_property_candidate": {
            "description": "Native PR water/ice Gibbs reference with ideal gas",
            "reason": "Large ice-pressure discrepancies against IAPWS",
            "accepted": False, "points": candidates},
        "checks": checks,
    }
