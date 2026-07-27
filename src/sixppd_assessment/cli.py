"""Command-line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sixppd-assessment",
        description="Analyze public evidence for safer 6PPD alternatives.",
    )
    parser.add_argument("command", choices=["run"])
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root (default: current directory)",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "run":
        outputs = run_pipeline(args.root.resolve())
        for label, path in outputs.items():
            print(f"{label}: {path}")


if __name__ == "__main__":
    main()

