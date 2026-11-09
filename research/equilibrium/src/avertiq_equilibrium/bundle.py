"""Reproducible standalone research bundle; no app, CFD or deployment."""
import hashlib
import json
from pathlib import Path
import tempfile

from .verification import verify


def _write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+"\n", encoding="utf-8", newline="\n")


def create_bundle(output, **study_options):
    """Verify, calculate, audit, and publish a fresh directory of research artifacts.

    Build in a temporary sibling so failures do not leave a partial final bundle.
    Existing destinations are refused, including empty directories and symlinks.
    """
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Output already exists: {output}")
    if study_options.get("pressure_Pa", 102500.) != 102500.:
        raise ValueError("Bundle source exports use 102500 Pa; use study for custom pressures")
    verification = verify()
    if not verification["passed"]:
        raise RuntimeError("Property/numerical verification failed; bundle refused")

    from .study import run_study
    from .cases import run_cases
    from .handoff import export_handoff, validate_handoff
    from .report import render_report

    study = run_study(**study_options)
    study["verification_passed"] = True
    cases = run_cases()
    exports = []
    for case in cases["cases"]:
        if case["case_id"] == "H04":
            continue  # Nonadiabatic TP audit is not an adiabatic PH boundary.
        record = export_handoff(case, cases["molar_masses_kg_mol"], provenance=cases["provenance"])
        audit = validate_handoff(record)
        if not audit["passed"]:
            raise RuntimeError(f"Source handoff failed: {case['case_id']}")
        exports.append({"source": record, "audit": audit})
    handoffs = {
        "schema_version": 1,
        "scope": "Conditional 0D source contracts; not executable CFD boundaries.",
        "cases": exports,
        "excluded": {"H04": "Nonadiabatic imposed-temperature audit; not a PH source."},
        "provenance": cases["provenance"],
    }
    html = render_report(study)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".avertiq-bundle-", dir=output.parent) as directory:
        staging = Path(directory)
        for name, value in (("verification.json", verification),
                            ("study.json", study), ("handoffs.json", handoffs)):
            _write_json(staging/name, value)
        (staging/"report.html").write_text(html, encoding="utf-8", newline="\n")
        manifest = {
            "schema_version": 1,
            "kind": "Avertiq standalone equilibrium research bundle",
            "scope": "0D research only; no CFD, spatial plume, app or safety validation.",
            "verification_passed": True,
            "source_contracts_passed": len(exports),
            "study_options_requested": study_options,
            "hash_basis": "SHA-256 of exact artifact bytes; manifest excludes itself.",
            "files": {p.name: {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                              "bytes": p.stat().st_size}
                      for p in sorted(staging.iterdir())},
            "provenance": study["provenance"],
        }
        _write_json(staging/"manifest.json", manifest)
        # Recheck after calculation; never reuse a pre-existing run directory.
        if output.exists() or output.is_symlink():
            raise FileExistsError(f"Output already exists: {output}")
        staging.rename(output)
    return manifest
