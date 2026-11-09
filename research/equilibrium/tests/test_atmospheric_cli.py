"""CLI verification gates for open-atmosphere research commands."""
import sys
import pytest
import avertiq_equilibrium.__main__ as cli

@pytest.mark.parametrize("command",["atmospheric","atmospheric-checks","atmospheric-refinement"])
def test_property_gate_refuses_atmospheric_outputs(command,monkeypatch,tmp_path):
    output=tmp_path/"refused.json"
    monkeypatch.setattr(cli,"verify",lambda:{"passed":False})
    monkeypatch.setattr(sys,"argv",["avertiq-equilibrium",command,"--output",str(output)])
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code==1
    assert not output.exists()

def test_failed_boundary_checks_refuse_output(monkeypatch,tmp_path):
    import avertiq_equilibrium.atmospheric_checks as checks
    output=tmp_path/"failed.json"
    monkeypatch.setattr(cli,"verify",lambda:{"passed":True})
    monkeypatch.setattr(checks,"run_atmospheric_checks",lambda:{"passed":False})
    monkeypatch.setattr(sys,"argv",["avertiq-equilibrium","atmospheric-checks","--output",str(output)])
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code==1
    assert not output.exists()
