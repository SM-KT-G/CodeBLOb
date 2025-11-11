#!/usr/bin/env python3
"""CLI helper that will showcase various random utilities."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Playground for a handful of random module helpers.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of samples to generate for each example.",
    )
    return parser


def main() -> None:
    """Entry point for the random utilities demo."""
    args = build_parser().parse_args()
    print(f"Random demo placeholder running with count={args.count}")


if __name__ == "__main__":
    main()
