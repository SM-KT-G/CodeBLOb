#!/usr/bin/env python3
"""Share a random book recommendation with a short note."""

from __future__ import annotations

import random

BOOKS = [
    ("Deep Work", "Great for rebuilding focus."),
    ("The Pragmatic Programmer", "Timeless software craftsmanship reminders."),
    ("Atomic Habits", "Useful for incremental change."),
    ("Range", "Broad skills can accelerate learning."),
    ("Thinking in Systems", "Helps spot feedback loops."),
    ("Make Time", "Practical tactics for busy days."),
]


def main() -> None:
    title, note = random.choice(BOOKS)
    print(f"Read '{title}'. {note}")


if __name__ == "__main__":
    main()
