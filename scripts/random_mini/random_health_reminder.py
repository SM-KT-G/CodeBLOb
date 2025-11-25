#!/usr/bin/env python3
"""Print a short health reminder for desk workdays."""

from __future__ import annotations

import random

REMINDERS = [
    "Refill your water bottle now.",
    "Relax your jaw and drop your shoulders.",
    "Check your posture: ears over shoulders.",
    "Blink and focus on a distant point for 20 seconds.",
    "Stand up for a minute and stretch your legs.",
]


def main() -> None:
    print(random.choice(REMINDERS))


if __name__ == "__main__":
    main()
