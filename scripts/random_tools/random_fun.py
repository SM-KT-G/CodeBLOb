#!/usr/bin/env python3
"""CLI helper that will showcase various random utilities."""

from __future__ import annotations

import argparse
import random


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
    print(f"Random demo running with count={args.count}")
    ints = random_integers(args.count, low=1, high=100)
    print_section("Random integers", ", ".join(str(num) for num in ints))


def random_integers(count: int, low: int = 0, high: int = 10) -> list[int]:
    """Return a list of pseudorandom integers inclusive of bounds."""
    return [random.randint(low, high) for _ in range(count)]


def print_section(title: str, content: str) -> None:
    """Nicely format a section of CLI output."""
    print(f"\n== {title} ==")
    print(content)


if __name__ == "__main__":
    main()
