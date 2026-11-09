"""No output is published when thermal verification fails."""
import sys
import pytest
import avertiq_equilibrium.__main__ as cli

@pytest.mark.parametrize("command", ["thermal-flow", "thermal-checks"])
def test_property_failure_refuses_thermal_output(command, monkeypatch, tmp_path):
    output = tmp_path/"refused.json"
    monkeypatch.setattr(cli, "verify", lambda: {"passed":False})
    monkeypatch.setattr(sys, "argv", ["avertiq-equilibrium",command,"--output",str(output)])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 1
    assert not output.exists()

def test_failed_thermal_checks_refuse_output(monkeypatch,tmp_path):
    import avertiq_equilibrium.thermal_checks as checks
    output=tmp_path/"refused.json"
    monkeypatch.setattr(cli,"verify",lambda:{"passed":True})
    monkeypatch.setattr(checks,"run_thermal_checks",lambda:{"passed":False})
    monkeypatch.setattr(sys,"argv",["avertiq-equilibrium","thermal-checks","--output",str(output)])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 1
    assert not output.exists()
