"""Independent stream ledgers and failure gates for conditional source studies."""
import json
from pathlib import Path

import numpy as np
import pytest

from avertiq_equilibrium.equilibrium import Equilibrium
from avertiq_equilibrium.properties import Properties, COMPONENTS, PROPANE, WATER
from avertiq_equilibrium.study import (
    ambient_stream, build_source, run_study, solve_path)


@pytest.fixture(scope="module")
def props():
    return Properties()


@pytest.fixture(scope="module")
def report(props):
    return run_study(props)


def test_default_matrix_and_original_H00_regression(report):
    assert report["summary"]["path_count"] == 12
    assert report["summary"]["point_count"] == 132
    assert report["summary"]["conservation_gate_passed"]
    assert not report["summary"]["dispersion_ready"]
    original = json.loads((Path(__file__).resolve().parents[3]/
                           "data/public/eec550-equilibrium-results.json").read_text(encoding="utf-8"))
    h00 = next(c for c in original["cases"] if c["case_id"] == "H00")["state"]
    for path in report["paths"]:
        if path["source_id"] == "H00":
            zero = path["points"][0]
            assert zero["temperature_K"] == pytest.approx(h00["temperature_K"], abs=1e-6)
            assert zero["total_mass_kg_s"] == pytest.approx(h00["mass_flow_kg_s"], rel=1e-12)


def test_independent_total_component_and_phase_ledgers(props, report):
    for path in report["paths"]:
        source = path["source"]
        ambient = path["ambient"]
        n0 = np.array([source["total_component_flow_mol_s"][k] for k in COMPONENTS])
        na = np.array([ambient["component_mol_per_kg"][k] for k in COMPONENTS])
        for point in path["points"]:
            added = point["added_wet_air_to_source_mass_ratio"]*source["mass_flow_kg_s"]
            expected = n0+added*na
            actual = np.array([point["gas_component_flow_mol_s"][k] for k in COMPONENTS])
            actual[PROPANE] += point["phase_mass_kg_s"]["propane_liquid"]/props.mw[PROPANE]
            actual[WATER] += (point["phase_mass_kg_s"]["water_liquid"]+
                              point["phase_mass_kg_s"]["water_ice"])/props.mw[WATER]
            np.testing.assert_allclose(actual, expected, rtol=1e-10, atol=1e-10)
            assert actual[PROPANE]*props.mw[PROPANE] == pytest.approx(3., abs=1e-10)
            assert sum(point["phase_mass_kg_s"].values()) == pytest.approx(
                source["mass_flow_kg_s"]+added, rel=1e-12)
            expected_h = source["thermal_enthalpy_flux_W"]+added*ambient["thermal_enthalpy_J_kg"]
            assert abs(point["thermal_enthalpy_flux_W"]-expected_h)/point["total_mass_kg_s"] < 1.
            assert sum(point["phase_mass_fractions"].values()) == pytest.approx(1., abs=1e-12)


def test_source_basis_is_independent_of_added_air(report):
    for source_id in ("H00", "H01", "H02", "H03"):
        sources = [p["source"] for p in report["paths"] if p["source_id"] == source_id]
        assert sources[0] == sources[1] == sources[2]
    source = {p["source_id"]:p["source"] for p in report["paths"]}
    assert source["H01"]["mass_flow_kg_s"] > source["H00"]["mass_flow_kg_s"]
    assert source["H02"]["total_component_flow_mol_s"]["H2O"] == 0
    assert source["H00"]["total_component_flow_mol_s"]["H2O"] > 0
    assert source["H03"]["feed_pressure_Pa"] > source["H00"]["feed_pressure_Pa"]


@pytest.mark.parametrize("rh", [0., .5, .99, 1.])
def test_gas_only_ambient_endpoint(props, rh):
    a = ambient_stream(props, relative_humidity=rh)
    assert a.mol_per_kg[PROPANE] == 0
    assert float(a.mol_per_kg@props.mw) == pytest.approx(1., abs=1e-12)
    state = Equilibrium(props).ph(a.metadata["pressure_Pa"], a.mol_per_kg, a.enthalpy_J_kg)
    assert state.temperature_K == pytest.approx(a.metadata["temperature_K"], abs=1e-6)
    assert state.ice_mol+state.water_liquid_mol+state.propane_liquid_mol < 1e-9


def test_warm_dry_mixing_reaches_all_gas(props):
    path = solve_path(props, build_source(props), ambient_stream(props, relative_humidity=0.))
    assert all(path["points"][-1]["phase_mass_kg_s"][k] == 0
               for k in ("propane_liquid", "water_liquid", "water_ice"))
    assert path["points"][-1]["temperature_K"] < 283.05


def test_humid_ice_to_liquid_is_bracketed_not_exact(report):
    path = next(p for p in report["paths"] if p["source_id"]=="H00"
                and p["ambient"]["relative_humidity"]==.99)
    assert path["points"][5]["phase_mass_kg_s"]["water_ice"] > path["points"][0]["phase_mass_kg_s"]["water_ice"]
    ice = next(t for t in path["transition_brackets"] if t["phase"]=="water_ice")
    assert ice["lower_mass_ratio"] == 2.
    assert ice["upper_mass_ratio"] == 5.
    assert "not exact" in ice["interpretation"]
    assert path["points"][-1]["phase_mass_kg_s"]["water_liquid"] > 0


@pytest.mark.parametrize("kwargs", [
    {"source_ids":[]}, {"source_ids":["H04"]}, {"source_ids":["H00","H00"]},
    {"relative_humidities":[]}, {"relative_humidities":[float("nan")]},
    {"relative_humidities":[-.1]}, {"relative_humidities":[1.1]},
    {"relative_humidities":[.5,.5]}, {"relative_humidities":[True]},
    {"ratios":[]}, {"ratios":[1.,0.]}, {"ratios":[0.,0.]},
    {"ratios":[float("inf")]}, {"ratios":[101.]}, {"ratios":[-.1]},
    {"ambient_temperature_K":273.}, {"ambient_temperature_K":300.1},
    {"ambient_temperature_K":float("nan")}, {"pressure_Pa":49999.},
    {"pressure_Pa":200001.}, {"pressure_Pa":"102500"},
])
def test_invalid_configuration_fails_before_native_creation(kwargs):
    with pytest.raises(ValueError):
        run_study(**kwargs)


def test_stream_pressure_mismatch_and_corruption_fail(props):
    source = build_source(props)
    ambient = ambient_stream(props, pressure_Pa=100000.)
    with pytest.raises(ValueError, match="pressure"):
        solve_path(props, source, ambient)
    ambient = ambient_stream(props)
    ambient.mol_per_kg[WATER] = float("nan")
    with pytest.raises(ValueError, match="finite"):
        solve_path(props, source, ambient)


def test_report_is_finite_strict_json(report):
    encoded = json.dumps(report, allow_nan=False)
    assert json.loads(encoded)["summary"]["point_count"] == 132
