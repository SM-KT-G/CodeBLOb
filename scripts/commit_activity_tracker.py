#!/usr/bin/env python3
"""
Utility script to inspect git commit activity within a repository.

The script will evolve over a series of commits to include filtering,
aggregation, and export helpers for daily commit tracking.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import subprocess
from typing import Iterable, List


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


@dataclass
class CommitRecord:
    sha: str
    author: str
    authored_at: datetime


def build_git_log_command(repo_path: Path, args: argparse.Namespace) -> List[str]:
    """Construct the git log command according to CLI flags."""
    cmd = [
        "git",
        "-C",
        str(repo_path),
        "log",
        "--date=iso8601-strict",
        "--pretty=format:%H|%an|%ad",
    ]
    if args.start_date:
        cmd.append(f"--since={args.start_date}")
    if args.end_date:
        cmd.append(f"--until={args.end_date}")
    if args.branch:
        cmd.append(args.branch)
    return cmd


def parse_commits(lines: Iterable[str]) -> List[CommitRecord]:
    """Transform git log output into typed commit records."""
    records: List[CommitRecord] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            sha, author, timestamp = line.split("|", 2)
        except ValueError:
            continue
        try:
            authored_at = datetime.fromisoformat(timestamp)
        except ValueError:
            continue
        records.append(CommitRecord(sha=sha, author=author, authored_at=authored_at))
    return records


def load_commits(repo_path: Path, args: argparse.Namespace) -> List[CommitRecord]:
    """Execute git log and parse results."""
    cmd = build_git_log_command(repo_path, args)
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "Failed to read git log")
    lines = proc.stdout.splitlines()
    return parse_commits(lines)


def main() -> None:
    """Parse CLI arguments and perform light validation."""
    args = parse_args()
    repo_path = Path(args.repo).expanduser()
    commits = load_commits(repo_path, args)
    print(f"Found {len(commits)} commits for {repo_path.resolve()}")


if __name__ == "__main__":
    main()
