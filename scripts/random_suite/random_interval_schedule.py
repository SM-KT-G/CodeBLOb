#!/usr/bin/env python3
"""Create a sequence of random time intervals within a range."""

from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate random reminder times.")
    parser.add_argument("--count", type=int, default=5, help="Number of reminders.")
    parser.add_argument(
        "--min-minutes",
        type=int,
        default=10,
        help="Minimum minutes between reminders.",
    )
    parser.add_argument(
        "--max-minutes",
        type=int,
        default=45,
        help="Maximum minutes between reminders.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Optional seed for reproducibility.",
    )
    return parser


def build_intervals(count: int, min_minutes: int, max_minutes: int) -> list[timedelta]:
    if min_minutes > max_minutes:
        raise ValueError("min-minutes cannot exceed max-minutes")
    deltas = []
    for _ in range(count):
        minutes = random.randint(min_minutes, max_minutes)
        deltas.append(timedelta(minutes=minutes))
    return deltas


def main() -> None:
    args = build_parser().parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    deltas = build_intervals(args.count, args.min_minutes, args.max_minutes)
    now = datetime.now()
    print(f"Start time: {now.strftime('%H:%M')}")
    current = now
    for idx, delta in enumerate(deltas, start=1):
        current += delta
        print(f"{idx:02d}. +{delta} -> {current.strftime('%H:%M')}")


if __name__ == "__main__":
    main()
