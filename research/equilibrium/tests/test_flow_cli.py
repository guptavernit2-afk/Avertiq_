"""CLI verification gates for buoyant research commands."""
import sys
import pytest
import avertiq_equilibrium.__main__ as cli

@pytest.mark.parametrize("command", ["flow", "flow-checks"])
def test_property_failure_blocks_flow_output(command, monkeypatch, tmp_path):
    output = tmp_path/"refused.json"
    monkeypatch.setattr(cli, "verify", lambda: {"passed": False})
    monkeypatch.setattr(sys, "argv", ["avertiq-equilibrium", command, "--output", str(output)])
    with pytest.raises(SystemExit) as failure:
        cli.main()
    assert failure.value.code == 1
    assert not output.exists()

def test_failed_flow_checks_do_not_publish(monkeypatch, tmp_path):
    import avertiq_equilibrium.flow_checks as checks
    output = tmp_path/"failed.json"
    monkeypatch.setattr(cli, "verify", lambda: {"passed": True})
    monkeypatch.setattr(checks, "run_flow_checks", lambda: {"passed": False})
    monkeypatch.setattr(sys, "argv", ["avertiq-equilibrium", "flow-checks", "--output", str(output)])
    with pytest.raises(SystemExit) as failure:
        cli.main()
    assert failure.value.code == 1
    assert not output.exists()
