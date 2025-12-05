#!/usr/bin/env python3
"""Generate lottery-style random number picks."""

from __future__ import annotations

import argparse
import random


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate lottery number sets.")
    parser.add_argument("--draws", type=int, default=3, help="How many tickets to draw.")
    parser.add_argument("--count", type=int, default=6, help="Numbers per ticket.")
    parser.add_argument(
        "--max-number",
        type=int,
        default=45,
        help="Highest number in the pool (inclusive).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Optional seed for reproducible tickets.",
    )
    return parser


def draw_ticket(count: int, max_number: int) -> list[int]:
    """Draw a unique, sorted set of numbers."""
    if count > max_number:
        raise ValueError("count cannot exceed max_number")
    numbers = random.sample(range(1, max_number + 1), count)
    return sorted(numbers)


def main() -> None:
    args = build_parser().parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    for idx in range(1, args.draws + 1):
        ticket = draw_ticket(args.count, args.max_number)
        print(f"Ticket {idx}: {' '.join(map(str, ticket))}")


if __name__ == "__main__":
    main()
