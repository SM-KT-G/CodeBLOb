#!/usr/bin/env python3
"""Generate random passwords with configurable length and amount."""

from __future__ import annotations

import argparse
import random
import string


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate random passwords.")
    parser.add_argument("--length", type=int, default=12, help="Length per password.")
    parser.add_argument("--count", type=int, default=5, help="Number of passwords.")
    parser.add_argument(
        "--digits",
        action="store_true",
        help="Include digits in the password alphabet.",
    )
    parser.add_argument(
        "--symbols",
        action="store_true",
        help="Include punctuation symbols.",
    )
    return parser


def build_alphabet(include_digits: bool, include_symbols: bool) -> str:
    alphabet = string.ascii_letters
    if include_digits:
        alphabet += string.digits
    if include_symbols:
        alphabet += "!@#$%^&*"
    return alphabet


def generate_password(length: int, alphabet: str) -> str:
    return "".join(random.choice(alphabet) for _ in range(length))


def main() -> None:
    args = build_parser().parse_args()
    alphabet = build_alphabet(args.digits, args.symbols)
    for _ in range(args.count):
        print(generate_password(args.length, alphabet))


if __name__ == "__main__":
    main()
