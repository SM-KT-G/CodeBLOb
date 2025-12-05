#!/usr/bin/env python3
"""Generate a playful username from adjectives, nouns, and numbers."""

from __future__ import annotations

import random

ADJECTIVES = [
    "swift",
    "bright",
    "quiet",
    "lucky",
    "bold",
    "cozy",
    "brave",
    "sunny",
]

NOUNS = [
    "otter",
    "falcon",
    "maple",
    "nebula",
    "panda",
    "sparrow",
    "ember",
    "pixel",
]


def main() -> None:
    handle = f"{random.choice(ADJECTIVES)}_{random.choice(NOUNS)}{random.randint(10, 99)}"
    print(handle)


if __name__ == "__main__":
    main()
