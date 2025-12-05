#!/usr/bin/env python3
"""Shuffle tasks into a random order with timestamps."""

from __future__ import annotations

import argparse
import datetime as dt
import random


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Randomize a daily task plan.")
    parser.add_argument("--tasks", nargs="+", required=True, help="Tasks to schedule.")
    parser.add_argument(
        "--start",
        type=str,
        default="09:00",
        help="Start time in HH:MM (24h).",
    )
    parser.add_argument(
        "--slot-minutes",
        type=int,
        default=30,
        help="Minutes allocated per slot.",
    )
    parser.add_argument("--seed", type=int, help="Optional RNG seed.")
    return parser


def parse_time(value: str) -> dt.datetime:
    hour, minute = map(int, value.split(":"))
    today = dt.date.today()
    return dt.datetime(today.year, today.month, today.day, hour, minute)


def main() -> None:
    args = build_parser().parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    tasks = args.tasks[:]
    random.shuffle(tasks)
    current = parse_time(args.start)
    delta = dt.timedelta(minutes=args.slot_minutes)
    for task in tasks:
        print(f"{current.strftime('%H:%M')} - {task}")
        current += delta


if __name__ == "__main__":
    main()
