#!/usr/bin/env python3
"""Offer a playful seed for a commit message."""

from __future__ import annotations

import random

SEEDS = [
    "polish a rough corner",
    "sweep up stray logs",
    "teach tests to catch up",
    "trim unused branches",
    "nudge performance forward",
    "keep docs honest",
]


def main() -> None:
    print(random.choice(SEEDS))


if __name__ == "__main__":
    main()
