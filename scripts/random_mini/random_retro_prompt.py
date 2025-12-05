#!/usr/bin/env python3
"""Provide a random retrospective question for team sessions."""

from __future__ import annotations

import random

PROMPTS = [
    "What felt surprisingly easy this week?",
    "Where did we get blocked and how can we remove it?",
    "Which habit helped you most recently?",
    "What should we stop doing next sprint?",
    "Who deserves a shoutout and why?",
    "What small experiment should we try next?",
]


def main() -> None:
    print(random.choice(PROMPTS))


if __name__ == "__main__":
    main()
