"""Conditional H00--H04, with explicit feed and mechanical-energy bookkeeping."""
import hashlib
from importlib.metadata import version, distribution
from datetime import datetime, timezone
from pathlib import Path
import platform

import numpy as np

from .equilibrium import Equilibrium
from .properties import Properties, COMPONENTS, PROPANE, WATER, water_reference_pressure

# Assumed dry-air mixture; CO2 omitted, the remaining fractions normalized.
AIR = np.array([0., .78084, .20946, .00934, 0.])
AIR /= AIR.sum()


def feed(properties, basis="wet", dry=False):
    if basis not in ("wet", "dry"):
        raise ValueError("Unknown concentration basis")
    np_ = 3./properties.mw[PROPANE]  # nominal propane mass is preserved exactly
    xw = .99*water_reference_pressure(283.05)/102500.
    if basis == "wet":
        ndry, nw = 4*np_*(1-xw), 4*np_*xw
    else:
        ndry, nw = 4*np_, 4*np_*xw/(1-xw)
    n = ndry*AIR
    n[PROPANE] = np_
    n[WATER] = 0. if dry else nw
    return n


def feed_energy(properties, n, feed_pressure=1013250.):
    liquid_h = properties.condensed(286.45, feed_pressure, PROPANE, "liquid")[0]
    thermal = n[PROPANE]*liquid_h + sum(
        n[i]*properties.gas_h(283.05, i) for i in range(1, len(COMPONENTS)))
    mass = float(n @ properties.mw)
    ambient_mass = mass-3.
    incoming_ke = .5*ambient_mass*2.73**2
    outgoing_ke = .5*mass*18.1**2
    return {
        "thermal_in_W": float(thermal), "ambient_incoming_kinetic_W": incoming_ke,
        "propane_feed_kinetic_W_assumed": 0.,
        "outgoing_kinetic_W": outgoing_ke, "external_heat_W_assumed": 0.,
        "work_W_assumed": 0., "potential_change_W_assumed": 0.,
        "target_outgoing_thermal_W": float(thermal+incoming_ke-outgoing_ke),
    }


def provenance():
    directory = Path(__file__).parent
    return {
        "executed_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(), "platform": platform.platform(),
        "thermopack_native_sha256": {
            str(f): hashlib.sha256(distribution("thermopack").locate_file(f).read_bytes()).hexdigest()
            for f in distribution("thermopack").files
            if str(f).lower().endswith((".dll", ".so", ".dylib"))},
        "packages": {name: version(name) for name in ("thermopack", "numpy", "scipy")},
        "source_hash_basis": "UTF-8 text normalized to LF for Git/platform reproducibility",
        "source_sha256": {p.name: hashlib.sha256(p.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
                          for p in sorted(directory.glob("*.py"))},
    }


def run_cases(properties=None):
    p = properties or Properties()
    eq = Equilibrium(p)
    results = []
    for ident, basis, dry, pin in (
        ("H00", "wet", False, 1013250.), ("H01", "dry", False, 1013250.),
        ("H02", "wet", True, 1013250.), ("H03", "wet", False, 1115750.),
        ("H04", "wet", False, 1013250.)):
        n = feed(p, basis, dry)
        energy = feed_energy(p, n, pin)
        target = energy["target_outgoing_thermal_W"]
        state = eq.tp(196., 102500., n) if ident == "H04" else eq.ph(102500., n, target)
        diagnostics = eq.diagnostics(state, n, target)
        if diagnostics["maximum_component_relative_residual"] > 1e-8:
            raise RuntimeError(f"{ident}: component conservation failure")
        if ident != "H04" and abs(diagnostics["energy_residual_J_kg"]) > 1.:
            raise RuntimeError(f"{ident}: energy conservation failure")
        flow_state = state.as_dict()
        for old, new in {
            "gas_mol": "gas_mol_s", "propane_liquid_mol": "propane_liquid_mol_s",
            "water_liquid_mol": "water_liquid_mol_s", "ice_mol": "ice_mol_s",
            "enthalpy_J": "thermal_power_W", "volume_m3": "volume_flow_m3_s",
            "mass_kg": "mass_flow_kg_s"}.items():
            flow_state[new] = flow_state.pop(old)
        diagnostics["component_residual_mol_s"] = diagnostics.pop("component_residual_mol")
        results.append({
            "case_id": ident, "mode": "TP_audit" if ident == "H04" else "PH",
            "quantity_basis": "steady component flows mol/s and kg/s; thermal power W",
            "energy_target_enforced": ident != "H04",
            "assumption": {"concentration_feed_basis": basis, "counterfactual_dry": dry,
                           "feed_pressure_Pa": pin, "feed_temperature_K": 286.45,
                           "outlet_speed_prescribed_m_s": 18.1},
            "feed_mol_s": dict(zip(COMPONENTS, n.tolist())),
            "feed_mass_kg_s": dict(zip(COMPONENTS, (n*p.mw).tolist())),
            "energy": energy, "state": flow_state, "diagnostics": diagnostics,
            "implied_window_area_m2": state.volume_m3/18.1,
            "reference_window_area_m2": .3042,
            "external_heat_required_for_TP_W": (
                state.enthalpy_J-target if ident == "H04" else None),
            "is_historical_source_reconstruction": False,
        })
    return {
        "schema_version": 1, "model": p.label,
        "status": "conditional_reduced_model_results_not_field_validation",
        "scope": "0D only; ideal gas, pure immiscible condensates, instantaneous equilibrium",
        "assumptions": [
            "Source/feed concentration interpretations are assumptions.",
            "Dry air: specified normalized N2/O2/Ar; CO2 excluded.",
            "Water: reference-saturation Gibbs/enthalpy closure; no Poynting correction.",
            "Gas nonideality, condensate solubility, slip and phase kinetics are omitted.",
            "Melting at 273.16 K is a low-pressure approximation.",
            "ThermoPack native PR/ice energy closure was rejected by property screening.",
            "No source geometry, timing, CFD or operational validity is established."],
        "molar_masses_kg_mol": dict(zip(COMPONENTS, p.mw.tolist())),
        "provenance": provenance(), "cases": results,
    }
