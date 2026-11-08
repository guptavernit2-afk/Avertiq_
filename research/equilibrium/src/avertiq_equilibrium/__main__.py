"""CLI for verification and conditional source cases. No app or CFD."""
import argparse
import json
from pathlib import Path

from .verification import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "cases", "mixing"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; select a new path to preserve prior runs")
    try:
        verification = verify()
        if args.command in ("cases", "mixing"):
            if not verification["passed"]:
                raise RuntimeError("Property/numerical verification failed; calculation refused")
            if args.command == "cases":
                from .cases import run_cases
                result = run_cases()
            else:
                from .mixing import run_mixing
                result = run_mixing()
            result["verification_passed"] = True
        else:
            result = verification
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(result, indent=2, allow_nan=False)+"\n")
        print(f"{args.command}: wrote {args.output}")
        return 0 if verification["passed"] else 1
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(1, f"Calculation failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
