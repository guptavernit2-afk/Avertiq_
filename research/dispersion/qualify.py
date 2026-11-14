"""Evidence checks for the first external dispersion reference; not a solver."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_json(path: Path) -> dict:
    def bad_constant(value: str):
        raise ValueError(f"Non-finite JSON constant: {value}")
    value = json.loads(path.read_text(encoding="utf-8"), parse_constant=bad_constant)
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    return value


def case_hash(case: dict) -> str:
    """Canonical hash survives Git LF/CRLF conversion."""
    return hashlib.sha256(json.dumps(case, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def positive(value, name: str, allow_zero: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if value < 0 or (value == 0 and not allow_zero):
        raise ValueError(f"{name} is out of range")
    return float(value)


def check_input(case: dict) -> dict:
    if case["chemical"]["CAS"] != "115-07-1" or case["chemical"]["composition_mole_fraction"] != 1:
        raise ValueError("This bounded sheet is for assumed pure propylene only")
    s, w = case["source"], case["weather"]
    rate = positive(s["rate_kg_s"], "airborne rate")
    duration = positive(s["duration_s"], "duration")
    if not 60 <= duration <= 3600:
        raise ValueError("ALOHA direct-source duration must be 1 to 60 minutes")
    if s["phase"] != "gas_only" or s["droplets"] is not False or s["height_m"] != 0:
        raise ValueError("This case excludes aerosol and elevated-source effects")
    positive(s["temperature_K"], "source temperature")
    positive(s["pressure_Pa"], "source pressure")
    positive(w["wind_speed_m_s"], "wind")
    positive(w["measurement_height_m"], "measurement height")
    positive(w["air_temperature_K"], "air temperature")
    humidity = positive(w["relative_humidity_percent"], "humidity", True)
    direction = positive(w["wind_from_degrees_true"], "wind-from", True)
    if humidity > 100 or direction >= 360 or w["stability_class"] != "D":
        raise ValueError("Invalid humidity, direction or unsupported stability in this bounded case")
    return {
        "case_id": case["id"], "case_sha256": case_hash(case),
        "input_checks_passed": True,
        "arithmetic_only": {"airborne_mass_kg": rate * duration, "wind_towards_degrees_true": (direction + 180) % 360},
        "model_calculation_performed": False,
        "dashboard_adapter_enabled": False,
        "open_gates": [key for key, value in case["gates"].items() if value is not True],
        "label": "Assumed inputs checked; arithmetic is not a dispersion prediction",
    }


def compare_reference(reference: dict, observed: dict, evidence_base: Path) -> dict:
    if observed.get("case_id") != reference["id"] or observed.get("case_sha256") != case_hash(reference):
        raise ValueError("Observed run does not identify the exact frozen reference inputs")
    engine = observed.get("engine", {})
    if engine.get("name") != "ALOHA" or engine.get("version") != reference["version"]:
        raise ValueError("Observed engine/version differs from the reference")
    manifest = read_json(ROOT / "engine-manifest.json")
    if engine.get("executable_sha256", "").lower() != manifest["runtime_files"]["ALOHA.EXE"].lower():
        raise ValueError("Observed executable hash differs from the audited installation")
    if observed.get("run_completed") is not True or observed.get("synthetic_test_data") is not False:
        raise ValueError("A completed real software run is required; templates and synthetic tests are not evidence")
    if not observed.get("run_at_utc") or not observed.get("dispersion_method"):
        raise ValueError("Record the actual run time and selected dispersion method")
    raw = observed.get("evidence_files")
    if not isinstance(raw, list) or not raw:
        raise ValueError("Archive raw local run evidence before claiming reproduction")
    files = []
    for item in raw:
        path = (evidence_base / item["path"]).resolve()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest.lower() != item["sha256"].lower():
            raise ValueError(f"Evidence hash mismatch: {path.name}")
        # Avoid redistributing raw summaries that may contain licensed properties.
        files.append({"name": path.name, "sha256": digest})
    tolerances = reference["comparison_tolerances_registered_before_run"]
    comparisons = {}
    for name, expected in reference["expected"].items():
        actual = positive(observed["values"][name], name)
        if name == "release_duration_min":
            allowance = tolerances["duration_absolute_min"]
        elif name == "maximum_average_sustained_rate_lb_min":
            allowance = expected * tolerances["rate_relative"]
        else:
            allowance = max(tolerances["distance_absolute_floor_yd"], expected * tolerances["distance_relative"])
        difference = abs(actual - expected)
        comparisons[name] = {"reference": expected, "observed": actual, "absolute_difference": difference, "registered_tolerance": allowance, "passed": difference <= allowance}
    passed = all(item["passed"] for item in comparisons.values())
    return {
        "case_id": reference["id"], "case_sha256": case_hash(reference),
        "status": "reference_reproduced" if passed else "reference_mismatch",
        "comparison_type": "published_software_reference_reproduction",
        "engine": engine, "run_at_utc": observed["run_at_utc"],
        "dispersion_method": observed["dispersion_method"], "comparisons": comparisons,
        "evidence_files": files, "propylene_qualified": False, "field_validated": False,
        "dashboard_adapter_enabled": False,
        "label": "Software benchmark only; not validation of the propylene incident",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["input-check", "reference-template", "compare-reference"])
    parser.add_argument("--observed", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Choose a fresh output path; evidence is not overwritten")
    reference = read_json(ROOT / "cases/aloha-reference-propane-v1.json")
    if args.command == "input-check":
        result = check_input(read_json(ROOT / "cases/propylene-direct-v1.json"))
    elif args.command == "reference-template":
        result = {"case_id": reference["id"], "case_sha256": case_hash(reference), "engine": {"name": "ALOHA", "version": "5.4.7", "executable_sha256": read_json(ROOT / "engine-manifest.json")["runtime_files"]["ALOHA.EXE"]}, "run_completed": False, "synthetic_test_data": False, "run_at_utc": None, "dispersion_method": None, "evidence_files": [], "values": {key: None for key in reference["expected"]}, "label": "UNRUN TEMPLATE; fill only from an observed software run, never from expected values"}
    else:
        if not args.observed:
            parser.error("--observed is required")
        result = compare_reference(reference, read_json(args.observed), args.observed.parent)
    result["report_created_at_utc"] = datetime.now(timezone.utc).isoformat()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}; {result.get('status', result.get('label'))}")


if __name__ == "__main__":
    main()
