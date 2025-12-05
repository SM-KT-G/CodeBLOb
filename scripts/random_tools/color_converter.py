"""Color conversion helpers between HEX and RGB."""
from __future__ import annotations

import argparse
import sys
from typing import List, Tuple


def hex_to_rgb(value: str) -> Tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError("HEX value must be 6 characters.")
    r = int(value[0:2], 16)
    g = int(value[2:4], 16)
    b = int(value[4:6], 16)
    return r, g, b


def rgb_to_hex(r: int, g: int, b: int) -> str:
    for comp in (r, g, b):
        if not (0 <= comp <= 255):
            raise ValueError("RGB components must be between 0 and 255.")
    return f"#{r:02X}{g:02X}{b:02X}"


def complement_rgb(rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return tuple(255 - value for value in rgb)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--hex", help="HEX string such as #FFEE00")
    group.add_argument(
        "--rgb",
        nargs=3,
        type=int,
        metavar=("R", "G", "B"),
        help="RGB components (0-255).",
    )
    parser.add_argument("--complement", action="store_true", help="Show complementary color.")
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.hex:
            rgb = hex_to_rgb(args.hex)
            hex_value = rgb_to_hex(*rgb)
        else:
            rgb = tuple(args.rgb)
            hex_value = rgb_to_hex(*rgb)
        print(f"HEX: {hex_value}")
        print(f"RGB: {rgb}")
        if args.complement:
            comp = complement_rgb(rgb)
            print(f"Complement HEX: {rgb_to_hex(*comp)}")
            print(f"Complement RGB: {comp}")
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
