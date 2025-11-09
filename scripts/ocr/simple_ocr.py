#!/usr/bin/env python3
"""Minimal OCR example that will be fleshed out in subsequent commits."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Demonstrate a basic OCR pipeline using Pillow and pytesseract.",
    )
    parser.add_argument(
        "--text",
        default="Hello OCR!",
        help="Text that will be rendered into the sample image.",
    )
    parser.add_argument(
        "--font-size",
        type=int,
        default=48,
        help="Font size (in pt) used when generating the test image.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable extra logging while the script runs.",
    )
    return parser


def main() -> None:
    """Entry point for the OCR example script."""
    args = build_parser().parse_args()
    if args.debug:
        print("Debug mode enabled - OCR pipeline not implemented yet.")


if __name__ == "__main__":
    main()
