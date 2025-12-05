#!/usr/bin/env python3
"""Simulate a 2D random walk."""

from __future__ import annotations

import argparse
import random

MOVES = {
    "N": (0, 1),
    "S": (0, -1),
    "E": (1, 0),
    "W": (-1, 0),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a 2D random walk.")
    parser.add_argument("--steps", type=int, default=20, help="Number of steps.")
    parser.add_argument("--seed", type=int, help="Optional RNG seed.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    x = y = 0
    print(f"Start at ({x}, {y})")
    for step in range(1, args.steps + 1):
        direction = random.choice(list(MOVES.keys()))
        dx, dy = MOVES[direction]
        x += dx
        y += dy
        print(f"{step:02d}. {direction} -> ({x}, {y})")
    print(f"End position: ({x}, {y})")


if __name__ == "__main__":
    main()
