"""Conservative mixing-path checks; not experimental validation."""
import json
import subprocess
import sys

import numpy as np
import pytest

from avertiq_equilibrium.cases import feed, feed_energy
from avertiq_equilibrium.equilibrium import Equilibrium
from avertiq_equilibrium.mixing import (
    AMBIENT_K, PRESSURE_PA, ambient_per_kg, mix_point, run_mixing)
from avertiq_equilibrium.properties import Properties, PROPANE, WATER


@pytest.fixture(scope="module")
def props():
    return Properties()


@pytest.fixture(scope="module")
def report(props):
    return run_mixing(props)


def test_zero_added_air_recovers_H00(props, report):
    eq = Equilibrium(props)
    n = feed(props)
    state = eq.ph(PRESSURE_PA, n, feed_energy(props, n)["target_outgoing_thermal_W"])
    point = report["points"][0]
    assert point["added_wet_air_to_H00_mass_ratio"] == 0
    assert point["temperature_K"] == pytest.approx(state.temperature_K, abs=1e-6)
    assert point["phase_mass_kg_s"]["water_ice"] == pytest.approx(state.ice_mol*props.mw[WATER])
    assert point["phase_mass_kg_s"]["propane_liquid"] == 0


def test_independent_component_and_enthalpy_ledgers(props, report):
    source = report["source"]
    ambient_n, ambient_h = ambient_per_kg(props)
    source_n = np.array(list(source["component_flow_mol_s"].values()))
    for point in report["points"]:
        added_mass = point["added_wet_air_to_H00_mass_ratio"]*source["mass_flow_kg_s"]
        expected_n = source_n+added_mass*ambient_n
        actual_n = np.array(list(point["gas_component_flow_mol_s"].values()))
        actual_n[PROPANE] += point["phase_mass_kg_s"]["propane_liquid"]/props.mw[PROPANE]
        actual_n[WATER] += (point["phase_mass_kg_s"]["water_ice"]+
                           point["phase_mass_kg_s"]["water_liquid"])/props.mw[WATER]
        np.testing.assert_allclose(actual_n, expected_n, rtol=1e-10, atol=1e-10)
        assert sum(point["phase_mass_kg_s"].values()) == pytest.approx(
            source["mass_flow_kg_s"]+added_mass, rel=1e-12)
        expected_h = source["thermal_enthalpy_flux_W"]+added_mass*ambient_h
        assert abs(point["thermal_enthalpy_flux_W"]-expected_h)/point["total_mass_kg_s"] < 1.
        assert sum(point["phase_mass_fractions"].values()) == pytest.approx(1., abs=1e-12)


def test_warm_ambient_limit_and_ice_extinction(report):
    first, last = report["points"][0], report["points"][-1]
    assert first["temperature_K"] < last["temperature_K"] < AMBIENT_K
    assert first["phase_mass_kg_s"]["water_ice"] > 0
    assert last["phase_mass_kg_s"]["water_ice"] == 0
    assert last["temperature_K"] > 273.16
    assert last["gas_mole_fractions"]["C3"] < first["gas_mole_fractions"]["C3"]


def test_ambient_basis_and_no_propane(props):
    n, h = ambient_per_kg(props)
    assert float(n @ props.mw) == pytest.approx(1., abs=1e-12)
    assert n[PROPANE] == 0
    state = Equilibrium(props).ph(PRESSURE_PA, n, h)
    assert state.temperature_K == pytest.approx(AMBIENT_K, abs=1e-6)
    assert state.ice_mol == state.water_liquid_mol == 0


@pytest.mark.parametrize("ratios", [[], [-.1], [101.], [float("nan")],
                                    [float("inf")], [0., 0.]])
def test_bad_ratios_fail_before_property_calls(ratios):
    with pytest.raises(ValueError):
        run_mixing(ratios=ratios)


def test_mix_point_rejects_bad_ratio(props):
    eq = Equilibrium(props)
    n = feed(props)
    source = eq.ph(PRESSURE_PA, n, feed_energy(props, n)["target_outgoing_thermal_W"])
    ambient_n, ambient_h = ambient_per_kg(props)
    with pytest.raises(ValueError):
        mix_point(props, eq, source, ambient_n, ambient_h, -.01)


def test_cli_failed_verification_blocks_mixing(monkeypatch, tmp_path):
    import avertiq_equilibrium.__main__ as cli
    output = tmp_path/"must_not_exist.json"
    monkeypatch.setattr(cli, "verify", lambda: {"passed": False})
    monkeypatch.setattr(sys, "argv", ["avertiq-equilibrium", "mixing", "--output", str(output)])
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 1
    assert not output.exists()


def test_cli_mixing_preserves_existing_output(tmp_path):
    output = tmp_path/"preserve.json"
    output.write_text('{"preserve":true}', encoding="utf-8")
    result = subprocess.run([sys.executable, "-m", "avertiq_equilibrium", "mixing",
                             "--output", str(output)], capture_output=True, text=True)
    assert result.returncode != 0
    assert json.loads(output.read_text(encoding="utf-8")) == {"preserve": True}
