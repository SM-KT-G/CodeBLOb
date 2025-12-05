"""Utilities to inspect and debug palindromes from the command line."""
from __future__ import annotations

import argparse
import sys
from typing import List, Tuple


def normalize(text: str, ignore_case: bool, alnum_only: bool) -> str:
    """Normalize text according to provided flags."""
    if ignore_case:
        text = text.lower()
    if alnum_only:
        text = "".join(ch for ch in text if ch.isalnum())
    return text


def find_mismatches(text: str) -> List[Tuple[int, str, str]]:
    """Return positions where palindrome symmetry fails."""
    mismatches: List[Tuple[int, str, str]] = []
    midpoint = len(text) // 2
    for i in range(midpoint):
        left = text[i]
        right = text[-(i + 1)]
        if left != right:
            mismatches.append((i, left, right))
    return mismatches


def inspect_palindrome(
    text: str, ignore_case: bool = True, alnum_only: bool = True
) -> Tuple[bool, List[Tuple[int, str, str]], str]:
    """Inspect the text and report palindrome status."""
    normalized = normalize(text, ignore_case=ignore_case, alnum_only=alnum_only)
    mismatches = find_mismatches(normalized)
    return not mismatches, mismatches, normalized


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "text",
        help="Text to inspect. Surround with quotes when spaces are involved.",
    )
    parser.add_argument(
        "--keep-case",
        action="store_true",
        help="Do not force lower-case comparison.",
    )
    parser.add_argument(
        "--keep-symbols",
        action="store_true",
        help="Do not strip non-alphanumeric characters.",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    is_pal, mismatches, normalized = inspect_palindrome(
        args.text,
        ignore_case=not args.keep_case,
        alnum_only=not args.keep_symbols,
    )
    print(f"Normalized text: {normalized}")
    if is_pal:
        print("✅ This is a palindrome.")
        return 0
    print("❌ Not a palindrome. First few mismatches:")
    for idx, left, right in mismatches[:5]:
        print(f"  position {idx}: {left!r} != {right!r}")
    if len(mismatches) > 5:
        print(f"  ... {len(mismatches) - 5} more mismatch pairs")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
