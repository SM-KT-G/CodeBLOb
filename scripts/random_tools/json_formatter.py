"""Tiny CLI to pretty-print or minify JSON payloads."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, List


def load_payload(source: str | None, text: str | None) -> Any:
    if source:
        return json.loads(Path(source).read_text(encoding="utf-8"))
    if text is not None:
        return json.loads(text)
    return json.load(sys.stdin)


def format_payload(payload: Any, minify: bool, indent: int, sort_keys: bool) -> str:
    if minify:
        return json.dumps(payload, separators=(",", ":"), sort_keys=sort_keys)
    return json.dumps(payload, indent=indent, ensure_ascii=False, sort_keys=sort_keys)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", help="Path to JSON file. When omitted, read from text/STDIN.")
    parser.add_argument("--text", help="Inline JSON payload to format.")
    parser.add_argument("--indent", type=int, default=2, help="Indent level for pretty-print mode.")
    parser.add_argument("--minify", action="store_true", help="Produce a minified payload.")
    parser.add_argument("--sort-keys", action="store_true", help="Sort keys alphabetically.")
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        payload = load_payload(args.file, args.text)
        result = format_payload(payload, args.minify, args.indent, args.sort_keys)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    sys.stdout.write(result)
    if not result.endswith("\n"):
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
