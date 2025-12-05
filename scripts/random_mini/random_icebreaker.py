#!/usr/bin/env python3
"""Serve a random icebreaker question for meetings or chats."""

from __future__ import annotations

import random

QUESTIONS = [
    "What's a small win you had this week?",
    "Which hobby would you try if you had a free weekend?",
    "What's a song you never skip?",
    "If you could learn one tool instantly, what would it be?",
    "What's your favorite quick meal to cook?",
    "Which book or show are you enjoying lately?",
]


def main() -> None:
    print(random.choice(QUESTIONS))


if __name__ == "__main__":
    main()
