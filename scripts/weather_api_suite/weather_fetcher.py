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
    parser.add_argument(
        "--nx",
        type=int,
        default=60,
        help="Grid X coordinate (short-term forecast). Default points to Seoul.",
    )
    parser.add_argument(
        "--ny",
        type=int,
        default=127,
        help="Grid Y coordinate (short-term forecast). Default points to Seoul.",
    )
    parser.add_argument(
        "--base-date",
        type=str,
        help="Override base_date (YYYYMMDD) for short-term API.",
    )
    parser.add_argument(
        "--base-time",
        type=str,
        help="Override base_time (HHMM) for short-term API.",
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
    dispatch(args.service, client, args)
    return 0


def dispatch(service: str, client: WeatherAPIClient, args: argparse.Namespace) -> None:
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
    handler(client, args)


def handle_short_term(client: WeatherAPIClient, args: argparse.Namespace) -> None:
    base_date, base_time = get_short_term_timestamp(args)
    params = {
        "pageNo": "1",
        "numOfRows": "200",
        "base_date": base_date,
        "base_time": base_time,
        "nx": args.nx,
        "ny": args.ny,
    }
    endpoint = f"{SHORT_BASE}/getVilageFcst"
    data = client.get(endpoint, params)
    items = extract_items(data)
    if not items:
        print("No short-term forecast data returned.")
        return
    for item in items[:20]:
        print(
            f"{item['fcstDate']} {item['fcstTime']} {item['category']}: {item['fcstValue']}",
        )


def handle_mid_term(client: WeatherAPIClient, args: argparse.Namespace) -> None:
    print("Mid-term forecast handler not implemented yet.")


def handle_warnings(client: WeatherAPIClient, args: argparse.Namespace) -> None:
    print("Weather warning handler not implemented yet.")


def handle_air_quality(client: WeatherAPIClient, args: argparse.Namespace) -> None:
    print("Air quality handler not implemented yet.")


def get_short_term_timestamp(args: argparse.Namespace) -> tuple[str, str]:
    """Return (base_date, base_time) strings."""
    if args.base_date and args.base_time:
        return args.base_date, args.base_time
    from datetime import datetime, timedelta

    now = datetime.now()
    base = now - timedelta(hours=1)
    return base.strftime("%Y%m%d"), base.strftime("%H00")


def extract_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Safely pull the 'item' list from a nested response object."""
    return (
        payload.get("response", {})
        .get("body", {})
        .get("items", {})
        .get("item", [])
    )


if __name__ == "__main__":
    raise SystemExit(main())
