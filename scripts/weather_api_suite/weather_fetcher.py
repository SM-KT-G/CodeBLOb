#!/usr/bin/env python3
"""CLI entry point for fetching weather data from public KMA APIs."""

from __future__ import annotations

import argparse
import os
from typing import Any, Dict

import requests

MID_BASE = "https://apis.data.go.kr/1360000/MidFcstInfoService"
SHORT_BASE = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0"
WARN_BASE = "https://apis.data.go.kr/1360000/WthrWrnInfoService"
AIR_BASE = "https://apis.data.go.kr/B552584/ArpltnStatsSvc"


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


class WeatherAPIClient:
    """Small helper for calling the various weather APIs with shared config."""

    def __init__(self, api_key: str, debug: bool = False) -> None:
        self.api_key = api_key
        self.session = requests.Session()
        self.debug = debug

    def get(self, url: str, params: Dict[str, Any]) -> dict[str, Any]:
        """Perform a GET request including the required API key parameters."""
        query = {
            "serviceKey": self.api_key,
            "dataType": "JSON",
        }
        query.update(params)
        if self.debug:
            print(f"[debug] GET {url} params={query}")
        response = self.session.get(url, params=query, timeout=30)
        response.raise_for_status()
        data = response.json()
        if self.debug:
            print("[debug] Response keys:", list(data.keys()))
        return data


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.api_key:
        parser.error("API key not provided via --api-key or WEATHER_API_KEY env var.")
    if args.debug:
        print(f"[debug] Invoking service={args.service}")
    client = WeatherAPIClient(api_key=args.api_key, debug=args.debug)
    dispatch(args.service, client)
    return 0


def dispatch(service: str, client: WeatherAPIClient) -> None:
    """Dispatch placeholder service handlers."""
    handlers = {
        "short-term": handle_short_term,
        "mid-term": handle_mid_term,
        "warnings": handle_warnings,
        "air": handle_air_quality,
    }
    handler = handlers.get(service)
    if not handler:
        raise ValueError(f"Unsupported service {service}")
    handler(client)


def handle_short_term(client: WeatherAPIClient) -> None:
    print("Short-term forecast handler not implemented yet.")


def handle_mid_term(client: WeatherAPIClient) -> None:
    print("Mid-term forecast handler not implemented yet.")


def handle_warnings(client: WeatherAPIClient) -> None:
    print("Weather warning handler not implemented yet.")


def handle_air_quality(client: WeatherAPIClient) -> None:
    print("Air quality handler not implemented yet.")


if __name__ == "__main__":
    raise SystemExit(main())
