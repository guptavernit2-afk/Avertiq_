"""Reusable conditional equilibrium study; no spatial or temporal transport."""
from dataclasses import dataclass
import math

import numpy as np

from .cases import AIR, feed, feed_energy, provenance
from .equilibrium import Equilibrium
from .mixing import DEFAULT_RATIOS
from .properties import COMPONENTS, PROPANE, WATER, Properties

SOURCE_IDS = ("H00", "H01", "H02", "H03")
DEFAULT_HUMIDITIES = (0., .5, .99)
PHASE_KEYS = ("gas", "propane_liquid", "water_liquid", "water_ice")


@dataclass
class SourceStream:
    state: object
    metadata: dict


@dataclass
class AmbientStream:
    mol_per_kg: np.ndarray
    enthalpy_J_kg: float
    metadata: dict


def _number(value, low, high, label):
    if isinstance(value, (bool, str, bytes)):
        raise ValueError(f"{label} must be a finite number")
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{label} must be a finite number") from exc
    if not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"{label} must be between {low} and {high}")
    return value


def _ratios(values):
    values = tuple(_number(v, 0., 100., "Added-air/source mass ratio") for v in values)
    if not values or tuple(sorted(set(values))) != values:
        raise ValueError("Ratios must be nonempty, unique and strictly increasing")
    return values


def build_source(properties, source_id="H00", pressure_Pa=102500.):
    """Keep original source feed assumptions fixed, independently of added air."""
    if source_id not in SOURCE_IDS:
        raise ValueError("Source must be H00, H01, H02 or H03; H04 is an audit")
    pressure = _number(pressure_Pa, 50000., 200000., "Pressure Pa")
    basis = "dry" if source_id == "H01" else "wet"
    dry = source_id == "H02"
    pin = 1115750. if source_id == "H03" else 1013250.
    totals = feed(properties, basis=basis, dry=dry)
    energy = feed_energy(properties, totals, feed_pressure=pin)
    state = Equilibrium(properties).ph(pressure, totals, energy["target_outgoing_thermal_W"])
    diagnostics = _checked_diagnostics(Equilibrium(properties), state, totals,
                                       energy["target_outgoing_thermal_W"])
    return SourceStream(state, {
        "case_id": source_id,
        "evidence_status": "conditional calculated source, not historical reconstruction",
        "feed_basis": basis,
        "counterfactual_dry_source": dry,
        "feed_ambient_temperature_K": 283.05,
        "feed_ambient_RH_assumed": .99,
        "feed_ambient_pressure_Pa": 102500.,
        "feed_pressure_Pa": pin,
        "source_pressure_Pa": pressure,
        "temperature_K": state.temperature_K,
        "mass_flow_kg_s": state.mass_kg,
        "thermal_enthalpy_flux_W": state.enthalpy_J,
        "energy_target_W": energy["target_outgoing_thermal_W"],
        "total_component_flow_mol_s": dict(zip(COMPONENTS, totals.tolist())),
        "total_component_mass_kg_s": dict(zip(COMPONENTS, (totals*properties.mw).tolist())),
        "diagnostics": diagnostics,
    })


def ambient_stream(properties, temperature_K=283.05, relative_humidity=.99,
                   pressure_Pa=102500.):
    """A one-kg gas stream; RH references the adopted liquid-water saturation."""
    t = _number(temperature_K, 273.16, 300., "Ambient temperature K")
    rh = _number(relative_humidity, 0., 1., "Relative humidity")
    pressure = _number(pressure_Pa, 50000., 200000., "Pressure Pa")
    # Use the same adopted curve as the thermodynamic closure at RH=1.
    psat = properties.saturation_fraction(t, pressure, WATER, "liquid")*pressure
    xw = rh*psat/pressure
    if not 0 <= xw < 1:
        raise ValueError("Invalid ambient water mole fraction")
    composition = (1-xw)*AIR.copy()
    composition[WATER] = xw
    amounts = composition / float(composition @ properties.mw)
    h = float(sum(amounts[i]*properties.gas_h(t, i) for i in range(len(COMPONENTS))))
    state = Equilibrium(properties).tp(t, pressure, amounts)
    condensed = state.ice_mol+state.water_liquid_mol+state.propane_liquid_mol
    if condensed > 1e-10 or not math.isfinite(h):
        raise RuntimeError("Declared ambient stream must be finite and gas-only")
    return AmbientStream(amounts, h, {
        "temperature_K": t, "relative_humidity": rh, "pressure_Pa": pressure,
        "humidity_definition": "relative to adopted normalized liquid-water saturation curve",
        "component_mol_per_kg": dict(zip(COMPONENTS, amounts.tolist())),
        "thermal_enthalpy_J_kg": h,
        "bulk_density_kg_m3": state.mass_kg/state.volume_m3,
    })


def _checked_diagnostics(model, state, totals, target):
    scalars = [state.temperature_K, state.pressure_Pa, state.mass_kg,
               state.volume_m3, state.enthalpy_J, state.propane_liquid_mol,
               state.water_liquid_mol, state.ice_mol, target]
    if (not np.isfinite(scalars).all() or not np.isfinite(state.gas_mol).all()
            or state.mass_kg <= 0 or state.volume_m3 <= 0
            or min(state.propane_liquid_mol, state.water_liquid_mol, state.ice_mol) < 0
            or (state.gas_mol < 0).any()):
        raise RuntimeError("Nonfinite or inadmissible equilibrium state")
    d = model.diagnostics(state, totals, target)
    residual = d["energy_residual_J_kg"]
    if (not math.isfinite(residual) or abs(residual) > 1.
            or not math.isfinite(d["maximum_component_relative_residual"])
            or d["maximum_component_relative_residual"] > 1e-8
            or not all(math.isfinite(x) for x in d["gas_saturation_ratios"].values())):
        raise RuntimeError("Equilibrium study conservation/phase diagnostic failed")
    return d


def _point(properties, model, source, ambient, ratio):
    added_mass = ratio*source.state.mass_kg
    totals = source.state.component_amounts()+added_mass*ambient.mol_per_kg
    target = source.state.enthalpy_J+added_mass*ambient.enthalpy_J_kg
    state = model.ph(source.state.pressure_Pa, totals, target)
    d = _checked_diagnostics(model, state, totals, target)
    phases = {
        "gas": float(state.gas_mol@properties.mw),
        "propane_liquid": float(state.propane_liquid_mol*properties.mw[PROPANE]),
        "water_liquid": float(state.water_liquid_mol*properties.mw[WATER]),
        "water_ice": float(state.ice_mol*properties.mw[WATER]),
    }
    return {
        "added_wet_air_to_source_mass_ratio": ratio,
        "added_wet_air_mass_kg_s": added_mass,
        "temperature_K": state.temperature_K, "pressure_Pa": state.pressure_Pa,
        "total_mass_kg_s": state.mass_kg,
        "total_component_flow_mol_s": dict(zip(COMPONENTS, totals.tolist())),
        "total_component_mass_kg_s": dict(zip(COMPONENTS, (totals*properties.mw).tolist())),
        "gas_component_flow_mol_s": dict(zip(COMPONENTS, state.gas_mol.tolist())),
        "gas_mole_fractions": dict(zip(COMPONENTS, (state.gas_mol/state.gas_mol.sum()).tolist())),
        "phase_mass_kg_s": phases,
        "phase_mass_fractions": {k:v/state.mass_kg for k,v in phases.items()},
        "bulk_density_kg_m3": state.mass_kg/state.volume_m3,
        "volume_flow_m3_s": state.volume_m3,
        "target_thermal_enthalpy_flux_W": target,
        "thermal_enthalpy_flux_W": state.enthalpy_J,
        "diagnostics": d,
    }


def solve_path(properties, source, ambient, ratios=DEFAULT_RATIOS):
    """Independent PH states; ratios prescribe mixing, not dynamics."""
    ratios = _ratios(ratios)
    if (not isinstance(source, SourceStream) or not isinstance(ambient, AmbientStream)):
        raise ValueError("Use build_source and ambient_stream to construct streams")
    amounts = np.asarray(ambient.mol_per_kg, dtype=float)
    if (amounts.shape != (len(COMPONENTS),) or not np.isfinite(amounts).all()
            or (amounts < 0).any() or not math.isfinite(ambient.enthalpy_J_kg)
            or not math.isclose(float(amounts@properties.mw), 1., rel_tol=1e-10)):
        raise ValueError("Ambient stream must contain one finite nonnegative kg")
    if source.state.pressure_Pa != ambient.metadata["pressure_Pa"]:
        raise ValueError("Source and ambient pressure must match")
    model = Equilibrium(properties)
    points = [_point(properties, model, source, ambient, v) for v in ratios]
    transitions = []
    for a,b in zip(points, points[1:]):
        for phase in PHASE_KEYS[1:]:
            present_a = a["phase_mass_kg_s"][phase] > 1e-12
            present_b = b["phase_mass_kg_s"][phase] > 1e-12
            if present_a != present_b:
                transitions.append({
                    "phase": phase, "change": "appears" if present_b else "disappears",
                    "lower_mass_ratio": a["added_wet_air_to_source_mass_ratio"],
                    "upper_mass_ratio": b["added_wet_air_to_source_mass_ratio"],
                    "presence_threshold_kg_s": 1e-12,
                    "interpretation": "sampled grid bracket, not exact transition or proof of monotonicity",
                })
    rh = ambient.metadata["relative_humidity"]
    return {
        "scenario_id": f'{source.metadata["case_id"]}-RH{rh}',
        "source_id": source.metadata["case_id"],
        "source": source.metadata, "ambient": ambient.metadata,
        "points": points, "transition_brackets": transitions,
        "summary": {
            "points": len(points),
            "maximum_abs_energy_residual_J_kg": max(abs(p["diagnostics"]["energy_residual_J_kg"]) for p in points),
            "maximum_component_relative_residual": max(p["diagnostics"]["maximum_component_relative_residual"] for p in points),
            "conservation_gate_passed": True,
        },
    }


def run_study(properties=None, source_ids=SOURCE_IDS,
              relative_humidities=DEFAULT_HUMIDITIES, ratios=DEFAULT_RATIOS,
              ambient_temperature_K=283.05, pressure_Pa=102500.):
    """Default: four fixed sources, three added-air RH values, eleven ratios."""
    ratios = _ratios(ratios)
    source_ids = tuple(source_ids)
    if not source_ids or len(set(source_ids)) != len(source_ids) or any(x not in SOURCE_IDS for x in source_ids):
        raise ValueError("Sources must be unique members of H00-H03")
    rhs = tuple(_number(x, 0., 1., "Relative humidity") for x in relative_humidities)
    if not rhs or len(set(rhs)) != len(rhs):
        raise ValueError("Humidities must be nonempty and unique")
    ambient_temperature_K = _number(ambient_temperature_K, 273.16, 300., "Ambient temperature K")
    pressure_Pa = _number(pressure_Pa, 50000., 200000., "Pressure Pa")
    p = properties or Properties()
    sources = [build_source(p, x, pressure_Pa) for x in source_ids]
    ambients = [ambient_stream(p, ambient_temperature_K, rh, pressure_Pa) for rh in rhs]
    paths = [solve_path(p, s, a, ratios) for s in sources for a in ambients]
    return {
        "schema_version": 1, "study_id": "EEC550-SOURCE-MIXING-SENSITIVITY-v1",
        "status": "conditional_0D_research_not_dispersion_or_field_validation",
        "model": p.label,
        "units": {"mass_flow": "kg/s", "component_flow": "mol/s", "enthalpy_flux": "W",
                  "temperature": "K", "pressure": "Pa", "density": "kg/m3", "volume_flow": "m3/s"},
        "ratio_definition": "added wet-air mass / original selected source total mass",
        "energy_policy": "Isobaric thermal-enthalpy mixing only; momentum and kinetic-energy conversion excluded",
        "assumptions": [
            "Source feed assumptions stay fixed at original ambient 283.05 K/RH99%; H02 alone removes source water.",
            "Added-air RH is a downstream mixing sensitivity, not reconstructed experimental weather.",
            "Instantaneous ideal-gas/pure-condensate equilibrium; no slip, phase rates or deposition.",
            "No distance, time, dilution rate, terrain or hazard-footprint prediction.",
            "Transition outputs are sampled brackets only; this study does not establish HEM relaxation applicability.",
        ],
        "provenance": provenance(),
        "summary": {
            "path_count": len(paths), "point_count": sum(len(x["points"]) for x in paths),
            "maximum_abs_energy_residual_J_kg": max(x["summary"]["maximum_abs_energy_residual_J_kg"] for x in paths),
            "maximum_component_relative_residual": max(x["summary"]["maximum_component_relative_residual"] for x in paths),
            "conservation_gate_passed": True, "dispersion_ready": False,
        },
        "paths": paths,
    }
