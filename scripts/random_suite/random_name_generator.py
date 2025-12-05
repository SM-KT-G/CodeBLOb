#!/usr/bin/env python3
"""Generate whimsical random names by combining syllables."""

from __future__ import annotations

import argparse
import random

PREFIXES = ["ka", "lo", "mi", "za", "ra", "ta", "shi", "el", "or", "ve"]
SUFFIXES = ["na", "ra", "len", "rin", "tor", "sha", "bel", "dor", "mon", "xis"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate random names.")
    parser.add_argument("--count", type=int, default=10, help="How many names.")
    parser.add_argument(
        "--seed",
        type=int,
        help="Optional seed for reproducibility.",
    )
    return parser


def generate_name() -> str:
    return random.choice(PREFIXES).capitalize() + random.choice(SUFFIXES)


def main() -> None:
    args = build_parser().parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    for _ in range(args.count):
        print(generate_name())


if __name__ == "__main__":
    main()
