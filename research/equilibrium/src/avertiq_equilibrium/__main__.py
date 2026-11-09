"""CLI for standalone equilibrium research. No app or CFD."""
import argparse
import json
from pathlib import Path

from .verification import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("verify", "cases", "mixing", "study", "bundle"):
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
            if args.command == "cases":
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
