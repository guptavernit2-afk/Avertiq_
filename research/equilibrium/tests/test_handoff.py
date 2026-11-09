"""Boundary-contract corruption tests, including non-gas propane sources."""
from copy import deepcopy

import pytest

from avertiq_equilibrium.cases import run_cases
from avertiq_equilibrium.handoff import export_handoff, validate_handoff


@pytest.fixture(scope="module")
def cases():
    return run_cases()


@pytest.fixture(scope="module")
def handoff(cases):
    return export_handoff(cases["cases"][0], cases["molar_masses_kg_mol"],
                          provenance=cases["provenance"])


def test_all_adiabatic_cases_export_and_validate(cases):
    for case in cases["cases"][:4]:
        record = export_handoff(case, cases["molar_masses_kg_mol"],
                                provenance=cases["provenance"])
        audit = validate_handoff(record)
        assert audit["passed"]
        assert len(audit["checks"]) >= 30
        assert record["run_ready"] is False
        assert record["source_energy"] == case["energy"]
        assert record["provenance"] == cases["provenance"]


def test_dry_H02_keeps_liquid_propane_in_component_and_phase_ledgers(cases):
    case = cases["cases"][2]
    record = export_handoff(case, cases["molar_masses_kg_mol"])
    b = record["boundary"]
    assert b["liquid_propane_mass_kg_s"] > .2
    assert b["ice_mass_kg_s"] == 0
    gas_propane = b["gas_mass_kg_s"]*b["gas_mass_fractions"]["C3"]
    assert gas_propane+b["liquid_propane_mass_kg_s"] == pytest.approx(3., abs=1e-10)
    assert b["phase_mass_fractions"]["liquid_propane"] > 0


def test_input_case_and_provenance_not_mutated(cases):
    before = deepcopy(cases)
    record = export_handoff(cases["cases"][0], cases["molar_masses_kg_mol"],
                            provenance=cases["provenance"])
    record["source_energy"]["thermal_in_W"] = 0
    record["provenance"]["packages"]["numpy"] = "mutated"
    assert cases == before


def test_H04_cannot_be_claimed_adiabatic(cases):
    with pytest.raises(ValueError, match="adiabatic"):
        export_handoff(cases["cases"][4], cases["molar_masses_kg_mol"])


def test_speed_change_requires_new_energy_solve(cases):
    with pytest.raises(ValueError, match="new PH"):
        export_handoff(cases["cases"][0], cases["molar_masses_kg_mol"],
                       source_speed_m_s=19.)


@pytest.mark.parametrize("key,value", [
    ("window_area_m2", .3042),
    ("bulk_density_kg_m3", 1.932),
    ("gas_mass_kg_s", 10.),
    ("ice_mass_kg_s", 0.),
    ("kinetic_energy_flux_W", 0.),
    ("thermal_enthalpy_flux_W", 0.),
    ("pressure_Pa", 1025.),
    ("ambient_static_pressure_Pa", 101325.),
    ("excess_pressure_Pa", 5.),
    ("temperature_K", 301.),
    ("window_width_m", float("nan")),
    ("window_height_m", -1.),
    ("speed_m_s", True),
    ("enthalpy_reference", ""),
])
def test_corrupt_boundary_rejected(handoff, key, value):
    record = deepcopy(handoff)
    record["boundary"][key] = value
    with pytest.raises(ValueError):
        validate_handoff(record)


def test_normalized_but_wrong_mole_mass_conversion_rejected(handoff):
    record = deepcopy(handoff)
    fractions = record["boundary"]["gas_mass_fractions"]
    fractions["C3"] += .01
    fractions["N2"] -= .01
    with pytest.raises(ValueError, match="basis|component"):
        validate_handoff(record)


def test_zero_component_must_not_hide_nonzero_gas_or_condensate(handoff):
    record = deepcopy(handoff)
    record["boundary"]["total_component_mass_kg_s"]["H2O"] = 0.
    with pytest.raises(ValueError, match="H2O total component"):
        validate_handoff(record)


def test_velocity_direction_not_just_magnitude(handoff):
    record = deepcopy(handoff)
    record["boundary"]["velocity_xyz_m_s"] = [18.1, 0., 0.]
    with pytest.raises(ValueError, match="direction"):
        validate_handoff(record)


@pytest.mark.parametrize("mutation", ["missing_component", "unit", "ready", "heat", "nonfinite_provenance"])
def test_structural_and_scope_errors_rejected(handoff, mutation):
    record = deepcopy(handoff)
    if mutation == "missing_component":
        del record["boundary"]["gas_mole_fractions"]["AR"]
    elif mutation == "unit":
        record["units"]["pressure"] = "bar_gauge"
    elif mutation == "ready":
        record["run_ready"] = True
    elif mutation == "heat":
        record["source_energy"]["external_heat_W_assumed"] = 100.
    else:
        record["provenance"]["invalid"] = float("inf")
    with pytest.raises(ValueError):
        validate_handoff(record)


def test_historical_v1_cannot_silently_pass_v2_validation(handoff):
    record = deepcopy(handoff)
    record["schema_version"] = 1
    with pytest.raises(ValueError, match="schema_version 2"):
        validate_handoff(record)


def test_valid_geometric_alternative_preserves_solved_energy(cases):
    record = export_handoff(cases["cases"][0], cases["molar_masses_kg_mol"],
                            azimuth_deg=90., aspect_ratio=1., centre_xyz_m=(5., 0., .8))
    b = record["boundary"]
    assert b["window_width_m"] == pytest.approx(b["window_height_m"])
    assert b["velocity_xyz_m_s"] == pytest.approx([18.1, 0., 0.], abs=1e-12)
    assert validate_handoff(record)["passed"]


@pytest.mark.parametrize("kwargs", [
    {"source_speed_m_s": 0.}, {"aspect_ratio": -1.},
    {"azimuth_deg": 360.}, {"centre_xyz_m": (1., 2.)},
    {"centre_xyz_m": (1., 2., -.1)},
])
def test_invalid_export_geometry_rejected(cases, kwargs):
    with pytest.raises(ValueError):
        export_handoff(cases["cases"][0], cases["molar_masses_kg_mol"], **kwargs)
