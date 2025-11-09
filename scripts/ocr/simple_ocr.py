#!/usr/bin/env python3
"""Minimal OCR example that will be fleshed out in subsequent commits."""

from __future__ import annotations

import argparse

from PIL import Image, ImageDraw, ImageFont


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


def _load_font(font_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Best-effort font loader that falls back to Pillow's default font."""
    try:
        return ImageFont.truetype("DejaVuSans.ttf", font_size)
    except OSError:
        return ImageFont.load_default()


def generate_sample_image(text: str, font_size: int) -> Image.Image:
    """Render text into a Pillow image that will later feed the OCR engine."""
    font = _load_font(font_size)
    padding = 20
    dummy_img = Image.new("RGB", (1, 1), color="white")
    draw = ImageDraw.Draw(dummy_img)
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0] + padding * 2
    height = bbox[3] - bbox[1] + padding * 2
    image = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((padding, padding), text, fill="black", font=font)
    return image


if __name__ == "__main__":
    main()
