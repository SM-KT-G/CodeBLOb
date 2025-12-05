#!/usr/bin/env python3
"""Stream random floats until a threshold is met."""

from __future__ import annotations

import argparse
import random
from itertools import count


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Stream random floats until the cumulative sum exceeds a threshold.",
    )
    parser.add_argument("--threshold", type=float, default=10.0, help="Target sum.")
    parser.add_argument("--seed", type=int, help="Optional RNG seed.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    total = 0.0
    for idx in count(start=1):
        value = random.random()
        total += value
        print(f"{idx:02d}: {value:.4f} (total={total:.4f})")
        if total >= args.threshold:
            break


if __name__ == "__main__":
    main()
