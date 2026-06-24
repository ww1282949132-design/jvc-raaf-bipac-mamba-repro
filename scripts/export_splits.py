#!/usr/bin/env python3
"""Export per-seed event split files from the released split audit."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--split-audit",
        default="metadata/event_split_audit_10seeds.csv",
        help="Released split audit CSV.",
    )
    parser.add_argument(
        "--out-dir",
        default="outputs/splits",
        help="Output directory for per-seed split CSVs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    split_path = Path(args.split_audit)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    by_seed: dict[str, list[dict[str, str]]] = defaultdict(list)
    with split_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        for row in reader:
            by_seed[row["seed"]].append(row)

    for seed, rows in sorted(by_seed.items(), key=lambda item: int(item[0])):
        out_path = out_dir / f"seed_{seed}_event_split.csv"
        with out_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        split_counts = defaultdict(int)
        for row in rows:
            split_counts[row["split"]] += 1
        counts = ", ".join(f"{name}={count}" for name, count in sorted(split_counts.items()))
        print(f"seed {seed}: {len(rows)} events ({counts}) -> {out_path}")

    print(f"Exported {len(by_seed)} seed split files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

