#!/usr/bin/env python3
"""Suggest a pairing prompt to start a session."""

from __future__ import annotations

import random

PROMPTS = [
    "What's our success criteria for this session?",
    "Which tests will we watch closely?",
    "Who drives first and for how long?",
    "What tiny slice can we deliver today?",
    "What will we defer if we run out of time?",
]


def main() -> None:
    print(random.choice(PROMPTS))


if __name__ == "__main__":
    main()
