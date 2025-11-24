#!/usr/bin/env python3
"""Pick a random lunch option from simple cuisine ideas."""

from __future__ import annotations

import random

CUISINES = [
    "kimbap and tteokbokki",
    "ramen and gyoza",
    "grilled chicken salad",
    "burrito bowl",
    "pasta with pesto",
    "bibimbap",
    "poké bowl",
    "burger and fries",
]


def main() -> None:
    choice = random.choice(CUISINES)
    print(f"Today's lunch idea: {choice}.")


if __name__ == "__main__":
    main()
