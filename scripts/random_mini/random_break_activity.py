#!/usr/bin/env python3
"""Offer a random quick break activity."""

from __future__ import annotations

import random

ACTIVITIES = [
    "Stretch your neck and shoulders for 2 minutes.",
    "Walk around the room and hydrate.",
    "Look outside and rest your eyes for 60 seconds.",
    "Do 10 squats or push-ups.",
    "Clean your desk for 3 minutes.",
    "Breathe deeply: 4-7-8 cycle three times.",
]


def main() -> None:
    print(random.choice(ACTIVITIES))


if __name__ == "__main__":
    main()
