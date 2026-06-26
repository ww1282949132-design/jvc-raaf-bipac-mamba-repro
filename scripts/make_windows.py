#!/usr/bin/env python3
"""Validate sample event files and optionally export a window index."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        default="metadata/sample_data_manifest.csv",
        help="Path to sample data manifest.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root used to resolve manifest-relative paths.",
    )
    parser.add_argument(
        "--out",
        default="outputs/window_index.csv",
        help="Output CSV path for window index.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only validate the manifest and files; do not write a window index.",
    )
    return parser.parse_args()


def count_rows_and_channels(path: Path) -> tuple[int, int]:
    rows = 0
    channels = None
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            rows += 1
            if channels is None:
                channels = len(stripped.replace(",", " ").split())
    return rows, channels or 0


def expected_windows(rows: int, length: int, step: int) -> int:
    if rows < length:
        return 0
    return ((rows - length) // step) + 1


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    manifest_path = (repo_root / args.manifest).resolve()
    out_path = (repo_root / args.out).resolve()

    problems: list[str] = []
    window_rows: list[dict[str, object]] = []

    with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for record in reader:
            rel_path = record["relative_path"]
            file_path = (repo_root / rel_path).resolve()
            if not file_path.exists():
                problems.append(f"missing file: {rel_path}")
                continue

            rows, channels = count_rows_and_channels(file_path)
            length = int(record["window_length"])
            step = int(record["window_step"])
            expected = expected_windows(rows, length, step)
            manifest_windows = int(record["clean_windows"])

            if rows != int(record["rows"]):
                problems.append(f"{rel_path}: row count {rows} != manifest {record['rows']}")
            if channels != int(record["channels"]):
                problems.append(f"{rel_path}: channel count {channels} != manifest {record['channels']}")
            if expected != manifest_windows:
                problems.append(f"{rel_path}: windows {expected} != manifest {manifest_windows}")

            for window_id in range(expected):
                start = window_id * step
                window_rows.append(
                    {
                        "sample_id": record["sample_id"],
                        "class": record["class"],
                        "relative_path": rel_path,
                        "window_id": window_id,
                        "start_row": start,
                        "end_row_exclusive": start + length,
                    }
                )

    if problems:
        print("Window validation failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print(f"Window validation passed for {len(window_rows)} clean windows.")

    if not args.check_only:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "sample_id",
                    "class",
                    "relative_path",
                    "window_id",
                    "start_row",
                    "end_row_exclusive",
                ],
            )
            writer.writeheader()
            writer.writerows(window_rows)
        print(f"Wrote {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
