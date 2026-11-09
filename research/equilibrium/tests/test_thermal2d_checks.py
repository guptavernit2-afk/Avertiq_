"""Independent coupled-2D verification must reject damaged conservative output."""
from copy import deepcopy
import json
import numpy as np
import pytest
from avertiq_equilibrium import thermal2d_checks as checks

@pytest.fixture(scope="module")
def report():
    return checks.run_thermal2d_checks()

def test_independent_runner_records_real_checks(report):
    assert report["passed"]
    assert len(report["checks"])>300
    assert all(c["passed"] for c in report["checks"])
    assert report["reference_checks"]["hydrostatic_maximum_speed_m_s"]<1e-7
    assert report["dimensional_reduction"]["normalized_conservative_difference"]<1e-8
    assert report["heat_control_response"]["pressure_Pa"]>1e-4
    assert report["gravity_control_response"]["maximum_vertical_velocity_difference_m_s"]>1e-8
    assert json.loads(json.dumps(report,allow_nan=False))["passed"]

def test_corrupt_energy_is_rejected(monkeypatch):
    original=checks.thermal2d.solve_thermal2d
    def damaged(*args,**kwargs):
        result=original(*args,**kwargs)
        result["final_conserved"][0][0][7]+=100.
        return result
    monkeypatch.setattr(checks.thermal2d,"solve_thermal2d",damaged)
    with pytest.raises(RuntimeError,match="hydrostatic conservative rest|total internal kinetic potential energy"):
        checks.run_thermal2d_checks()

def test_invalid_integral_array_is_rejected():
    with pytest.raises(RuntimeError):
        checks._integrals(np.zeros((4,4,7)),1.,1.)
