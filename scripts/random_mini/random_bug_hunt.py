#!/usr/bin/env python3
"""Give a random bug hunt challenge."""

from __future__ import annotations

import random

CHALLENGES = [
    "Find and remove one unused dependency.",
    "Fix a flaky test and document it.",
    "Improve a confusing error message.",
    "Add logging around a risky path.",
    "Find a slow query and note a fix.",
    "Reduce one linter warning to zero.",
]


def main() -> None:
    print(random.choice(CHALLENGES))


if __name__ == "__main__":
    main()
