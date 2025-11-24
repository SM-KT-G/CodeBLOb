#!/usr/bin/env python3
"""Print a random short affirmation for a quick mood boost."""

from __future__ import annotations

import random

AFFIRMATIONS = [
    "You are making steady progress.",
    "Small steps still move you forward.",
    "Your effort today matters.",
    "You learn something new every try.",
    "Focus beats speed; you are focused.",
]


def main() -> None:
    print(random.choice(AFFIRMATIONS))


if __name__ == "__main__":
    main()
