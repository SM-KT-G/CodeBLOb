#!/usr/bin/env python3
"""Produce a random lightweight demo idea for learning."""

from __future__ import annotations

import random

IDEAS = [
    "Build a CLI that summarizes a text file.",
    "Make a small REST endpoint returning mock data.",
    "Create a dashboard card with a live-updating chart.",
    "Write a scraper for headlines into CSV.",
    "Implement a to-do list with local storage only.",
    "Mock a WebSocket chat feed and log events.",
]


def main() -> None:
    print(random.choice(IDEAS))


if __name__ == "__main__":
    main()
