#!/usr/bin/env python3
"""Print a random gratitude prompt."""

from __future__ import annotations

import random

PROMPTS = [
    "Name one person you appreciate today.",
    "Recall a small moment that made you smile.",
    "What's one tool that saved you time?",
    "Pick a habit you're proud of keeping.",
    "What recent lesson are you grateful for?",
]


def main() -> None:
    print(random.choice(PROMPTS))


if __name__ == "__main__":
    main()
