#!/usr/bin/env python3
"""Flip a virtual coin multiple times and report the stats."""

from __future__ import annotations

import argparse
import random
from collections import Counter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Flip a coin N times.")
    parser.add_argument("--flips", type=int, default=10, help="Number of flips.")
    parser.add_argument(
        "--seed",
        type=int,
        help="Optional seed for reproducible results.",
    )
    return parser


def flip_coin(flips: int) -> Counter[str]:
    outcomes = [random.choice(["Heads", "Tails"]) for _ in range(flips)]
    return Counter(outcomes)


def main() -> None:
    args = build_parser().parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    stats = flip_coin(args.flips)
    print(f"Flipped the coin {args.flips} times:")
    for face in ("Heads", "Tails"):
        print(f"{face}: {stats.get(face, 0)}")


if __name__ == "__main__":
    main()
