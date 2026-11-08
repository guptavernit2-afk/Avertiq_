"""Conditional H00 plus ambient-air equilibrium mixing, not a plume calculation.

The entrainment ratio is added wet-air mass / original H00 total mass.
This is an isobaric thermal-enthalpy mixing path. Kinetic-energy conversion,
momentum, mixing rates, distance, time, slip and deposition are not modelled.
"""
import math

import numpy as np

from .cases import AIR, feed, feed_energy, provenance
from .equilibrium import Equilibrium
from .properties import COMPONENTS, PROPANE, WATER, Properties, water_reference_pressure

PRESSURE_PA = 102500.
AMBIENT_K = 283.05
AMBIENT_RH = .99
DEFAULT_RATIOS = (0., .1, .25, .5, 1., 2., 5., 10., 20., 50., 100.)
MAX_RATIO = 100.


def ambient_per_kg(properties):
    """Return gas component mol/kg and J/kg for the declared wet atmosphere."""
    xw = AMBIENT_RH*water_reference_pressure(AMBIENT_K)/PRESSURE_PA
    composition = (1-xw)*AIR.copy()
    composition[WATER] = xw
    amounts = composition / float(composition @ properties.mw)
    enthalpy = sum(amounts[i]*properties.gas_h(AMBIENT_K, i)
                   for i in range(len(COMPONENTS)))
    return amounts, float(enthalpy)


def validate_ratios(ratios):
    values = tuple(float(v) for v in ratios)
    if not values or any(not math.isfinite(v) or not 0 <= v <= MAX_RATIO
                         for v in values):
        raise ValueError("Mixing ratios must be finite and between 0 and 100")
    if len(set(values)) != len(values):
        raise ValueError("Mixing ratios must be unique")
    return values


def mix_point(properties, model, source, ambient_mol_kg, ambient_h_J_kg, ratio):
    """Mix existing source with a prescribed ambient mass; amounts are flows."""
    ratio = validate_ratios((ratio,))[0]
    added_mass = ratio*source.mass_kg
    added_mol = added_mass*ambient_mol_kg
    totals = source.component_amounts()+added_mol
    target = source.enthalpy_J+added_mass*ambient_h_J_kg
    state = model.ph(PRESSURE_PA, totals, target)
    diagnostics = model.diagnostics(state, totals, target)
    if diagnostics["maximum_component_relative_residual"] > 1e-8:
        raise RuntimeError("Mixing component conservation failed")
    if abs(diagnostics["energy_residual_J_kg"]) > 1.:
        raise RuntimeError("Mixing energy conservation failed")
    return state, totals, target, added_mass, diagnostics


def run_mixing(properties=None, ratios=DEFAULT_RATIOS):
    """Calculate a declared path. No spatial or temporal dispersion is solved."""
    ratios = validate_ratios(ratios)
    p = properties or Properties()
    eq = Equilibrium(p)
    source_n = feed(p)
    source_target = feed_energy(p, source_n)["target_outgoing_thermal_W"]
    source = eq.ph(PRESSURE_PA, source_n, source_target)
    ambient_n, ambient_h = ambient_per_kg(p)
    ambient_state = eq.tp(AMBIENT_K, PRESSURE_PA, ambient_n)
    if (ambient_state.ice_mol or ambient_state.water_liquid_mol
            or ambient_state.propane_liquid_mol):
        raise RuntimeError("Declared ambient air unexpectedly contains condensate")
    points = []
    for ratio in ratios:
        state, totals, target, added_mass, diagnostics = mix_point(
            p, eq, source, ambient_n, ambient_h, ratio)
        phase_mass = {
            "propane_liquid": state.propane_liquid_mol*p.mw[PROPANE],
            "water_liquid": state.water_liquid_mol*p.mw[WATER],
            "water_ice": state.ice_mol*p.mw[WATER],
        }
        gas_mass = float(state.gas_mol @ p.mw)
        phase_mass["gas"] = gas_mass
        points.append({
            "added_wet_air_to_H00_mass_ratio": ratio,
            "added_wet_air_mass_kg_s": added_mass,
            "total_component_flow_mol_s": dict(zip(COMPONENTS, totals.tolist())),
            "target_thermal_enthalpy_flux_W": target,
            "temperature_K": state.temperature_K,
            "pressure_Pa": state.pressure_Pa,
            "total_mass_kg_s": state.mass_kg,
            "gas_mole_fractions": dict(zip(
                COMPONENTS, (state.gas_mol/state.gas_mol.sum()).tolist())),
            "gas_component_flow_mol_s": dict(zip(COMPONENTS, state.gas_mol.tolist())),
            "phase_mass_kg_s": {k: float(v) for k, v in phase_mass.items()},
            "phase_mass_fractions": {k: float(v/state.mass_kg)
                                     for k, v in phase_mass.items()},
            "bulk_density_kg_m3": state.mass_kg/state.volume_m3,
            "volume_flow_m3_s": state.volume_m3,
            "thermal_enthalpy_flux_W": state.enthalpy_J,
            "diagnostics": diagnostics,
        })
    return {
        "schema_version": 1,
        "study_id": "EEC550-H00-MIXING-v1",
        "status": "conditional_0D_equilibrium_path_not_dispersion_or_field_validation",
        "model": p.label,
        "ratio_definition": "added wet-air mass / original H00 total mass",
        "ratio_range_reviewed": [0., MAX_RATIO],
        "energy_policy": "Conserve thermal enthalpy at fixed pressure; kinetic/potential energy and work excluded. This is not a dynamic mixing control volume.",
        "assumptions": [
            "Recompute conditional H00 from unchanged feed and energy definitions.",
            "Ambient wet air is 283.05 K, RH 0.99, 102500 Pa; ideal-gas composition.",
            "Instantaneous equilibrium; no phase slip, finite-rate nucleation, deposition or mixing rate.",
            "No prediction of distance, time, velocity, terrain flow or hazard footprint.",
            "Grid samples do not locate exact phase-transition ratios.",
            "The path is a diagnostic of the reduced model, not evidence for HEM relaxation times.",
        ],
        "ambient": {
            "temperature_K": AMBIENT_K, "relative_humidity": AMBIENT_RH,
            "pressure_Pa": PRESSURE_PA,
            "component_mol_per_kg": dict(zip(COMPONENTS, ambient_n.tolist())),
            "thermal_enthalpy_J_kg": ambient_h,
            "bulk_density_kg_m3": ambient_state.mass_kg/ambient_state.volume_m3,
        },
        "source": {
            "case_id": "H00",
            "temperature_K": source.temperature_K,
            "mass_flow_kg_s": source.mass_kg,
            "thermal_enthalpy_flux_W": source.enthalpy_J,
            "component_flow_mol_s": dict(zip(COMPONENTS, source_n.tolist())),
            "energy_target_W": source_target,
        },
        "provenance": provenance(),
        "points": points,
    }
