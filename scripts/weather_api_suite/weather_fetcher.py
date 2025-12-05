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
    parser.add_argument(
        "--mid-region",
        type=str,
        default="11B10101",
        help="Region ID for mid-term land forecast (default=Seoul).",
    )
    parser.add_argument(
        "--mid-tmfc",
        type=str,
        help="Override tmFc (YYYYMMDDHHMM) for mid-term calls.",
    )
    parser.add_argument(
        "--warning-region",
        type=str,
        default="108",
        help="Station ID for weather warnings (default=108 nationwide).",
    )
    parser.add_argument(
        "--sido",
        type=str,
        default="서울",
        help="시도 이름 (air quality service).",
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
    tm_fc = args.mid_tmfc or compute_mid_tmfc()
    params = {
        "pageNo": "1",
        "numOfRows": "10",
        "tmFc": tm_fc,
        "regId": args.mid_region,
    }
    endpoint = f"{MID_BASE}/getMidLandFcst"
    data = client.get(endpoint, params)
    items = extract_items(data)
    if not items:
        print("No mid-term forecast data returned.")
        return
    entry = items[0]
    fields = [
        ("wf3Am", "Day3 AM"),
        ("wf3Pm", "Day3 PM"),
        ("wf4Am", "Day4 AM"),
        ("wf4Pm", "Day4 PM"),
        ("wf5Am", "Day5 AM"),
        ("wf5Pm", "Day5 PM"),
    ]
    print(f"Mid-term outlook (tmFc={tm_fc}, regId={args.mid_region}):")
    for key, label in fields:
        if key in entry:
            print(f"{label}: {entry[key]}")


def handle_warnings(client: WeatherAPIClient, args: argparse.Namespace) -> None:
    params = {
        "pageNo": "1",
        "numOfRows": "50",
        "stnId": args.warning_region,
    }
    endpoint = f"{WARN_BASE}/getWthrWrnList"
    data = client.get(endpoint, params)
    items = extract_items(data)
    if not items:
        print("No weather warnings returned.")
        return
    for entry in items[:5]:
        title = entry.get("title", "N/A")
        tm = entry.get("tmFc") or entry.get("tmSeq") or "Unknown"
        print(f"- [{tm}] {title}")


def handle_air_quality(client: WeatherAPIClient, args: argparse.Namespace) -> None:
    params = {
        "pageNo": "1",
        "numOfRows": "100",
        "sidoName": args.sido,
        "returnType": "json",
    }
    endpoint = f"{AIR_BASE}/getCtprvnRltmMesureDnsty"
    data = client.get(endpoint, params)
    items = extract_items(data)
    if not items:
        print("No air quality data returned.")
        return
    top = items[:3]
    print(f"Air quality in {args.sido}:")
    for row in top:
        station = row.get("stationName")
        pm10 = row.get("pm10Value")
        pm25 = row.get("pm25Value")
        khai = row.get("khaiValue")
        print(f"- {station}: PM10={pm10}, PM2.5={pm25}, KHAI={khai}")


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


def compute_mid_tmfc() -> str:
    """Return tmFc aligned to the latest 0600/1800 cycle."""
    from datetime import datetime

    now = datetime.now()
    hour = now.hour
    cycle = 18 if hour >= 18 else 6 if hour >= 6 else 18
    if hour < 6:
        from datetime import timedelta

        now = now - timedelta(days=1)
    return now.replace(hour=cycle, minute=0, second=0, microsecond=0).strftime(
        "%Y%m%d%H%M",
    )


if __name__ == "__main__":
    raise SystemExit(main())
