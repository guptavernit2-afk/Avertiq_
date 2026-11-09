"""Independent flow verification runner checks."""
import numpy as np
import pytest
from avertiq_equilibrium.flow_checks import run_flow_checks


def test_flow_verification_runner_passes_and_records_scope():
    record = run_flow_checks()
    assert record["passed"]
    assert len(record["checks"]) >= 20
    assert all(c["passed"] for c in record["checks"])
    assert "not HEM energy coupling" in record["scope"]
    assert record["projection"]["final_max_divergence_s_inv"] < 1e-8
    assert record["projection"]["initial_max_divergence_s_inv"] > 1.


def test_corrupt_projection_is_rejected(monkeypatch):
    import avertiq_equilibrium.flow_checks as checks
    def broken_projection(u,w,rho,dx,dz,dt):
        return u,w,np.zeros_like(rho),{}
    monkeypatch.setattr(checks.flow,"project_velocity",broken_projection)
    with pytest.raises(RuntimeError,match="projected divergence"):
        checks.run_flow_checks()
