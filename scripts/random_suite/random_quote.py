#!/usr/bin/env python3
"""Print a random motivational quote."""

from __future__ import annotations

import random

QUOTES = [
    "Stay hungry, stay foolish.",
    "Done is better than perfect.",
    "Measure twice, cut once.",
    "The best time to code was yesterday. The second best is now.",
    "Simplicity is the soul of efficiency.",
]


def main() -> None:
    print(random.choice(QUOTES))


if __name__ == "__main__":
    main()
