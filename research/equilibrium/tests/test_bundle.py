"""Bundle failure isolation, provenance and CLI configuration checks."""
import hashlib
import json

import pytest

from avertiq_equilibrium import bundle


def test_existing_directory_is_never_reused(tmp_path, monkeypatch):
    output = tmp_path/"run"
    output.mkdir()
    marker = output/"keep.txt"
    marker.write_text("original", encoding="utf-8")
    monkeypatch.setattr(bundle, "verify", lambda: pytest.fail("must refuse before verification"))
    with pytest.raises(FileExistsError):
        bundle.create_bundle(output)
    assert marker.read_text(encoding="utf-8") == "original"


def test_verification_failure_publishes_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(bundle, "verify", lambda: {"passed": False})
    with pytest.raises(RuntimeError, match="verification"):
        bundle.create_bundle(tmp_path/"run")
    assert not (tmp_path/"run").exists()


def test_render_failure_leaves_no_partial_bundle(tmp_path, monkeypatch):
    import avertiq_equilibrium.study as study
    import avertiq_equilibrium.cases as cases
    import avertiq_equilibrium.report as report
    monkeypatch.setattr(bundle, "verify", lambda: {"passed": True})
    monkeypatch.setattr(study, "run_study", lambda **kwargs: {"provenance": {}})
    monkeypatch.setattr(cases, "run_cases", lambda: {"cases": [], "provenance": {}})
    def fail(_):
        raise ValueError("invalid report")
    monkeypatch.setattr(report, "render_report", fail)
    with pytest.raises(ValueError, match="invalid report"):
        bundle.create_bundle(tmp_path/"run")
    assert not (tmp_path/"run").exists()


def test_manifest_matches_exact_artifact_bytes(tmp_path, monkeypatch):
    import avertiq_equilibrium.study as study
    import avertiq_equilibrium.cases as cases
    import avertiq_equilibrium.handoff as handoff
    import avertiq_equilibrium.report as report
    monkeypatch.setattr(bundle, "verify", lambda: {"passed": True, "checks": []})
    monkeypatch.setattr(study, "run_study", lambda **kwargs: {"provenance": {}, "paths": []})
    monkeypatch.setattr(cases, "run_cases", lambda: {
        "cases": [{"case_id": "H00"}, {"case_id": "H04"}],
        "provenance": {}, "molar_masses_kg_mol": {}})
    monkeypatch.setattr(handoff, "export_handoff", lambda c, m, **kw: {"case_id": c["case_id"]})
    monkeypatch.setattr(handoff, "validate_handoff", lambda r: {"passed": True})
    monkeypatch.setattr(report, "render_report", lambda _: "<p>offline\nreport</p>")
    output = tmp_path/"run"
    manifest = bundle.create_bundle(output)
    assert manifest["source_contracts_passed"] == 1
    assert set(manifest["files"]) == {"verification.json", "study.json", "handoffs.json", "report.html"}
    for name, details in manifest["files"].items():
        data = (output/name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == details["sha256"]
        assert len(data) == details["bytes"]
        assert b"\r\n" not in data
    assert json.loads((output/"handoffs.json").read_text(encoding="utf-8"))["cases"][0]["source"]["case_id"] == "H00"
    assert not list(tmp_path.glob(".avertiq-bundle-*"))


def test_cli_passes_explicit_study_options(monkeypatch, tmp_path):
    import sys
    import avertiq_equilibrium.__main__ as cli
    import avertiq_equilibrium.study as study
    received = {}
    def calculate(**options):
        received.update(options)
        return {"paths": [], "provenance": {}}
    monkeypatch.setattr(cli, "verify", lambda: {"passed": True})
    monkeypatch.setattr(study, "run_study", calculate)
    monkeypatch.setattr(sys, "argv", ["avertiq-equilibrium", "study", "--output",
        str(tmp_path/"study.json"), "--sources", "H00", "H02",
        "--relative-humidities", "0", "0.99", "--ratios", "0", "1",
        "--ambient-temperature", "283.05", "--pressure", "102500"])
    assert cli.main() == 0
    assert received == {"source_ids": ["H00", "H02"], "relative_humidities": [0., .99],
                        "ratios": [0., 1.], "ambient_temperature_K": 283.05, "pressure_Pa": 102500.}
