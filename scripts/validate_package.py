#!/usr/bin/env python3
"""Run package-level consistency checks."""

from __future__ import annotations

import csv
import hashlib
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "metadata" / "sample_data_manifest.csv"
EXPECTED_CLASSES = {
    "coal": {"events": 49, "windows": 882},
    "gangue": {"events": 57, "windows": 1026},
    "empty": {"events": 42, "windows": 756},
}
VALIDATION_REPORTS = [
    REPO_ROOT / "results" / "primary_event_level" / "event_validation_report_10seeds_v2.csv",
    REPO_ROOT / "results" / "baseline_and_controls" / "T6_full_validation_report.csv",
    REPO_ROOT / "results" / "baseline_and_controls" / "T7_fair_controls_validation_report.csv",
    REPO_ROOT / "results" / "baseline_and_controls" / "T8_pac_control_validation_report_v4.csv",
    REPO_ROOT / "results" / "baseline_and_controls" / "T9_empty_rule_validation_report.csv",
    REPO_ROOT / "results" / "roughness_and_thresholds" / "T10_validation_report.csv",
    REPO_ROOT / "results" / "statistics_and_confusion" / "T12_group_lonso_s6_validation_report.csv",
]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_rows_and_channels(path: Path) -> tuple[int, int]:
    rows = 0
    channels = None
    with path.open("r", encoding="utf-8", errors="replace") as handle:
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


def read_manifest() -> list[dict[str, str]]:
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_manifest() -> list[str]:
    problems: list[str] = []
    rows = read_manifest()
    class_events = defaultdict(int)
    class_windows = defaultdict(int)

    for record in rows:
        rel_path = record["relative_path"]
        path = REPO_ROOT / rel_path
        class_name = record["class"]
        class_events[class_name] += 1
        class_windows[class_name] += int(record["clean_windows"])

        if not path.exists():
            problems.append(f"missing manifest file: {rel_path}")
            continue

        actual_rows, actual_channels = count_rows_and_channels(path)
        actual_windows = expected_windows(
            actual_rows,
            int(record["window_length"]),
            int(record["window_step"]),
        )

        if actual_rows != int(record["rows"]):
            problems.append(f"{rel_path}: row count mismatch")
        if actual_channels != int(record["channels"]):
            problems.append(f"{rel_path}: channel count mismatch")
        if actual_windows != int(record["clean_windows"]):
            problems.append(f"{rel_path}: window count mismatch")
        if file_sha256(path) != record["sha256"]:
            problems.append(f"{rel_path}: sha256 mismatch")

    for class_name, expected in EXPECTED_CLASSES.items():
        if class_events[class_name] != expected["events"]:
            problems.append(f"{class_name}: event count {class_events[class_name]} != {expected['events']}")
        if class_windows[class_name] != expected["windows"]:
            problems.append(f"{class_name}: window count {class_windows[class_name]} != {expected['windows']}")

    total_events = sum(class_events.values())
    total_windows = sum(class_windows.values())
    if total_events != 148:
        problems.append(f"total events {total_events} != 148")
    if total_windows != 2664:
        problems.append(f"total clean windows {total_windows} != 2664")

    print("Sample data manifest:")
    for class_name in ["coal", "gangue", "empty"]:
        print(
            f"  {class_name}: {class_events[class_name]} events, "
            f"{class_windows[class_name]} clean windows"
        )
    print(f"  total: {total_events} events, {total_windows} clean windows")

    return problems


def validate_report(path: Path) -> list[str]:
    problems: list[str] = []
    if not path.exists():
        return [f"missing validation report: {path.relative_to(REPO_ROOT)}"]

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if "passed" not in (reader.fieldnames or []):
            return []
        for row_number, row in enumerate(reader, start=2):
            value = row.get("passed", "").strip().lower()
            if value not in {"true", "1", "yes", "pass", "passed"}:
                problems.append(f"{path.relative_to(REPO_ROOT)} row {row_number}: passed={row.get('passed')}")
    return problems


def main() -> int:
    problems = validate_manifest()
    for report in VALIDATION_REPORTS:
        problems.extend(validate_report(report))

    if problems:
        print("\nPackage validation failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("\nPackage validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

