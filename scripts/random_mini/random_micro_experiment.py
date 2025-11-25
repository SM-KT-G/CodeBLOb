#!/usr/bin/env python3
"""Suggest a tiny experiment to try today."""

from __future__ import annotations

import random

EXPERIMENTS = [
    "Try a different code editor theme for a day.",
    "Schedule a meeting-free afternoon and guard it.",
    "Write tests before coding a small change.",
    "Replace one sync meeting with an async update.",
    "Automate one manual task you do weekly.",
    "Pair program for 30 minutes on a tricky part.",
]


def main() -> None:
    print(random.choice(EXPERIMENTS))


if __name__ == "__main__":
    main()
