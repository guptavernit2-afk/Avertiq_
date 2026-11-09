"""Independent runner checks and deliberate ledger corruption."""
from copy import deepcopy
import json

import numpy as np
import pytest

from avertiq_equilibrium.thermal_checks import run_thermal_checks, _integrals


@pytest.fixture(scope="module")
def report():
    return run_thermal_checks()


def test_coupled_thermal_verification(report):
    assert report["passed"] and all(c["passed"] for c in report["checks"])
    # Exercise the exact CLI serialization contract, including finite scalars.
    assert json.loads(json.dumps(report, allow_nan=False))["passed"]
    response = report["heat_control_response"]
    assert response["no_heat_pressure_drift_Pa"] < 1e-3
    assert response["no_heat_maximum_speed_m_s"] < 1e-7
    assert response["no_heat_normalized_conserved_drift"] < 1e-8
    assert response["maximum_temperature_difference_K"] > .01
    assert response["maximum_pressure_difference_Pa"] > .01
    assert response["maximum_condensate_mass_fraction_difference"] > 1e-7
    assert response["maximum_momentum_density_difference_kg_m2_s"] > 1e-5
    heating = report["fixed_volume_heating"]
    assert heating["heated"]["pressure_Pa"] > heating["cold"]["pressure_Pa"]
    assert heating["ice_mass_loss_kg_per_kg"] > 1e-5


def test_corrupted_total_energy_is_detected(report, monkeypatch):
    import avertiq_equilibrium.thermal_flow as solver
    controls = report["controls"]
    reports = [deepcopy(controls[name]) for name in
               ("without_heat", "with_heat", "uniform", "momentum_reversal")]
    reports[1]["final_conserved"][0][6] += 100.
    monkeypatch.setattr(solver, "solve_thermal_flow", lambda *a, **k: reports.pop(0))
    with pytest.raises(RuntimeError, match="heat total internal-plus-kinetic energy"):
        run_thermal_checks()


@pytest.mark.parametrize("values", [np.ones((8,6)), np.full((8,7),float("nan"))])
def test_malformed_conservative_ledgers_refused(values):
    with pytest.raises(RuntimeError, match="seven finite"):
        _integrals(values,1.)
