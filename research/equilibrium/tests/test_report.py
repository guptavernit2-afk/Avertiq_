"""Offline renderer validation and injection/overwrite protection."""
from copy import deepcopy
import json
import re

import pytest

from avertiq_equilibrium.report import render_report, write_report


@pytest.fixture
def study():
    return {
        "study_id": "test-study", "model": "conditional model",
        "energy_policy": "Thermal enthalpy only; no momentum.",
        "assumptions": ["No distance or time prediction."], "provenance": {"version": "test"},
        "paths": [{
            "scenario_id": "H00-RH0990", "source_id": "H00",
            "ambient": {"relative_humidity": .99},
            "points": [{
                "added_wet_air_to_source_mass_ratio": 0.,
                "temperature_K": 204.3, "bulk_density_kg_m3": 1.94,
                "phase_mass_fractions": {"gas": .995, "water_ice": .005,
                                         "water_liquid": 0., "propane_liquid": 0.},
                "diagnostics": {"maximum_component_relative_residual": 0.,
                                "energy_residual_J_kg": 1e-8}
            }]
        }]
    }


def test_required_scope_units_offline_and_static_table(study):
    html = render_report(study)
    for label in ("0D equilibrium", "not dispersion", "J/kg", "Temperature (K)",
                  "log(1 + ratio)", "<noscript>", 'id="scenario"', "<tbody>",
                  "No measured detector data"):
        assert label in html
    assert "<svg" in html
    assert "https://" not in html and "http://" not in html
    assert 'src="' not in html
    assert html.count('<tr data-index=') == 1


def test_injection_escaped_and_embedded_json_roundtrips(study):
    hostile = '</script><script>alert("XSS")</script><img src=x onerror=alert(1)>'
    study["study_id"] = hostile
    study["assumptions"] = [hostile, "__MODEL__"]
    study["paths"][0]["scenario_id"] = hostile
    document = render_report(study)
    assert hostile not in document
    assert "&lt;script&gt;" in document
    assert "\\u003c/script\\u003e" in document
    assert "<li>__MODEL__</li>" in document
    data = re.search(r'<script id="study-data" type="application/json">(.*?)</script>', document, re.S).group(1)
    assert json.loads(data)["study_id"] == hostile


def test_full_table_keeps_multiple_scenarios(study):
    second = deepcopy(study["paths"][0])
    second["scenario_id"] = "H01-RH0000"
    second["source_id"] = "H01"
    second["ambient"]["relative_humidity"] = 0.
    study["paths"].append(second)
    document = render_report(study)
    assert document.count('<tr data-index=') == 2
    assert "H01-RH0000" in document
    assert 'value="all"' in document


@pytest.mark.parametrize("change", [
    lambda s: s.update(paths=[]),
    lambda s: s["paths"][0].update(points=[]),
    lambda s: s["paths"][0]["points"][0].update(temperature_K=float("nan")),
    lambda s: s["paths"][0]["points"][0]["phase_mass_fractions"].update(gas=.5),
    lambda s: s["paths"][0]["ambient"].update(relative_humidity=2),
    lambda s: s["paths"].append(deepcopy(s["paths"][0])),
    lambda s: s["paths"][0].update(ambient=[]),
    lambda s: s["paths"][0].update(points=[[]]),
    lambda s: s["paths"][0]["points"][0].update(phase_mass_fractions=[]),
    lambda s: s["paths"][0]["points"][0].update(diagnostics=[]),
])
def test_malformed_study_fails_explicitly(study, change):
    change(study)
    with pytest.raises(ValueError):
        render_report(study)


def test_write_preserves_existing_file_and_validates_first(study, tmp_path):
    output = tmp_path/"report.html"
    write_report(study, output)
    original = output.read_bytes()
    with pytest.raises(FileExistsError):
        write_report(study, output)
    assert output.read_bytes() == original
    with pytest.raises(ValueError):
        write_report({"paths":[]}, tmp_path/"invalid.html")
    assert not (tmp_path/"invalid.html").exists()
