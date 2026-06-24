#!/usr/bin/env python3
"""Recompute event-level metrics and confusion matrices from prediction CSVs."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


DEFAULT_CLASSES = ["coal", "gangue", "empty"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", help="Prediction CSV containing y_true and y_pred columns.")
    parser.add_argument(
        "--classes",
        default=",".join(DEFAULT_CLASSES),
        help="Comma-separated class order.",
    )
    parser.add_argument(
        "--group-cols",
        default="",
        help="Optional comma-separated columns used to compute grouped metrics.",
    )
    parser.add_argument(
        "--out-dir",
        default="outputs/metrics",
        help="Output directory.",
    )
    return parser.parse_args()


def find_column(fieldnames: list[str], candidates: list[str]) -> str:
    lower_map = {name.lower(): name for name in fieldnames}
    for candidate in candidates:
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    raise ValueError(f"Could not find any of these columns: {candidates}")


def group_key(row: dict[str, str], columns: list[str]) -> tuple[str, ...]:
    return tuple(row.get(column, "") for column in columns)


def compute_metrics(rows: list[dict[str, str]], true_col: str, pred_col: str, classes: list[str]) -> tuple[dict[str, float], dict[tuple[str, str], int]]:
    confusion: dict[tuple[str, str], int] = defaultdict(int)
    for row in rows:
        confusion[(row[true_col], row[pred_col])] += 1

    labels = list(classes)
    for row in rows:
        if row[true_col] not in labels:
            labels.append(row[true_col])
        if row[pred_col] not in labels:
            labels.append(row[pred_col])

    total = len(rows)
    correct = sum(confusion[(label, label)] for label in labels)
    accuracy = correct / total if total else 0.0

    precisions = []
    recalls = []
    f1s = []
    for label in labels:
        tp = confusion[(label, label)]
        predicted = sum(confusion[(true_label, label)] for true_label in labels)
        actual = sum(confusion[(label, pred_label)] for pred_label in labels)
        precision = tp / predicted if predicted else 0.0
        recall = tp / actual if actual else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)

    metrics = {
        "n": float(total),
        "accuracy": accuracy,
        "macro_precision": sum(precisions) / len(labels) if labels else 0.0,
        "macro_recall": sum(recalls) / len(labels) if labels else 0.0,
        "macro_f1": sum(f1s) / len(labels) if labels else 0.0,
    }
    return metrics, confusion


def format_float(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.10f}"


def main() -> int:
    args = parse_args()
    prediction_path = Path(args.predictions)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with prediction_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    true_col = find_column(fieldnames, ["y_true", "true", "label", "target"])
    pred_col = find_column(fieldnames, ["y_pred", "pred", "prediction", "predicted"])
    classes = [item.strip() for item in args.classes.split(",") if item.strip()]
    group_columns = [item.strip() for item in args.group_cols.split(",") if item.strip()]

    missing_group_cols = [column for column in group_columns if column not in fieldnames]
    if missing_group_cols:
        raise ValueError(f"Missing group columns: {missing_group_cols}")

    grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    if group_columns:
        for row in rows:
            grouped[group_key(row, group_columns)].append(row)
    else:
        grouped[("all",)] = rows
        group_columns = ["group"]

    metric_rows: list[dict[str, str]] = []
    confusion_rows: list[dict[str, str]] = []

    for key, group_rows in sorted(grouped.items()):
        metrics, confusion = compute_metrics(group_rows, true_col, pred_col, classes)
        base = {column: value for column, value in zip(group_columns, key)}
        metric_rows.append(
            {
                **base,
                "n": format_float(metrics["n"]),
                "accuracy": format_float(metrics["accuracy"]),
                "macro_precision": format_float(metrics["macro_precision"]),
                "macro_recall": format_float(metrics["macro_recall"]),
                "macro_f1": format_float(metrics["macro_f1"]),
            }
        )
        labels = list(classes)
        for row in group_rows:
            if row[true_col] not in labels:
                labels.append(row[true_col])
            if row[pred_col] not in labels:
                labels.append(row[pred_col])
        for true_label in labels:
            for pred_label in labels:
                confusion_rows.append(
                    {
                        **base,
                        "true_label": true_label,
                        "pred_label": pred_label,
                        "count": str(confusion[(true_label, pred_label)]),
                    }
                )

    metrics_path = out_dir / "event_metrics.csv"
    confusion_path = out_dir / "confusion_matrix_long.csv"

    with metrics_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=group_columns + ["n", "accuracy", "macro_precision", "macro_recall", "macro_f1"],
        )
        writer.writeheader()
        writer.writerows(metric_rows)

    with confusion_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=group_columns + ["true_label", "pred_label", "count"],
        )
        writer.writeheader()
        writer.writerows(confusion_rows)

    print(f"Read {len(rows)} predictions from {prediction_path}")
    print(f"Wrote {metrics_path}")
    print(f"Wrote {confusion_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

