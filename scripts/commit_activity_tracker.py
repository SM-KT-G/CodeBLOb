#!/usr/bin/env python3
"""
Utility script to inspect git commit activity within a repository.

The script will evolve over a series of commits to include filtering,
aggregation, and export helpers for daily commit tracking.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import subprocess
from typing import Dict, Iterable, List, Sequence, Tuple


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
    parser.add_argument(
        "--csv-output",
        help="Optional file path to export the daily summary as CSV",
    )
    return parser.parse_args()


@dataclass
class CommitRecord:
    sha: str
    author: str
    authored_at: datetime


@dataclass
class DailySummary:
    author: str
    day: date
    count: int


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


def summarize_by_day(commits: Iterable[CommitRecord]) -> List[DailySummary]:
    """Group commit counts by author/day pairs."""
    counter: Dict[Tuple[str, date], int] = defaultdict(int)
    for commit in commits:
        key = (commit.author, commit.authored_at.date())
        counter[key] += 1
    summaries = [
        DailySummary(author=author, day=day, count=count)
        for (author, day), count in counter.items()
    ]
    summaries.sort(key=lambda summary: (summary.day, summary.author))
    return summaries


def print_summary(summaries: Iterable[DailySummary]) -> None:
    """Emit a tiny table describing daily commit counts."""
    print("Daily commit totals:")
    print("-" * 60)
    print(f"{'Date':<12} {'Author':<25} {'Commits':>8}")
    print("-" * 60)
    for summary in summaries:
        print(f"{summary.day.isoformat():<12} {summary.author:<25} {summary.count:>8}")
    print("-" * 60)


def summarize_author_totals(commits: Iterable[CommitRecord]) -> List[Tuple[str, int]]:
    """Collapse commit counts per author."""
    totals: Dict[str, int] = defaultdict(int)
    for commit in commits:
        totals[commit.author] += 1
    return sorted(totals.items(), key=lambda entry: entry[1], reverse=True)


def print_author_totals(totals: Sequence[Tuple[str, int]]) -> None:
    """Display overall commit totals per author."""
    print("Author totals:")
    print("-" * 60)
    print(f"{'Author':<25} {'Commits':>8}")
    print("-" * 60)
    for author, count in totals:
        print(f"{author:<25} {count:>8}")
    print("-" * 60)


def write_csv(summaries: Iterable[DailySummary], destination: Path) -> None:
    """Persist daily summaries to a CSV file."""
    destination = destination.expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["date", "author", "commit_count"])
        for summary in summaries:
            writer.writerow([summary.day.isoformat(), summary.author, summary.count])
    print(f"Wrote CSV summary to {destination}")


def main() -> None:
    """Parse CLI arguments and perform light validation."""
    args = parse_args()
    repo_path = Path(args.repo).expanduser()
    commits = load_commits(repo_path, args)
    print(f"Found {len(commits)} commits for {repo_path.resolve()}")
    summaries = summarize_by_day(commits)
    if summaries:
        print_summary(summaries)
        if args.csv_output:
            write_csv(summaries, Path(args.csv_output))
    else:
        print("No commits to summarize.")
    totals = summarize_author_totals(commits)
    if totals:
        print_author_totals(totals)


if __name__ == "__main__":
    main()
