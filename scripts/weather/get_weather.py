"""CLI utility to fetch current weather JSON using Open-Meteo."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from weather_client import WeatherClient, WeatherQuery


def _default_config_path() -> Path:
    return Path(__file__).with_name("config.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch current weather JSON")
    parser.add_argument(
        "--config",
        type=Path,
        default=_default_config_path(),
        help="경로를 지정하지 않으면 scripts/weather/config.json 을 사용합니다.",
    )
    return parser.parse_args()


def load_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"config file not found: {path}")
    text = path.read_text(encoding="utf-8")
    return json.loads(text)


def main() -> None:
    args = parse_args()
    raw_config = load_config(args.config)
    query = WeatherQuery(
        latitude=float(raw_config["latitude"]),
        longitude=float(raw_config["longitude"]),
        timezone=raw_config.get("timezone", "auto"),
        temperature_unit=raw_config.get("temperature_unit", "celsius"),
        wind_speed_unit=raw_config.get("wind_speed_unit", "ms"),
    )
    client = WeatherClient()
    payload = client.fetch_current_weather(query)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
