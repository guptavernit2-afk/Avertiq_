"""Strict arithmetic source boundary contract; not CFD input or validation.

Only existing adiabatic conditional PH cases may be exported. The contract
preserves all gas/liquid/ice component flows and the source enthalpy reference.
It cannot establish phase rates, historical accuracy or transport capability.
"""
from copy import deepcopy
from datetime import datetime, timezone
import math

COMPONENTS = ("C3", "N2", "O2", "AR", "H2O")
UNITS = {
    "mass_flow": "kg/s", "molar_mass": "kg/mol", "pressure": "Pa_absolute",
    "temperature": "K", "enthalpy": "J/kg", "energy_flux": "W",
    "volume_flow": "m3/s", "density": "kg/m3", "length": "m",
    "area": "m2", "speed": "m/s", "momentum_flux": "N",
    "gas_fractions": "dimensionless_gas_phase", "phase_fractions": "dimensionless_total_mass",
}


def _finite(value, name, *, minimum=None, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name}: finite number required")
    if not math.isfinite(value):
        raise ValueError(f"{name}: finite number required")
    if positive and value <= 0 or minimum is not None and value < minimum:
        raise ValueError(f"{name}: out of range")
    return float(value)


def _no_nonfinite(value, path="record"):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{path}: nonfinite value")
    if isinstance(value, dict):
        for key, item in value.items():
            _no_nonfinite(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for i, item in enumerate(value):
            _no_nonfinite(item, f"{path}[{i}]")


def _components(values, name, *, positive=False):
    if not isinstance(values, dict) or set(values) != set(COMPONENTS):
        raise ValueError(f"{name}: exactly {COMPONENTS} required")
    return {k: _finite(values[k], f"{name}.{k}", minimum=0, positive=positive)
            for k in COMPONENTS}


def _vector(value, name):
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError(f"{name}: three coordinates required")
    return [_finite(v, name) for v in value]


def export_handoff(case_result, molar_masses, *, source_speed_m_s=18.1,
                   azimuth_deg=30.0, centre_xyz_m=(2.5, 4.330127018922193, .5),
                   aspect_ratio=2.0, provenance=None):
    """Export a conditional PH source, deriving area at the solved source speed.

    Changing speed needs a new source energy solve: this function deliberately
    refuses a speed differing from the case's prescribed outlet speed.
    provenance may contain the run_cases report's provenance dictionary.
    """
    if not isinstance(case_result, dict):
        raise ValueError("case_result: dictionary required")
    _no_nonfinite(case_result)
    if (case_result.get("case_id") not in ("H00", "H01", "H02", "H03")
            or case_result.get("mode") != "PH"
            or case_result.get("energy_target_enforced") is not True
            or case_result.get("is_historical_source_reconstruction") is not False):
        raise ValueError("Only conditional adiabatic H00-H03 PH cases may be exported")
    mw = _components(molar_masses, "molar_masses", positive=True)
    speed = _finite(source_speed_m_s, "source_speed_m_s", positive=True)
    azimuth = _finite(azimuth_deg, "azimuth_deg")
    if not 0 <= azimuth < 360:
        raise ValueError("azimuth_deg must be in [0,360)")
    aspect = _finite(aspect_ratio, "aspect_ratio", positive=True)
    centre = _vector(centre_xyz_m, "centre_xyz_m")
    if centre[2] < 0:
        raise ValueError("Source centre must not be below ground")
    try:
        state = case_result["state"]
        original_speed = case_result["assumption"]["outlet_speed_prescribed_m_s"]
        if not math.isclose(speed, original_speed, rel_tol=1e-12, abs_tol=1e-12):
            raise ValueError("Source speed change requires a new PH/kinetic-energy solve")
        gas_mol = _components(state["gas_mol_s"], "gas_mol_s")
        total_component = _components(case_result["feed_mass_kg_s"], "feed_mass_kg_s")
        gas_mass = sum(gas_mol[k]*mw[k] for k in COMPONENTS)
        gas_moles = sum(gas_mol.values())
        _finite(gas_mass, "gas_mass", positive=True)
        total = _finite(state["mass_flow_kg_s"], "total_mass", positive=True)
        volume = _finite(state["volume_flow_m3_s"], "volume_flow", positive=True)
        area = volume/speed
        height = math.sqrt(area/aspect)
        thermal = _finite(state["thermal_power_W"], "thermal_power_W")
        ice = state["ice_mol_s"]*mw["H2O"]
        lp = state["propane_liquid_mol_s"]*mw["C3"]
        lw = state["water_liquid_mol_s"]*mw["H2O"]
        kinetic = case_result["energy"]["outgoing_kinetic_W"]
        b = {
            "pressure_Pa": state["pressure_Pa"],
            "ambient_static_pressure_Pa": state["pressure_Pa"],
            "excess_pressure_Pa": 0.0,
            "temperature_K": state["temperature_K"],
            "total_component_mass_kg_s": total_component,
            "total_mass_kg_s": total, "gas_mass_kg_s": gas_mass,
            "ice_mass_kg_s": ice, "liquid_propane_mass_kg_s": lp,
            "liquid_water_mass_kg_s": lw,
            "gas_mole_fractions": {k: gas_mol[k]/gas_moles for k in COMPONENTS},
            "gas_mass_fractions": {k: gas_mol[k]*mw[k]/gas_mass for k in COMPONENTS},
            "phase_mass_fractions": {"gas": gas_mass/total, "ice": ice/total,
                                     "liquid_propane": lp/total, "liquid_water": lw/total},
            "bulk_density_kg_m3": state["bulk_density_kg_m3"],
            "bulk_volume_flow_m3_s": volume,
            "thermal_enthalpy_flux_W": thermal,
            "thermal_enthalpy_J_kg": thermal/total,
            "enthalpy_reference": "Reduced ThermoPack/reference-saturation closure; map species and phase offsets before any different property package.",
            "kinetic_energy_flux_W": kinetic,
            "total_enthalpy_plus_kinetic_flux_W": thermal+kinetic,
            "speed_m_s": speed,
            "velocity_xyz_m_s": [speed*math.sin(math.radians(azimuth)),
                                speed*math.cos(math.radians(azimuth)), 0.0],
            "advective_momentum_flux_magnitude_N": total*speed,
            "pressure_thrust_assumption": "Zero excess-pressure thrust; advective momentum only.",
            "normal_azimuth_deg": azimuth,
            "window_area_m2": area, "window_width_m": aspect*height,
            "window_height_m": height, "aspect_ratio_width_to_height": aspect,
            "window_centre_xyz_m": centre,
            "coordinates": "X east; Y magnetic north; Z up; origin original nozzle",
            "source_profile": "Assumed uniform top hat; common phase velocity and temperature",
        }
        record = {
            "schema_version": 2, "id": f"EEC550-{case_result['case_id']}-HANDOFF-v2",
            "status": "conditional_candidate_not_solver_input",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "CFD_run_authorized": False, "CFD_runs_completed": 0, "run_ready": False,
            "is_historical_source_reconstruction": False, "units": dict(UNITS),
            "molar_masses_kg_mol": mw,
            "source_case": {"case_id": case_result["case_id"], "mode": "PH",
                            "energy_target_enforced": True,
                            "assumption": deepcopy(case_result["assumption"])},
            "source_energy": deepcopy(case_result["energy"]),
            "provenance": deepcopy(provenance) if provenance is not None else {
                "status": "caller_case_dictionary; supply run provenance for archived export"},
            "evidence_status": {"source": "conditional reduced-model calculation",
                                "geometry": "assumed uniform rectangular inlet",
                                "pressure": "assumed downstream absolute pressure",
                                "enthalpy": "same reference as source calculation; not an absolute energy zero"},
            "boundary": b,
        }
    except (KeyError, TypeError, ZeroDivisionError) as exc:
        raise ValueError(f"Malformed PH source case: {exc}") from exc
    validate_handoff(record)
    return record


def validate_handoff(record):
    """Validate v2 arithmetic/labels; return an audit or fail with ValueError."""
    if not isinstance(record, dict):
        raise ValueError("handoff must be a dictionary")
    _no_nonfinite(record)
    checks = []

    def match(name, actual, expected, *, absolute=1e-9, relative=1e-9):
        a = _finite(actual, name)
        e = _finite(expected, name)
        residual = abs(a-e)
        tolerance = max(absolute, relative*max(abs(a), abs(e)))
        if residual > tolerance:
            raise ValueError(f"{name}: inconsistent ({a!r} versus {e!r})")
        checks.append({"name": name, "absolute_residual": residual,
                       "tolerance": tolerance, "passed": True})

    try:
        if type(record["schema_version"]) is not int or record["schema_version"] != 2:
            raise ValueError("Strict handoff validation requires schema_version 2")
        if record["units"] != UNITS:
            raise ValueError("Units must match the v2 SI/absolute-pressure contract")
        if (record["status"] != "conditional_candidate_not_solver_input"
                or record["run_ready"] is not False
                or record["CFD_run_authorized"] is not False
                or type(record["CFD_runs_completed"]) is not int
                or record["CFD_runs_completed"] != 0
                or record["is_historical_source_reconstruction"] is not False):
            raise ValueError("Conditional research scope flags must be retained")
        source = record["source_case"]
        if (source["case_id"] not in ("H00", "H01", "H02", "H03")
                or source["mode"] != "PH" or source["energy_target_enforced"] is not True):
            raise ValueError("Only adiabatic PH sources H00-H03 are valid")
        if not isinstance(record["provenance"], dict) or not record["provenance"]:
            raise ValueError("Source provenance dictionary required")
        evidence = record["evidence_status"]
        if not all(isinstance(evidence[k], str) and evidence[k].strip()
                   for k in ("source", "geometry", "pressure", "enthalpy")):
            raise ValueError("Source evidence/reference labels required")
        mw = _components(record["molar_masses_kg_mol"], "molar masses", positive=True)
        b = record["boundary"]
        p = _finite(b["pressure_Pa"], "absolute pressure", positive=True)
        t = _finite(b["temperature_K"], "temperature", positive=True)
        if not 50000 <= p <= 200000 or not 180 <= t <= 300:
            raise ValueError("Source is outside reviewed equilibrium pressure/temperature domain")
        match("ambient static pressure", b["ambient_static_pressure_Pa"], p)
        match("excess pressure", b["excess_pressure_Pa"], 0, absolute=1e-12)
        total = _finite(b["total_mass_kg_s"], "total mass", positive=True)
        gm = _finite(b["gas_mass_kg_s"], "gas mass", positive=True)
        masses = {"gas": gm, "ice": _finite(b["ice_mass_kg_s"], "ice mass", minimum=0),
                  "liquid_propane": _finite(b["liquid_propane_mass_kg_s"], "liquid propane", minimum=0),
                  "liquid_water": _finite(b["liquid_water_mass_kg_s"], "liquid water", minimum=0)}
        match("phase mass sum", sum(masses.values()), total)
        fractions = b["phase_mass_fractions"]
        if set(fractions) != set(masses):
            raise ValueError("Four phase mass fractions required")
        for phase, mass in masses.items():
            _finite(fractions[phase], f"{phase} fraction", minimum=0)
            match(f"{phase} mass fraction", fractions[phase], mass/total, absolute=1e-12)
        match("phase fraction sum", sum(fractions.values()), 1, absolute=1e-12)
        components = _components(b["total_component_mass_kg_s"], "total components")
        x = _components(b["gas_mole_fractions"], "gas mole fractions")
        y = _components(b["gas_mass_fractions"], "gas mass fractions")
        match("gas mole fraction sum", sum(x.values()), 1, absolute=1e-12)
        match("gas mass fraction sum", sum(y.values()), 1, absolute=1e-12)
        mean_mw = sum(x[k]*mw[k] for k in COMPONENTS)
        for k in COMPONENTS:
            match(f"{k} gas mole/mass basis", y[k], x[k]*mw[k]/mean_mw, absolute=1e-12)
            condensed = masses["liquid_propane"] if k == "C3" else (
                masses["ice"]+masses["liquid_water"] if k == "H2O" else 0.)
            match(f"{k} total component", gm*y[k]+condensed, components[k])
        match("component mass sum", sum(components.values()), total)
        match("nominal propane feed", components["C3"], 3.0)
        volume = _finite(b["bulk_volume_flow_m3_s"], "volume flow", positive=True)
        density = _finite(b["bulk_density_kg_m3"], "bulk density", positive=True)
        speed = _finite(b["speed_m_s"], "speed", positive=True)
        match("source solved speed", speed, source["assumption"]["outlet_speed_prescribed_m_s"])
        velocity = _vector(b["velocity_xyz_m_s"], "velocity")
        match("velocity magnitude", math.sqrt(sum(v*v for v in velocity)), speed)
        angle = _finite(b["normal_azimuth_deg"], "normal azimuth")
        if not 0 <= angle < 360:
            raise ValueError("normal azimuth must be in [0,360)")
        for axis, expected in enumerate((speed*math.sin(math.radians(angle)),
                                         speed*math.cos(math.radians(angle)), 0.0)):
            match(f"velocity direction {axis}", velocity[axis], expected)
        centre = _vector(b["window_centre_xyz_m"], "window centre")
        if centre[2] < 0:
            raise ValueError("Source centre is below ground")
        area = _finite(b["window_area_m2"], "area", positive=True)
        width = _finite(b["window_width_m"], "width", positive=True)
        height = _finite(b["window_height_m"], "height", positive=True)
        aspect = _finite(b["aspect_ratio_width_to_height"], "aspect", positive=True)
        match("rectangular area", width*height, area)
        match("window aspect ratio", width/height, aspect)
        match("volume flow", area*speed, volume)
        match("bulk density/mass", density*volume, total)
        kinetic = _finite(b["kinetic_energy_flux_W"], "kinetic energy", minimum=0)
        match("outgoing kinetic energy", kinetic, .5*total*speed**2, absolute=1e-6)
        match("advective momentum", b["advective_momentum_flux_magnitude_N"], total*speed)
        thermal = _finite(b["thermal_enthalpy_flux_W"], "thermal enthalpy")
        if not isinstance(b["enthalpy_reference"], str) or not b["enthalpy_reference"].strip():
            raise ValueError("Enthalpy reference description required")
        match("specific thermal enthalpy", b["thermal_enthalpy_J_kg"], thermal/total)
        match("total energy flux", b["total_enthalpy_plus_kinetic_flux_W"], thermal+kinetic, absolute=1e-6)
        energy = record["source_energy"]
        thermal_in = _finite(energy["thermal_in_W"], "source thermal input")
        incoming = _finite(energy["ambient_incoming_kinetic_W"], "ambient kinetic input", minimum=0)
        feed_ke = _finite(energy["propane_feed_kinetic_W_assumed"], "propane kinetic input", minimum=0)
        q = _finite(energy["external_heat_W_assumed"], "heat")
        work = _finite(energy["work_W_assumed"], "work")
        potential = _finite(energy["potential_change_W_assumed"], "potential energy")
        match("adiabatic heat assumption", q, 0, absolute=1e-12)
        match("kinetic energy source ledger", kinetic, energy["outgoing_kinetic_W"], absolute=1e-6)
        target = thermal_in+incoming+feed_ke+q-work-potential-kinetic
        match("source target definition", energy["target_outgoing_thermal_W"], target, absolute=1e-5)
        match("source thermal target", thermal, target, absolute=1e-5)
    except (KeyError, TypeError, ZeroDivisionError) as exc:
        raise ValueError(f"Malformed handoff contract: {exc}") from exc
    return {"schema_version": 1, "passed": True, "handoff_id": record.get("id"),
            "scope": "Arithmetic contract checks only; not transport or physical validation",
            "checks": checks}
