#!/usr/bin/env python3
"""Generate a quick study prompt with a topic and time block."""

from __future__ import annotations

import random

TOPICS = [
    "data structures",
    "networking basics",
    "database indexing",
    "JavaScript fundamentals",
    "Python standard library",
    "system design sketching",
    "shell scripting",
    "algorithms practice",
]

TIME_BLOCKS = [15, 20, 25, 30, 35, 40]


def main() -> None:
    topic = random.choice(TOPICS)
    minutes = random.choice(TIME_BLOCKS)
    print(f"Focus on {topic} for {minutes} minutes.")


if __name__ == "__main__":
    main()
