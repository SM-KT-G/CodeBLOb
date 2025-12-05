#!/usr/bin/env python3
"""CLI helper that will showcase various random utilities."""

from __future__ import annotations

import argparse
import random
import statistics
import string


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Playground for a handful of random module helpers.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of samples to generate for each example.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Optional random seed for reproducible results.",
    )
    return parser


def main() -> None:
    """Entry point for the random utilities demo."""
    args = build_parser().parse_args()
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Seeding RNG with {args.seed}")
    print(f"Random demo running with count={args.count}")
    ints = random_integers(args.count, low=1, high=100)
    print_section("Random integers", ", ".join(str(num) for num in ints))
    print_section("Integer stats", summarize_numbers(ints))
    picks = random_choices(
        options=["🍎 apple", "🍌 banana", "🍇 grape", "🥝 kiwi", "🍓 strawberry"],
        count=args.count,
    )
    print_section("Random fruit picks", "\n".join(picks))
    passwords = [generate_password(length=12) for _ in range(min(args.count, 3))]
    print_section("Sample passwords", "\n".join(passwords))


def random_integers(count: int, low: int = 0, high: int = 10) -> list[int]:
    """Return a list of pseudorandom integers inclusive of bounds."""
    return [random.randint(low, high) for _ in range(count)]


def print_section(title: str, content: str) -> None:
    """Nicely format a section of CLI output."""
    print(f"\n== {title} ==")
    print(content)


def random_choices(options: list[str], count: int) -> list[str]:
    """Return `count` random picks (with replacement) from the options."""
    return [random.choice(options) for _ in range(count)]


def generate_password(length: int = 12) -> str:
    """Generate a pseudo-random password with mixed character classes."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(random.choice(alphabet) for _ in range(length))


def summarize_numbers(values: list[int]) -> str:
    """Return mean and standard deviation summary for the collection."""
    mean = statistics.fmean(values)
    stdev = statistics.stdev(values) if len(values) > 1 else 0.0
    return f"mean={mean:.2f}, stdev={stdev:.2f}, min={min(values)}, max={max(values)}"


if __name__ == "__main__":
    main()
