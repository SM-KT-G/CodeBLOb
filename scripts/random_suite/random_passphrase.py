#!/usr/bin/env python3
"""Generate simple passphrases using random words."""

from __future__ import annotations

import argparse
import random

WORDS = [
    "river",
    "planet",
    "ocean",
    "panda",
    "code",
    "forest",
    "ember",
    "matrix",
    "jelly",
    "stone",
    "cloud",
    "pixel",
    "rocket",
    "coffee",
    "breeze",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate passphrases.")
    parser.add_argument("--count", type=int, default=5, help="How many passphrases.")
    parser.add_argument(
        "--words",
        type=int,
        default=4,
        help="Words per passphrase.",
    )
    parser.add_argument(
        "--separator",
        type=str,
        default="-",
        help="Separator between words.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Optional seed for reproducibility.",
    )
    return parser


def generate_passphrase(words: int, separator: str) -> str:
    return separator.join(random.choice(WORDS) for _ in range(words))


def main() -> None:
    args = build_parser().parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    for _ in range(args.count):
        print(generate_passphrase(args.words, args.separator))


if __name__ == "__main__":
    main()
