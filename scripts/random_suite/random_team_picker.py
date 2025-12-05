#!/usr/bin/env python3
"""Split participants into random teams."""

from __future__ import annotations

import argparse
import random
from math import ceil


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Assign people to random teams.")
    parser.add_argument(
        "--people",
        nargs="+",
        required=True,
        help="List of names to distribute.",
    )
    parser.add_argument("--teams", type=int, default=2, help="Number of teams.")
    parser.add_argument("--seed", type=int, help="Optional RNG seed.")
    return parser


def chunk(items: list[str], size: int) -> list[list[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def main() -> None:
    args = build_parser().parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    shuffled = args.people[:]
    random.shuffle(shuffled)
    per_team = ceil(len(shuffled) / args.teams)
    grouped = chunk(shuffled, per_team)
    for idx, team in enumerate(grouped, start=1):
        print(f"Team {idx}: {', '.join(team)}")


if __name__ == "__main__":
    main()
