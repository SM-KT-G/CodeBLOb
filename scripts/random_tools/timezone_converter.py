"""Convert datetimes between time zones using zoneinfo."""
from __future__ import annotations

import argparse
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List


def parse_iso_datetime(value: str | None) -> datetime:
    if value:
        return datetime.fromisoformat(value)
    return datetime.now()


def convert_time(moment: datetime, from_zone: str, to_zone: str) -> tuple[datetime, datetime]:
    source_zone = ZoneInfo(from_zone)
    target_zone = ZoneInfo(to_zone)
    aware_source = moment.replace(tzinfo=source_zone)
    return aware_source, aware_source.astimezone(target_zone)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--time", help="Datetime in ISO format (default: now)")
    parser.add_argument("--from-zone", required=True, help="IANA timezone to treat input as.")
    parser.add_argument("--to-zone", required=True, help="IANA timezone to convert into.")
    parser.add_argument(
        "--format",
        default="%Y-%m-%d %H:%M:%S %Z%z",
        help="Output strftime format (default: %(default)s)",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or [])
    try:
        moment = parse_iso_datetime(args.time)
        source, target = convert_time(moment, args.from_zone, args.to_zone)
    except Exception as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Source: {source.strftime(args.format)}")
    print(f"Target: {target.strftime(args.format)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
