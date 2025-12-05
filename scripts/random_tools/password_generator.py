"""Generate strong passwords with repeatable options."""
from __future__ import annotations

import argparse
import secrets
import string
import sys
from typing import List


CHARSETS = {
    "lower": string.ascii_lowercase,
    "upper": string.ascii_uppercase,
    "digits": string.digits,
    "symbols": "!@#$%^&*()-_=+[]{};:,.<>/?",
}


def build_pool(include: List[str]) -> str:
    pool = "".join(CHARSETS[key] for key in include)
    if not pool:
        raise ValueError("No character classes selected.")
    return pool


def ensure_minimums(password: List[str], include: List[str]) -> None:
    for key in include:
        password.append(secrets.choice(CHARSETS[key]))


def generate_password(length: int, include: List[str]) -> str:
    if length < len(include):
        raise ValueError("Length must be at least the number of character classes in use.")
    pool = build_pool(include)
    password_chars: List[str] = []
    ensure_minimums(password_chars, include)
    for _ in range(length - len(password_chars)):
        password_chars.append(secrets.choice(pool))
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--length", type=int, default=16, help="Length of password (default: 16)")
    parser.add_argument(
        "--no-upper",
        action="store_true",
        help="Exclude uppercase letters.",
    )
    parser.add_argument("--no-lower", action="store_true", help="Exclude lowercase letters.")
    parser.add_argument("--no-digits", action="store_true", help="Exclude digits.")
    parser.add_argument("--symbols", action="store_true", help="Include symbol characters.")
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    include = []
    if not args.no_lower:
        include.append("lower")
    if not args.no_upper:
        include.append("upper")
    if not args.no_digits:
        include.append("digits")
    if args.symbols:
        include.append("symbols")

    try:
        password = generate_password(args.length, include)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    print(password)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
