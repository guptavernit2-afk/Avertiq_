"""Offline research report for conditional 0D equilibrium studies.

This module renders supplied results; it does not run a model or validate physics.
No external assets, network calls, or third-party browser libraries are used.
"""
from html import escape
import json
import math
from pathlib import Path

PHASES = ("gas", "water_ice", "water_liquid", "propane_liquid")
COLORS = {"water_ice": "#3866ce", "water_liquid": "#158879", "propane_liquid": "#bb6222"}
RATIO = "added_wet_air_to_source_mass_ratio"


def _number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def _validate(study):
    if not isinstance(study, dict) or not isinstance(study.get("paths"), list) or not study["paths"]:
        raise ValueError("Study must contain a nonempty paths list")
    ids = set()
    for path in study["paths"]:
        if not isinstance(path, dict) or not isinstance(path.get("scenario_id"), str) or not path["scenario_id"]:
            raise ValueError("Each path needs a scenario_id")
        if path["scenario_id"] in ids:
            raise ValueError("Scenario identifiers must be unique")
        ids.add(path["scenario_id"])
        if not isinstance(path.get("source_id"), str):
            raise ValueError("Each path needs a source_id")
        ambient = path.get("ambient", {})
        if not isinstance(ambient, dict):
            raise ValueError("Ambient must be an object")
        rh = _number(ambient.get("relative_humidity"), "relative humidity")
        if not 0 <= rh <= 1:
            raise ValueError("Relative humidity must be in [0, 1]")
        points = path.get("points")
        if not isinstance(points, list) or not points:
            raise ValueError("Every path needs nonempty points")
        ratios = []
        for point in points:
            if not isinstance(point, dict):
                raise ValueError("Every point must be an object")
            ratio = _number(point.get(RATIO), "mixing ratio")
            if ratio < 0:
                raise ValueError("Mixing ratio must be nonnegative")
            ratios.append(ratio)
            _number(point.get("temperature_K"), "temperature")
            if _number(point.get("bulk_density_kg_m3"), "density") <= 0:
                raise ValueError("Density must be positive")
            fractions = point.get("phase_mass_fractions", {})
            if not isinstance(fractions, dict):
                raise ValueError("Phase fractions must be an object")
            values = [_number(fractions.get(k), k) for k in PHASES]
            if min(values) < 0 or max(values) > 1 or abs(sum(values)-1) > 1e-6:
                raise ValueError("Phase mass fractions must be nonnegative and sum to one")
            diagnostics = point.get("diagnostics", {})
            if not isinstance(diagnostics, dict):
                raise ValueError("Diagnostics must be an object")
            residual = _number(diagnostics.get("maximum_component_relative_residual"), "component residual")
            if residual < 0:
                raise ValueError("Maximum component residual must be nonnegative")
            _number(diagnostics.get("energy_residual_J_kg"), "energy residual")
        if len(set(ratios)) != len(ratios):
            raise ValueError("Mixing ratios must be unique within a path")


def _svg(points, *, phase=False, label=""):
    """Pre-render an accessible plot. Ratio uses explicitly labelled log1p spacing."""
    points = sorted(points, key=lambda p: p[RATIO])
    left, top, width, height = 70., 24., 650., 210.
    xmax = max(math.log1p(p[RATIO]) for p in points) or 1.
    if phase:
        series = [(k, [100*p["phase_mass_fractions"][k] for p in points], COLORS[k])
                  for k in PHASES if k != "gas"]
        ymin, ymax = 0., max([v for _, values, _ in series for v in values]+[0.01])*1.1
        ylabel = "Condensed phase / total mass (%)"
    else:
        series = [("temperature", [p["temperature_K"] for p in points], "#9b455f")]
        raw = series[0][1]
        padding = max((max(raw)-min(raw))*.08, 1.)
        ymin, ymax = min(raw)-padding, max(raw)+padding
        ylabel = "Temperature (K)"
    def xy(p, v):
        return left+width*math.log1p(p[RATIO])/xmax, top+height*(ymax-v)/(ymax-ymin)
    out = [f'<svg viewBox="0 0 760 310" role="img" aria-label="{escape(label, quote=True)}">',
           f'<title>{escape(label)}</title>',
           f'<text x="{left}" y="14" class="axis-label">{escape(ylabel)}</text>']
    for i in range(5):
        v = ymin+(ymax-ymin)*i/4
        y = top+height*(1-i/4)
        out += [f'<line x1="{left}" y1="{y:.2f}" x2="{left+width}" y2="{y:.2f}" class="grid"/>',
                f'<text x="{left-9}" y="{y+4:.2f}" text-anchor="end" class="tick">{v:.3g}</text>']
    # Select a readable subset of actual ratios; no interpolation of physical time.
    ticks = points if len(points) <= 6 else [points[i] for i in sorted({0, len(points)//4, len(points)//2, 3*len(points)//4, len(points)-1})]
    for p in ticks:
        x, _ = xy(p, ymin)
        out.append(f'<text x="{x:.2f}" y="{top+height+20}" text-anchor="middle" class="tick">{p[RATIO]:g}</text>')
    for name, values, color in series:
        coords = " ".join(f"{xy(p,v)[0]:.3f},{xy(p,v)[1]:.3f}" for p,v in zip(points,values))
        out.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        for p, v in zip(points, values):
            x,y = xy(p,v)
            out.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="3" fill="{color}"><title>{escape(name)}; ratio {p[RATIO]:g}; value {v:.6g}</title></circle>')
    out.append('<text x="395" y="283" text-anchor="middle" class="axis-label">Added wet-air / source mass ratio (log(1 + ratio) spacing)</text>')
    out.append('</svg>')
    if phase:
        out.append('<p class="legend">'+" ".join(
            f'<span><i style="background:{color}"></i>{escape(name.replace("_"," "))}</span>'
            for name,_,color in series)+'</p>')
    return "".join(out)


def render_report(study):
    """Render an existing valid study as self-contained HTML; no model is run."""
    _validate(study)
    paths = study["paths"]
    points = [p for path in paths for p in path["points"]]
    maximum_energy = max(abs(p["diagnostics"]["energy_residual_J_kg"]) for p in points)
    maximum_component = max(p["diagnostics"]["maximum_component_relative_residual"] for p in points)
    options, panels, rows = [], [], []
    for index, path in enumerate(paths):
        label = f'{path["source_id"]} / downstream RH {100*path["ambient"]["relative_humidity"]:g}%'
        options.append(f'<option value="{index}">{escape(label)} - {escape(path["scenario_id"])}</option>')
        panels.append(f'<section class="scenario" data-index="{index}"><h2>{escape(label)}</h2>'
                      '<p class="muted">Source assumptions stay fixed when downstream humidity changes. Lines connect sampled equilibrium states; they do not describe travel or mixing rates.</p>'
                      '<div class="plots"><figure><figcaption>Thermal response</figcaption>'
                      +_svg(path["points"],label=label+" temperature")
                      +'</figure><figure><figcaption>Water and propane condensates</figcaption>'
                      +_svg(path["points"],phase=True,label=label+" condensed phase mass fractions")
                      +'</figure></div></section>')
        for p in path["points"]:
            f = p["phase_mass_fractions"]
            rows.append(f'<tr data-index="{index}"><th scope="row">{escape(path["scenario_id"])}</th>'
                        f'<td>{p[RATIO]:g}</td><td>{p["temperature_K"]:.3f}</td>'
                        +''.join(f'<td>{100*f[k]:.6f}</td>' for k in PHASES)
                        +f'<td>{p["bulk_density_kg_m3"]:.6f}</td>'
                        f'<td>{p["diagnostics"]["energy_residual_J_kg"]:.3g}</td></tr>')
    assumptions = study.get("assumptions", [])
    if not isinstance(assumptions, list):
        raise ValueError("assumptions must be a list")
    assumptions_html = "".join(f'<li>{escape(str(a))}</li>' for a in assumptions)
    # Escaping "<" also prevents any embedded </script> from terminating this data block.
    payload = json.dumps(study, ensure_ascii=True, allow_nan=False).replace("&", r"\u0026").replace("<", r"\u003c").replace(">", r"\u003e")
    template = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Avertiq - equilibrium research report</title>
<style>
:root{color-scheme:light;--ink:#172c35;--muted:#52636b;--line:#dce5e8;--paper:#fff;--back:#f1f5f6}
*{box-sizing:border-box}body{margin:0;background:var(--back);color:var(--ink);font:16px/1.55 system-ui,sans-serif}
main{max-width:1440px;margin:auto;padding:40px 32px}header{border-bottom:1px solid var(--line);padding-bottom:22px}
.eyebrow{font-size:12px;font-weight:750;letter-spacing:.15em;color:#327365}h1{font-size:clamp(27px,4vw,42px);line-height:1.15;margin:10px 0}h2{font-size:22px}
.scope{background:#fff5db;border-left:4px solid #ba8123;padding:14px 18px;margin:22px 0}.scope strong{display:block}
.muted{color:var(--muted)}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}
.stat,figure,.selector,details{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:18px}
.stat b{font-size:25px;display:block}.stat span{font-size:13px;color:var(--muted)}
.selector{display:flex;align-items:center;gap:15px;flex-wrap:wrap}select{font:inherit;padding:9px;max-width:100%;border:1px solid #9cadaf;border-radius:5px;background:white}
.plots{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0;min-width:0}figcaption{font-weight:700}svg{display:block;width:100%;height:auto;margin-top:14px}
.grid{stroke:#e3e9eb;stroke-width:1}.tick{font-size:12px;fill:#52636b}.axis-label{font-size:12px;fill:#31464f}
.legend{font-size:12px;display:flex;gap:15px;flex-wrap:wrap;margin:0}.legend span{white-space:nowrap}.legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px}
.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:10px;background:#fff}table{border-collapse:collapse;width:100%;font-size:13px;font-variant-numeric:tabular-nums}caption{text-align:left;padding:14px;color:var(--muted)}
th,td{padding:10px 12px;border-top:1px solid var(--line);text-align:right;white-space:nowrap}th:first-child{text-align:left}thead th{background:#edf3f4}tbody tr:hover{background:#f6faf9}
details{margin:22px 0}summary{font-weight:700;cursor:pointer}footer{font-size:13px;color:var(--muted);margin-top:25px}code{overflow-wrap:anywhere}button{font:inherit}
[hidden]{display:none!important}@media(max-width:850px){main{padding:24px 14px}.plots{grid-template-columns:1fr}.stats{grid-template-columns:1fr 1fr}}
</style></head><body><main>
<header><div class="eyebrow">AVERTIQ / RESEARCH WORKBENCH</div><h1>Cold-source equilibrium study</h1>
<p class="muted">__STUDY_ID__ - locally generated, fully offline results</p></header>
<div class="scope"><strong>0D equilibrium, not dispersion or a validated safety map.</strong>Conditional calculations only. No prediction of cloud position, distance, time, terrain flow or operational safety. Numerical conservation does not establish experimental accuracy.</div>
<div class="stats"><div class="stat"><b>__PATHS__</b><span>declared source / humidity paths</span></div><div class="stat"><b>__POINTS__</b><span>sampled equilibrium states</span></div><div class="stat"><b>__ENERGY__</b><span>max |energy residual| (J/kg)</span></div><div class="stat"><b>__COMPONENT__</b><span>max relative component residual</span></div></div>
<div class="selector"><label for="scenario"><strong>Inspect a scenario</strong></label><select id="scenario"><option value="all">All scenarios</option>__OPTIONS__</select></div>
<noscript><p>JavaScript is disabled. All plots and the complete table remain available below.</p></noscript>
__PANELS__
<h2>Sampled states</h2><p class="muted">Phase columns are percentages of total mass, including gas. Condensate plots use the same total-mass denominator. Ratio is added wet-air mass / original source mass, never distance or elapsed time.</p>
<div class="table-wrap"><table><caption id="table-caption">All __POINTS__ states. No measured detector data are included.</caption><thead><tr><th scope="col">Scenario</th><th scope="col">Mass ratio</th><th scope="col">T (K)</th><th scope="col">Gas (%)</th><th scope="col">Ice (%)</th><th scope="col">Water liquid (%)</th><th scope="col">Propane liquid (%)</th><th scope="col">Density (kg/m3)</th><th scope="col">Energy residual (J/kg)</th></tr></thead><tbody>__ROWS__</tbody></table></div>
<details open><summary>Assumptions and interpretation</summary><p>__ENERGY_POLICY__</p><ul>__ASSUMPTIONS__</ul><p>Transition brackets describe sampled equilibrium changes, not exact physical thresholds. Inspect the embedded study record for bracket endpoints, component ledgers and provenance.</p></details>
<details><summary>Model and provenance</summary><p>__MODEL__</p><pre style="white-space:pre-wrap;overflow-wrap:anywhere">__PROVENANCE__</pre></details>
<footer>Generated from supplied research results. This renderer does not run a model. This file loads no external assets or services.</footer>
</main><script id="study-data" type="application/json">__JSON__</script>
<script>
"use strict";
const chooser = document.getElementById("scenario");
function filterScenario() {
  const choice = chooser.value;
  document.querySelectorAll("[data-index]").forEach(function(node) {
    node.hidden = choice !== "all" && node.dataset.index !== choice;
  });
  const count = document.querySelectorAll("tbody tr:not([hidden])").length;
  document.getElementById("table-caption").textContent = count + " displayed states. No measured detector data are included.";
}
chooser.addEventListener("change", filterScenario);
if (chooser.options.length > 1) { chooser.value = "0"; filterScenario(); }
</script></body></html>"""
    substitutions = {
        "__STUDY_ID__": escape(str(study.get("study_id", "Conditional study"))),
        "__PATHS__": str(len(paths)), "__POINTS__": str(len(points)),
        "__ENERGY__": f"{maximum_energy:.3g}", "__COMPONENT__": f"{maximum_component:.3g}",
        "__OPTIONS__": "".join(options), "__PANELS__": "".join(panels), "__ROWS__": "".join(rows),
        "__ASSUMPTIONS__": assumptions_html,
        "__ENERGY_POLICY__": escape(str(study.get("energy_policy", "Thermal enthalpy only; no momentum or kinetic-energy conversion."))),
        "__MODEL__": escape(str(study.get("model", "Model not specified"))),
        "__PROVENANCE__": escape(json.dumps(study.get("provenance", {}), indent=2, ensure_ascii=True)),
        "__JSON__": payload,
    }
    # One pass prevents user text resembling a placeholder from being substituted.
    import re
    return re.sub("|".join(map(re.escape, substitutions)), lambda m: substitutions[m.group()], template)


def write_report(study, output):
    """Write a report atomically with respect to existing files (exclusive create)."""
    output = Path(output)
    document = render_report(study)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(document)
    return output
