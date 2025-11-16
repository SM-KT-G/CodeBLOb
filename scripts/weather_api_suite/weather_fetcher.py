#!/usr/bin/env python3
"""CLI entry point for fetching weather data from public KMA APIs."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch weather, forecast, and air quality data using the APIs listed in Weatherapi.md.",
    )
    parser.add_argument(
        "service",
        choices=["short-term", "mid-term", "warnings", "air"],
        help="Target data service to invoke.",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("WEATHER_API_KEY"),
        help="Override API key (defaults to WEATHER_API_KEY env var).",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print verbose output for debugging.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.api_key:
        parser.error("API key not provided via --api-key or WEATHER_API_KEY env var.")
    if args.debug:
        print(f"[debug] Invoking service={args.service}")
    # Placeholder: will be replaced with real service logic in later commits.
    print(f"Weather service '{args.service}' is not implemented yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
