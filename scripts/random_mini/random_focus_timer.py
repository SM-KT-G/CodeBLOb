#!/usr/bin/env python3
"""Suggest a random focus timer and short break combo."""

from __future__ import annotations

import random

FOCUS_WINDOWS = [20, 25, 30, 35, 40, 45]
BREAK_OPTIONS = [5, 7, 8, 10]


def main() -> None:
    focus = random.choice(FOCUS_WINDOWS)
    rest = random.choice(BREAK_OPTIONS)
    print(f"Focus for {focus} minutes, then break for {rest} minutes.")


if __name__ == "__main__":
    main()
