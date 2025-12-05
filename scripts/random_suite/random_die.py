#!/usr/bin/env python3
"""Roll an N-sided die several times."""

from __future__ import annotations

import argparse
import random
from collections import Counter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Roll a die and show stats.")
    parser.add_argument("--sides", type=int, default=6, help="Number of die sides.")
    parser.add_argument("--rolls", type=int, default=12, help="Number of rolls.")
    parser.add_argument("--seed", type=int, help="Optional RNG seed.")
    return parser


def roll_die(sides: int, rolls: int) -> Counter[int]:
    results = [random.randint(1, sides) for _ in range(rolls)]
    return Counter(results)


def main() -> None:
    args = build_parser().parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    stats = roll_die(args.sides, args.rolls)
    print(f"Rolled a {args.sides}-sided die {args.rolls} times:")
    for face in range(1, args.sides + 1):
        count = stats.get(face, 0)
        print(f"{face}: {count}")


if __name__ == "__main__":
    main()
