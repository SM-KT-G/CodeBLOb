#!/usr/bin/env python3
"""Emit random colors in hex and RGB forms."""

from __future__ import annotations

import argparse
import random


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate random colors.")
    parser.add_argument("--count", type=int, default=5, help="How many colors.")
    return parser


def random_color() -> tuple[int, int, int]:
    return tuple(random.randint(0, 255) for _ in range(3))


def fmt_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def main() -> None:
    args = build_parser().parse_args()
    for _ in range(args.count):
        rgb = random_color()
        print(f"{fmt_hex(rgb)} -> RGB{rgb}")


if __name__ == "__main__":
    main()
