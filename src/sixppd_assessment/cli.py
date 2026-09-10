"""Command-line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import run_pipeline
from .reporting import verify_manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sixppd-assessment",
        description="Analyze public evidence for safer 6PPD alternatives.",
    )
    parser.add_argument("command", choices=["run", "verify"])
    parser.add_argument(
        "--permutations",
        type=int,
        default=19,
        help="Within-run dose permutation diagnostic repetitions (default: 19)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root (default: current directory)",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.permutations < 0:
        raise SystemExit("--permutations must be nonnegative")
    if args.command == "run":
        outputs = run_pipeline(args.root.resolve(), permutations=args.permutations)
        for label, path in outputs.items():
            print(f"{label}: {path}")
    else:
        count = verify_manifest(args.root.resolve())
        print(f"Verified {count} recorded input, code and output hashes")


if __name__ == "__main__":
    main()
