#!/usr/bin/env python3
"""Generate a random five-color hex palette."""

from __future__ import annotations

import random


def random_color() -> str:
    """Return a random hex color like #A1B2C3."""
    return "#" + "".join(f"{random.randint(0, 255):02X}" for _ in range(3))


def main() -> None:
    palette = [random_color() for _ in range(5)]
    print(" ".join(palette))


if __name__ == "__main__":
    main()
