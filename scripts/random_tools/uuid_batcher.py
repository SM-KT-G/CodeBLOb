"""Generate batches of UUIDs with optional namespace support."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List
import uuid


NAMESPACES = {
    "dns": uuid.NAMESPACE_DNS,
    "url": uuid.NAMESPACE_URL,
    "oid": uuid.NAMESPACE_OID,
    "x500": uuid.NAMESPACE_X500,
}


def generate(version: int, count: int, namespace: str | None, name: str | None) -> Iterable[uuid.UUID]:
    if version == 4:
        for _ in range(count):
            yield uuid.uuid4()
        return
    if version == 5:
        if not namespace or not name:
            raise ValueError("Version 5 UUIDs require --namespace and --name.")
        ns = NAMESPACES.get(namespace.lower())
        if ns is None:
            raise ValueError(f"Unknown namespace '{namespace}'. Choose from {', '.join(NAMESPACES)}.")
        for idx in range(count):
            yield uuid.uuid5(ns, f"{name}-{idx}")
        return
    raise ValueError("Only versions 4 and 5 are supported.")


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=5, help="Number of UUIDs to generate.")
    parser.add_argument("--version", type=int, choices=(4, 5), default=4, help="UUID version.")
    parser.add_argument("--namespace", help="Namespace key for version 5 UUIDs (dns/url/oid/x500).")
    parser.add_argument("--name", help="Base name used for version 5 UUIDs.")
    parser.add_argument("--output", help="Optional file to write UUIDs into.")
    return parser.parse_args(argv)


def persist(values: Iterable[uuid.UUID], output: str | None) -> None:
    rendered = "\n".join(str(value) for value in values) + "\n"
    if output:
        Path(output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or [])
    try:
        uuids = list(generate(args.version, args.count, args.namespace, args.name))
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    persist(uuids, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
