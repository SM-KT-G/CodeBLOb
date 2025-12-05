#!/usr/bin/env python3
"""Generate a quick three-item meeting agenda."""

from __future__ import annotations

import random

TOPICS = [
    "Status check",
    "Blockers",
    "Risks",
    "Demos",
    "Decisions needed",
    "Metrics review",
    "Action items",
    "Next steps",
]


def main() -> None:
    picks = random.sample(TOPICS, 3)
    print(" - ".join(picks))


if __name__ == "__main__":
    main()
