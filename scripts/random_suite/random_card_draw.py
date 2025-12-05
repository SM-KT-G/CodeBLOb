#!/usr/bin/env python3
"""Draw cards from a freshly shuffled deck."""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass

SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["A"] + [str(n) for n in range(2, 11)] + ["J", "Q", "K"]


@dataclass(frozen=True)
class Card:
    rank: str
    suit: str

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Draw cards from a deck.")
    parser.add_argument("--count", type=int, default=5, help="Cards to draw.")
    parser.add_argument("--seed", type=int, help="Optional RNG seed.")
    return parser


def new_deck() -> list[Card]:
    return [Card(rank, suit) for suit in SUITS for rank in RANKS]


def main() -> None:
    args = build_parser().parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    deck = new_deck()
    random.shuffle(deck)
    draw = deck[: args.count]
    print("Drawn cards:", " ".join(map(str, draw)))


if __name__ == "__main__":
    main()
