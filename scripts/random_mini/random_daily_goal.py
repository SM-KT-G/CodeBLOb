#!/usr/bin/env python3
"""Suggest a tiny daily goal to keep momentum."""

from __future__ import annotations

import random

GOALS = [
    "Write one paragraph about something you learned.",
    "Refactor one small function.",
    "Read 5 pages of a technical book.",
    "Clean up your downloads folder.",
    "Review one old note and update it.",
    "Automate a repetitive task.",
    "Sketch tomorrow's plan on a sticky note.",
    "Share one helpful link with a teammate.",
]


def main() -> None:
    print(random.choice(GOALS))


if __name__ == "__main__":
    main()
