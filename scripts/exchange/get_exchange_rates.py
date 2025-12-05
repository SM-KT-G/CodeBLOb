"""CLI to fetch current exchange rates as JSON."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

from requests import RequestException

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
    parser.add_argument(
        "--base",
        dest="base_currency",
        type=str,
        help="기본 통화(예: USD)를 config 값 대신 직접 지정합니다.",
    )
    parser.add_argument(
        "--symbols",
        type=str,
        help="쉼표로 구분된 통화 리스트를 직접 지정합니다. 예) KRW,JPY,EUR",
    )
    parser.add_argument(
        "--amount",
        type=float,
        help="환산 기준 금액을 직접 지정합니다.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="결과 JSON을 지정한 파일에도 저장합니다.",
    )
    return parser.parse_args()


def load_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"config file not found: {path}")
    text = path.read_text(encoding="utf-8-sig")
    return json.loads(text)


def _parse_symbols(raw: Any) -> List[str]:
    if isinstance(raw, str):
        return [token.strip().upper() for token in raw.split(",") if token.strip()]
    if isinstance(raw, Iterable):
        return [str(token).strip().upper() for token in raw if str(token).strip()]
    raise TypeError("symbols must be a string or iterable")


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    query = ExchangeQuery(
        base_currency=(args.base_currency or config["base_currency"]).upper(),
        symbols=_parse_symbols(
            args.symbols if args.symbols is not None else config["symbols"]
        ),
        amount=float(args.amount if args.amount is not None else config.get("amount", 1.0)),
    )
    client = ExchangeClient()
    payload = client.fetch_rates(query)
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
    except (TypeError, ValueError) as exc:
        print(f"[config] invalid value: {exc}", file=sys.stderr)
    except RequestException as exc:
        print(f"[exchange] API 요청에 실패했습니다: {exc}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(_entrypoint())
