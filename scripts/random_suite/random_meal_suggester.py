#!/usr/bin/env python3
"""Suggest a random meal combination."""

from __future__ import annotations

import argparse
import random

PROTEINS = ["chicken", "tofu", "salmon", "pork", "eggs", "beans"]
SIDES = ["rice", "quinoa", "pasta", "salad", "roasted veggies", "bread"]
FLAVORS = ["garlic herb", "spicy gochujang", "lemon pepper", "soy ginger", "tomato basil"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pick a random meal idea.")
    parser.add_argument("--count", type=int, default=3, help="How many ideas to show.")
    parser.add_argument(
        "--seed",
        type=int,
        help="Optional random seed.",
    )
    return parser


def suggest_meal() -> str:
    protein = random.choice(PROTEINS)
    side = random.choice(SIDES)
    flavor = random.choice(FLAVORS)
    return f"{flavor} {protein} with {side}"


def main() -> None:
    args = build_parser().parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    for _ in range(args.count):
        print(suggest_meal())


if __name__ == "__main__":
    main()
