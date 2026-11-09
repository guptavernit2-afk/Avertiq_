"""Verification gates for integrated 2D thermal buoyancy commands."""
import sys
import pytest
import avertiq_equilibrium.__main__ as cli

@pytest.mark.parametrize("command",["thermal2d","thermal2d-checks"])
def test_property_gate_blocks_integrated_run(command,monkeypatch,tmp_path):
    output=tmp_path/"refused.json"
    monkeypatch.setattr(cli,"verify",lambda:{"passed":False})
    monkeypatch.setattr(sys,"argv",["avertiq-equilibrium",command,"--output",str(output)])
    with pytest.raises(SystemExit) as failure:
        cli.main()
    assert failure.value.code==1
    assert not output.exists()

def test_failed_2d_checks_do_not_publish(monkeypatch,tmp_path):
    import avertiq_equilibrium.thermal2d_checks as checks
    output=tmp_path/"failed.json"
    monkeypatch.setattr(cli,"verify",lambda:{"passed":True})
    monkeypatch.setattr(checks,"run_thermal2d_checks",lambda:{"passed":False})
    monkeypatch.setattr(sys,"argv",["avertiq-equilibrium","thermal2d-checks","--output",str(output)])
    with pytest.raises(SystemExit) as failure:
        cli.main()
    assert failure.value.code==1
    assert not output.exists()
