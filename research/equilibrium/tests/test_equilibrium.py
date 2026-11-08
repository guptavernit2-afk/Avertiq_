"""Numerical and thermodynamic checks; these are not field-validation tests."""
import json
import subprocess
import sys

import numpy as np
import pytest

from avertiq_equilibrium.properties import Properties, PROPANE, WATER
from avertiq_equilibrium.equilibrium import Equilibrium
from avertiq_equilibrium.cases import feed, run_cases
from avertiq_equilibrium.verification import verify


@pytest.fixture(scope="module")
def props():
    return Properties()


@pytest.fixture(scope="module")
def model(props):
    return Equilibrium(props)


def test_property_and_numerical_checkpoints():
    report = verify()
    assert report["passed"], [c for c in report["checks"] if not c["passed"]]
    # Failed candidates are reported rather than silently used.
    assert not report["rejected_property_candidate"]["accepted"]


def test_cold_mixed_condensates_and_complementarity(props, model):
    n = feed(props)
    s = model.tp(196., 102500., n)
    assert s.propane_liquid_mol > 0 and s.ice_mol > 0
    assert s.water_liquid_mol == 0
    diag = model.diagnostics(s, n)
    assert diag["maximum_component_relative_residual"] <= 1e-8
    assert all(abs(v-1) < 1e-9 for v in diag["gas_saturation_ratios"].values())


def test_warm_gas_and_liquid_water_limits(model):
    n = np.array([1., 100., 20., 1., 5.])
    warm_wet = model.tp(278., 102500., n)
    assert warm_wet.water_liquid_mol > 0 and warm_wet.ice_mol == 0
    n[WATER] = .0001
    dilute = model.tp(295., 102500., n)
    assert dilute.propane_liquid_mol == dilute.water_liquid_mol == dilute.ice_mol == 0
    assert all(v < 1 for v in model.diagnostics(dilute, n)["gas_saturation_ratios"].values())


def test_dry_limit_and_water_removal_preserves_other_feeds(props, model):
    moist, dry = feed(props), feed(props, dry=True)
    np.testing.assert_array_equal(moist[:WATER], dry[:WATER])
    s = model.tp(196., 102500., dry)
    assert s.gas_mol[WATER] == s.water_liquid_mol == s.ice_mol == 0


@pytest.mark.parametrize("scale", [.001, 1., 1000.])
@pytest.mark.parametrize("t", [190., 200., 210., 260., 280., 295.])
def test_ph_roundtrip_and_scale_invariance(props, model, scale, t):
    n = feed(props)*scale
    original = model.tp(t, 102500., n)
    s = model.ph(102500., n, original.enthalpy_J)
    assert abs(s.temperature_K-t) < 1e-6
    d = model.diagnostics(s, n, original.enthalpy_J)
    assert d["maximum_component_relative_residual"] < 1e-8
    assert abs(d["energy_residual_J_kg"]) < 1.
    assert (s.gas_mol >= 0).all()
    assert min(s.propane_liquid_mol, s.water_liquid_mol, s.ice_mol) >= 0


@pytest.mark.parametrize("ice_fraction", [.1, .5, .9])
def test_melting_latent_plateau(props, model, ice_fraction):
    n = feed(props)
    tm = props.melting_temperature(102500.)
    ice = model.tp(tm, 102500., n, water_phase="ice")
    liquid = model.tp(tm, 102500., n, water_phase="liquid")
    target = ice_fraction*ice.enthalpy_J+(1-ice_fraction)*liquid.enthalpy_J
    result = model.ph(102500., n, target)
    assert result.temperature_K == tm
    assert result.ice_mol/(result.ice_mol+result.water_liquid_mol) == pytest.approx(
        ice_fraction, abs=1e-8)
    assert abs(result.enthalpy_J-target)/result.mass_kg < 1.


def test_energy_reference_shift_does_not_change_solution(props, model):
    offset = 100000.
    class Shifted:
        def __getattr__(self, name):
            return getattr(props, name)
        def gas_h(self, t, i):
            return props.gas_h(t, i)+(offset if i == PROPANE else 0)
        def condensed(self, t, p, i, phase):
            h, g, v = props.condensed(t, p, i, phase)
            shift = offset if i == PROPANE else 0
            return h+shift, g+shift, v
    n = feed(props)
    original = model.tp(210., 102500., n)
    shifted = Equilibrium(Shifted()).ph(
        102500., n, original.enthalpy_J+offset*n[PROPANE])
    assert shifted.temperature_K == pytest.approx(210., abs=1e-6)
    np.testing.assert_allclose(shifted.component_amounts(), n, rtol=1e-12)


def test_random_component_budgets(props, model):
    rng = np.random.default_rng(42)
    for _ in range(25):
        n = rng.uniform(.01, 10., 5)
        t = float(rng.uniform(182., 299.))
        state = model.tp(t, 102500., n)
        assert model.diagnostics(state, n)["maximum_component_relative_residual"] < 1e-8


@pytest.mark.parametrize("t,p,n", [
    (179., 102500., [1, 4, 1, 1, .1]),
    (301., 102500., [1, 4, 1, 1, .1]),
    (200., 20000., [1, 4, 1, 1, .1]),
    (float("nan"), 102500., [1, 4, 1, 1, .1]),
    (200., 102500., [-1, 4, 1, 1, .1]),
    (200., 102500., [1, 0, 0, 0, .1]),
    (200., 102500., [1, 4]),
])
def test_invalid_inputs_fail(model, t, p, n):
    with pytest.raises(ValueError):
        model.tp(t, p, n)


def test_out_of_bracket_energy_fails(props, model):
    n = feed(props)
    target = model.tp(190., 102500., n).enthalpy_J
    with pytest.raises(ValueError):
        model.ph(102500., n, target, lower_K=220., upper_K=290.)


def test_eec550_energy_and_tp_audit(props):
    result = run_cases(props)
    assert len(result["cases"]) == 5
    for case in result["cases"]:
        assert sum(case["feed_mass_kg_s"].values()) == pytest.approx(case["state"]["mass_flow_kg_s"])
        assert case["feed_mass_kg_s"]["C3"] == pytest.approx(3., abs=1e-12)
        assert case["diagnostics"]["maximum_component_relative_residual"] < 1e-8
        if case["mode"] == "PH":
            energy = case["energy"]
            # Check the complete steady energy balance, independently of the PH target field.
            residual = (case["state"]["thermal_power_W"]+energy["outgoing_kinetic_W"]
                        -energy["thermal_in_W"]-energy["ambient_incoming_kinetic_W"])
            assert abs(residual)/case["state"]["mass_flow_kg_s"] < 1.
        else:
            assert case["state"]["temperature_K"] == 196.
            assert case["external_heat_required_for_TP_W"] != pytest.approx(0., abs=1.)
            assert case["state"]["propane_liquid_mol_s"] > 0
    assert not result["cases"][0]["is_historical_source_reconstruction"]


def test_cli_preserves_existing_output(tmp_path):
    output = tmp_path/"existing.json"
    output.write_text('{"preserve": true}')
    p = subprocess.run([sys.executable, "-m", "avertiq_equilibrium", "verify",
                        "--output", str(output)], capture_output=True, text=True)
    assert p.returncode != 0
    assert json.loads(output.read_text()) == {"preserve": True}


def test_cli_failed_verification_blocks_case_execution(monkeypatch, tmp_path):
    import avertiq_equilibrium.__main__ as cli
    output = tmp_path/"must_not_exist.json"
    monkeypatch.setattr(cli, "verify", lambda: {"passed": False})
    monkeypatch.setattr(sys, "argv", ["avertiq-equilibrium", "cases", "--output", str(output)])
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 1
    assert not output.exists()
