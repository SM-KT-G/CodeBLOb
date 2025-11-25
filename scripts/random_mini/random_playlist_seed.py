#!/usr/bin/env python3
"""Suggest a random playlist theme to cue up music."""

from __future__ import annotations

import random

THEMES = [
    "Lo-fi beats for deep work",
    "Upbeat pop for chores",
    "Instrumental movie scores",
    "Jazz for morning coffee",
    "Synthwave night drive",
    "Acoustic focus mix",
    "Classical piano sprint",
    "Rock anthems for shipping",
]


def main() -> None:
    print(random.choice(THEMES))


if __name__ == "__main__":
    main()
