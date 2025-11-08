"""CLI to fetch current exchange rates as JSON."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from exchange_client import ExchangeClient, ExchangeQuery


def _default_config_path() -> Path:
    return Path(__file__).with_name("config.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch latest exchange rates")
    parser.add_argument(
        "--config",
        type=Path,
        default=_default_config_path(),
        help="경로를 지정하지 않으면 scripts/exchange/config.json 을 사용합니다.",
    )
    return parser.parse_args()


def load_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"config file not found: {path}")
    text = path.read_text(encoding="utf-8")
    return json.loads(text)


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    query = ExchangeQuery(
        base_currency=config["base_currency"],
        symbols=config["symbols"],
        amount=float(config.get("amount", 1.0)),
    )
    client = ExchangeClient()
    payload = client.fetch_rates(query)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
