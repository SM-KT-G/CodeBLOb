#!/usr/bin/env python3
"""
Utility script to inspect git commit activity within a repository.

The script will evolve over a series of commits to include filtering,
aggregation, and export helpers for daily commit tracking.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """Collect CLI arguments for future use."""
    parser = argparse.ArgumentParser(
        description="Inspect commit activity for a repository"
    )
    parser.add_argument(
        "repo",
        nargs="?",
        default=".",
        help="Path to the git repository (defaults to current directory)",
    )
    parser.add_argument(
        "--start-date",
        help="Optional lower bound for commits (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end-date",
        help="Optional upper bound for commits (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--branch",
        default=None,
        help="Optional branch to inspect (defaults to current HEAD)",
    )
    return parser.parse_args()


def main() -> None:
    """Parse CLI arguments and perform light validation."""
    args = parse_args()
    repo_path = Path(args.repo).expanduser()
    print(f"Repo path: {repo_path.resolve()}")
    print(f"Start date: {args.start_date or 'not set'}")
    print(f"End date: {args.end_date or 'not set'}")
    print(f"Branch: {args.branch or 'current HEAD'}")


if __name__ == "__main__":
    main()
