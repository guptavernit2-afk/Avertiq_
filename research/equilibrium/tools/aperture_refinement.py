"""Vertical refinement around the EEC550 H00 source aperture."""
import argparse
import json
from pathlib import Path

from avertiq_equilibrium.atmospheric import run_atmospheric
from avertiq_equilibrium.atmospheric_checks import audit_atmospheric_result
from avertiq_equilibrium.cases import provenance
from avertiq_equilibrium.eec550_case import build_eec550_case
from avertiq_equilibrium.properties import Properties
from avertiq_equilibrium.verification import verify


def run_aperture_refinement():
    if not verify()["passed"]:
        raise RuntimeError("Thermodynamic property checks failed")
    props = Properties()
    case = build_eec550_case()
    case["domain"]["height_m"] = 1.6
    duration = 0.001
    steps = 25
    runs = []
    for nz in (4, 8, 16):
        result = run_atmospheric(props, nx=4, nz=nz, duration_s=duration, cfl=.2,
                                 case_config=case, max_timestep_s=duration/steps)
        audit_atmospheric_result(result)
        if result["diagnostics"]["steps"] != steps or result["diagnostics"]["timestep_retries"]:
            raise RuntimeError("Vertical refinement requires the same accepted timesteps")
        runs.append(result)
    return {
        "study": "H00 source-height refinement",
        "matched_duration_s": duration,
        "fixed_timestep_s": duration/steps,
        "source_height_m": case["source"]["height_m"],
        "scope": "Vertical refinement in a 16 m by 1.6 m inlet-region domain. Horizontal spacing is 4 m. The top boundary differs from the larger-domain study.",
        "grid_runs": runs,
        "case": case,
        "provenance": provenance(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    target = parser.parse_args().output
    if target.exists():
        parser.error("Choose a fresh output path")
    report = run_aperture_refinement()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(f"Wrote {target}")
