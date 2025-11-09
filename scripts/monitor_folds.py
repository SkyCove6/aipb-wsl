#!/usr/bin/env python3
"""
Continuous fold-progress monitor.

Reads the latest `[progress] ...` line from each `wf_fold_*.log` file and
prints a compact snapshot at a fixed interval (default: 10 seconds).
"""

from __future__ import annotations

import argparse
import os
import re
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional

PROGRESS_PATTERN = re.compile(
    r"\[progress\]\s+(?P<name>\S+)\s+"
    r"ts=(?P<ts>\S+)\s+"
    r"fills=(?P<fills>\d+)\s+"
    r"equity=(?P<equity>-?[\d\.]+)\s+"
    r"window=(?P<window>\S+)"
)


def read_last_progress(path: Path, tail_lines: int = 200) -> Optional[Dict[str, str]]:
    """
    Read up to `tail_lines` from the end of `path` looking for the most recent
    `[progress] ...` entry. Returns a dict of captured fields or None.
    """
    if not path.exists():
        return None
    try:
        size = path.stat().st_size
        with path.open("rb") as handle:
            if size > 0:
                handle.seek(max(size - 4096 * max(1, tail_lines // 4), 0))
            data = handle.read().decode("utf-8", errors="replace")
    except OSError:
        return None

    lines = deque(data.splitlines(), maxlen=tail_lines)
    for line in reversed(lines):
        match = PROGRESS_PATTERN.search(line)
        if match:
            return match.groupdict()
    return None


def render(statuses: Dict[str, Dict[str, str]]) -> str:
    """
    Format the current snapshot into a table.
    """
    if not statuses:
        return "No progress entries yet."

    headers = ("Fold", "Timestamp", "Fills", "Equity", "Window")
    rows = [headers]
    for fold in sorted(statuses):
        info = statuses[fold]
        rows.append(
            (
                fold,
                info.get("ts", "?"),
                info.get("fills", "?"),
                info.get("equity", "?"),
                info.get("window", "?"),
            )
        )

    col_widths = [max(len(str(row[idx])) for row in rows) for idx in range(len(headers))]
    lines = []
    for row in rows:
        parts = [
            str(val).ljust(col_widths[idx])
            for idx, val in enumerate(row)
        ]
        lines.append("  ".join(parts))
    return "\n".join(lines)


def collect_status(log_dir: Path, tail_lines: int = 200) -> Dict[str, Dict[str, str]]:
    statuses: Dict[str, Dict[str, str]] = {}
    for path in sorted(log_dir.glob("wf_fold_*.log")):
        info = read_last_progress(path, tail_lines=tail_lines)
        if info:
            statuses[info["name"]] = info
    return statuses


def collect_status_filtered(
    log_dir: Path,
    tail_lines: int,
    max_age: Optional[float],
) -> Dict[str, Dict[str, str]]:
    now = time.time()
    statuses: Dict[str, Dict[str, str]] = {}
    for path in sorted(log_dir.glob("wf_fold_*.log")):
        if max_age is not None:
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            if now - mtime > max_age:
                continue
        info = read_last_progress(path, tail_lines=tail_lines)
        if info:
            statuses[info["name"]] = info
    return statuses


def main(argv: Optional[Iterable[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Continuously print fold progress snapshots.")
    parser.add_argument(
        "--dir",
        default="logs",
        help="Directory containing wf_fold_*.log files (default: %(default)s)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=10.0,
        help="Seconds between refreshes (default: %(default)s)",
    )
    parser.add_argument(
        "--tail-lines",
        type=int,
        default=200,
        help="Max number of lines to examine from each log (default: %(default)s)",
    )
    parser.add_argument(
        "--max-age",
        type=float,
        default=None,
        help="Only include logs updated within the last N seconds (default: include all)",
    )
    args = parser.parse_args(argv)

    log_dir = Path(args.dir).expanduser().resolve()
    if not log_dir.exists():
        raise SystemExit(f"Log directory not found: {log_dir}")

    try:
        while True:
            statuses = collect_status_filtered(
                log_dir,
                tail_lines=max(10, args.tail_lines),
                max_age=args.max_age,
            )
            os.system("clear")
            print(time.strftime("%Y-%m-%d %H:%M:%S"), "(refresh every", f"{args.interval:.1f}s)")
            print(render(statuses))
            time.sleep(max(args.interval, 1.0))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
