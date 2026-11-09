"""CLI for standalone equilibrium research. No product app; includes bounded transport and buoyant-flow prototypes."""
import argparse
import json
from pathlib import Path

from .verification import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("verify", "cases", "mixing", "study", "bundle", "transport", "flow", "flow-checks", "thermal-flow", "thermal-checks", "thermal2d", "thermal2d-checks", "atmospheric", "atmospheric-checks", "atmospheric-refinement"):
        child = commands.add_parser(command)
        child.add_argument("--output", type=Path, required=True,
                           help="Fresh output directory for bundle; fresh JSON path otherwise")
        if command in ("study", "bundle"):
            child.add_argument("--sources", nargs="+", choices=("H00", "H01", "H02", "H03"))
            child.add_argument("--relative-humidities", nargs="+", type=float)
            child.add_argument("--ratios", nargs="+", type=float)
            child.add_argument("--ambient-temperature", type=float)
            child.add_argument("--pressure", type=float)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error("Output already exists; select a new path to preserve prior runs")
    options = {}
    for argument, key in (("sources", "source_ids"),
                          ("relative_humidities", "relative_humidities"),
                          ("ratios", "ratios"),
                          ("ambient_temperature", "ambient_temperature_K"),
                          ("pressure", "pressure_Pa")):
        value = getattr(args, argument, None)
        if value is not None:
            options[key] = value
    try:
        if args.command == "bundle":
            from .bundle import create_bundle
            create_bundle(args.output, **options)
        else:
            verification = verify()
            if args.command != "verify" and not verification["passed"]:
                raise RuntimeError("Property/numerical verification failed; calculation refused")
            if args.command == "atmospheric":
                from .atmospheric import run_atmospheric
                result = run_atmospheric()
            elif args.command == "atmospheric-checks":
                from .atmospheric_checks import run_atmospheric_checks
                result = run_atmospheric_checks()
                if not result["passed"]:
                    raise RuntimeError("Atmospheric boundary checks failed")
            elif args.command == "atmospheric-refinement":
                from .atmospheric_checks import run_refinement
                result = run_refinement()
            elif args.command == "thermal2d":
                from .thermal2d import run_thermal2d
                result = run_thermal2d()
            elif args.command == "thermal2d-checks":
                from .thermal2d_checks import run_thermal2d_checks
                result = run_thermal2d_checks()
                if not result["passed"]:
                    raise RuntimeError("2D thermal-buoyancy checks failed")
            elif args.command == "thermal-flow":
                from .thermal_flow import run_thermal_flow
                result = run_thermal_flow()
            elif args.command == "thermal-checks":
                from .thermal_checks import run_thermal_checks
                result = run_thermal_checks()
                if not result["passed"]:
                    raise RuntimeError("Thermal flow checks failed")
            elif args.command == "flow":
                from .flow import run_flow
                result = run_flow()
            elif args.command == "flow-checks":
                from .flow_checks import run_flow_checks
                result = run_flow_checks()
                if not result["passed"]:
                    raise RuntimeError("Flow verification checks failed")
            elif args.command == "transport":
                from .transport import run_transport
                result = run_transport()
            elif args.command == "cases":
                from .cases import run_cases
                result = run_cases()
            elif args.command == "mixing":
                from .mixing import run_mixing
                result = run_mixing()
            elif args.command == "study":
                from .study import run_study
                result = run_study(**options)
            else:
                result = verification
            if args.command != "verify":
                result["verification_passed"] = True
            serialized = json.dumps(result, indent=2, allow_nan=False)+"\n"
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(serialized)
            if not verification["passed"]:
                print(f"{args.command}: wrote failing verification {args.output}")
                return 1
        print(f"{args.command}: wrote {args.output}")
        return 0
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(1, f"Calculation failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
