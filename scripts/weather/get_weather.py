"""CLI utility to fetch current weather JSON using Open-Meteo."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

from requests import RequestException

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
    parser.add_argument("--latitude", type=float, help="위도를 직접 지정해 config 값을 덮어씁니다.")
    parser.add_argument("--longitude", type=float, help="경도를 직접 지정해 config 값을 덮어씁니다.")
    parser.add_argument("--timezone", type=str, help="시간대를 직접 지정합니다.")
    parser.add_argument(
        "--temperature-unit",
        dest="temperature_unit",
        type=str,
        help="섭씨(celsius) 외 단위를 사용할 때 입력합니다.",
    )
    parser.add_argument(
        "--wind-speed-unit",
        dest="wind_speed_unit",
        type=str,
        help="기본값(ms) 대신 사용할 풍속 단위를 입력합니다.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="결과 JSON 을 지정된 경로에 저장합니다 (stdout 출력은 그대로 유지).",
    )
    return parser.parse_args()


def load_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"config file not found: {path}")
    text = path.read_text(encoding="utf-8-sig")
    return json.loads(text)


def main() -> None:
    args = parse_args()
    raw_config = load_config(args.config)
    query = WeatherQuery(
        latitude=float(args.latitude if args.latitude is not None else raw_config["latitude"]),
        longitude=float(
            args.longitude if args.longitude is not None else raw_config["longitude"]
        ),
        timezone=args.timezone or raw_config.get("timezone", "auto"),
        temperature_unit=args.temperature_unit or raw_config.get("temperature_unit", "celsius"),
        wind_speed_unit=args.wind_speed_unit or raw_config.get("wind_speed_unit", "ms"),
    )
    client = WeatherClient()
    payload = client.fetch_current_weather(query)
    json_text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(json_text, encoding="utf-8")
    print(json_text)


def _entrypoint() -> int:
    try:
        main()
        return 0
    except FileNotFoundError as exc:
        print(f"[config] {exc}", file=sys.stderr)
    except KeyError as exc:
        print(f"[config] missing required field: {exc}", file=sys.stderr)
    except (ValueError, RequestException) as exc:
        print(f"[weather] 요청에 실패했습니다: {exc}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(_entrypoint())
