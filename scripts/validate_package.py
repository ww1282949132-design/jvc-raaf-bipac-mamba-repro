#!/usr/bin/env python3
"""Run package-level consistency checks."""

from __future__ import annotations

import csv
import hashlib
import math
import statistics
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "metadata" / "sample_data_manifest.csv"
EVENT_MANIFEST = REPO_ROOT / "metadata" / "event_manifest.csv"
MODEL_REFERENCE = REPO_ROOT / "model.py"
FIVE_SEED_SPLIT_AUDIT = REPO_ROOT / "metadata" / "physical_event_split_audit_5seeds.csv"
FIVE_SEED_TEST_PREDICTIONS = REPO_ROOT / "results" / "primary_event_level" / "test_predictions_5seeds.csv"
SUPPLEMENTARY_SOURCE_GROUP_PREDICTIONS = REPO_ROOT / "results" / "primary_window_level" / "group_disjoint_predictions_raaf_5seeds.csv"
SUPPLEMENTARY_SOURCE_GROUP_SEED_METRICS = REPO_ROOT / "results" / "primary_window_level" / "group_disjoint_seed_metrics_raaf_5seeds.csv"
SUPPLEMENTARY_SOURCE_GROUP_SUMMARY = REPO_ROOT / "results" / "primary_window_level" / "group_disjoint_summary_raaf_5seeds.csv"
FIVE_SEEDS = {"42", "43", "44", "45", "46"}
SCENARIOS = {f"S{idx}" for idx in range(7)}
CLASS_LABELS = ["coal", "gangue", "empty"]
PUBLIC_SAMPLE_EXPECTED_CLASSES = {
    "coal": {"events": 12, "windows": 216},
    "gangue": {"events": 14, "windows": 252},
    "empty": {"events": 11, "windows": 198},
}
PUBLIC_SAMPLE_TOTAL_EVENTS = 37
PUBLIC_SAMPLE_TOTAL_WINDOWS = 666
MANUSCRIPT_EXPECTED_CLASSES = {
    "coal": {"events": 49, "windows": 882},
    "gangue": {"events": 57, "windows": 1026},
    "empty": {"events": 42, "windows": 756},
}
MANUSCRIPT_TOTAL_EVENTS = 148
MANUSCRIPT_TOTAL_WINDOWS = 2664
VALIDATION_REPORTS = [
    REPO_ROOT / "results" / "primary_event_level" / "event_validation_report_10seeds_v2.csv",
    REPO_ROOT / "results" / "baseline_and_controls" / "T6_full_validation_report.csv",
    REPO_ROOT / "results" / "baseline_and_controls" / "T7_fair_controls_validation_report.csv",
    REPO_ROOT / "results" / "baseline_and_controls" / "T8_pac_control_validation_report_v4.csv",
    REPO_ROOT / "results" / "baseline_and_controls" / "T9_empty_rule_validation_report.csv",
    REPO_ROOT / "results" / "roughness_and_thresholds" / "T10_validation_report.csv",
    REPO_ROOT / "results" / "statistics_and_confusion" / "T12_group_lonso_s6_validation_report.csv",
]
RETAINED_TABLE4_HEADLINE = {
    "Avg7_acc": "93.74+/-0.33",
    "S6_acc": "91.18+/-0.41",
    "Avg7_f1": "93.93+/-0.32",
    "S6_f1": "91.43+/-0.37",
}
MODEL_REFERENCE_REQUIRED_TOKENS = [
    "class ResNetStem",
    "class BidirectionalMambaBlock",
    "class CrossAttention",
    "class RoughnessAwareAdaptiveFusion",
    "class RAAFBiPACMamba",
    "class GradientReversal",
    "def grl_sigmoid_coefficient",
    "def latent_vibration_roughness",
    "def estimate_pac_thresholds",
    "def pac_loss",
    "mamba_ssm",
]
MODEL_REFERENCE_FORBIDDEN_TOKENS = [
    "DATASET_FOLDER",
    "torch.load",
    "load_state_dict",
    ".pth",
    ".pt",
    "np.load",
    "DataLoader",
    "train_loader",
    "roughness_thresholds",
    "best_model",
    "optimizer",
    "scheduler",
    "EPOCHS",
    "DEVICE",
    "C:\\",
    "D:\\",
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


def read_manifest() -> list[dict[str, str]]:
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), reader.fieldnames or []


def validate_manifest() -> list[str]:
    problems: list[str] = []
    rows = read_manifest()
    class_events = defaultdict(int)
    class_windows = defaultdict(int)
    sha_paths = defaultdict(list)

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
        actual_sha = file_sha256(path)
        sha_paths[actual_sha].append(rel_path)
        if actual_sha != record["sha256"]:
            problems.append(f"{rel_path}: sha256 mismatch")

    for sha256, paths in sorted(sha_paths.items()):
        if len(paths) > 1:
            joined_paths = ", ".join(paths)
            problems.append(f"duplicate file content sha256={sha256}: {joined_paths}")

    for class_name, expected in PUBLIC_SAMPLE_EXPECTED_CLASSES.items():
        if class_events[class_name] != expected["events"]:
            problems.append(f"{class_name}: event count {class_events[class_name]} != {expected['events']}")
        if class_windows[class_name] != expected["windows"]:
            problems.append(f"{class_name}: window count {class_windows[class_name]} != {expected['windows']}")

    total_events = sum(class_events.values())
    total_windows = sum(class_windows.values())
    if total_events != PUBLIC_SAMPLE_TOTAL_EVENTS:
        problems.append(f"total events {total_events} != {PUBLIC_SAMPLE_TOTAL_EVENTS}")
    if total_windows != PUBLIC_SAMPLE_TOTAL_WINDOWS:
        problems.append(f"total clean windows {total_windows} != {PUBLIC_SAMPLE_TOTAL_WINDOWS}")

    print("Sample data manifest:")
    for class_name in ["coal", "gangue", "empty"]:
        print(
            f"  {class_name}: {class_events[class_name]} events, "
            f"{class_windows[class_name]} clean windows"
        )
    print(f"  total: {total_events} events, {total_windows} clean windows")

    return problems


def validate_model_reference() -> list[str]:
    problems: list[str] = []
    if not MODEL_REFERENCE.exists():
        return [f"missing architecture reference: {MODEL_REFERENCE.relative_to(REPO_ROOT)}"]

    source = MODEL_REFERENCE.read_text(encoding="utf-8")
    for token in MODEL_REFERENCE_REQUIRED_TOKENS:
        if token not in source:
            problems.append(f"{MODEL_REFERENCE.relative_to(REPO_ROOT)}: missing token {token!r}")
    for token in MODEL_REFERENCE_FORBIDDEN_TOKENS:
        if token in source:
            problems.append(f"{MODEL_REFERENCE.relative_to(REPO_ROOT)}: forbidden training/private token {token!r}")

    print("Architecture reference:")
    print("  model.py present with architecture-only RAAF-BiPAC-Mamba components")
    return problems


def validate_five_seed_artifacts() -> list[str]:
    problems: list[str] = []
    for path in [EVENT_MANIFEST, FIVE_SEED_SPLIT_AUDIT, FIVE_SEED_TEST_PREDICTIONS]:
        if not path.exists():
            problems.append(f"missing audit artifact: {path.relative_to(REPO_ROOT)}")
    if problems:
        return problems

    event_rows, _ = read_csv(EVENT_MANIFEST)
    if len(event_rows) != MANUSCRIPT_TOTAL_EVENTS:
        problems.append(
            f"{EVENT_MANIFEST.relative_to(REPO_ROOT)}: "
            f"row count {len(event_rows)} != {MANUSCRIPT_TOTAL_EVENTS}"
        )
    event_class_counts = defaultdict(int)
    event_windows = defaultdict(int)
    event_s0_s6_rows = defaultdict(int)
    for row in event_rows:
        class_name = row.get("class", "")
        event_class_counts[class_name] += 1
        event_windows[class_name] += int(row.get("clean_windows", "0"))
        event_s0_s6_rows[class_name] += int(row.get("s0_s6_rows", "0"))
    for class_name, expected in MANUSCRIPT_EXPECTED_CLASSES.items():
        if event_class_counts[class_name] != expected["events"]:
            problems.append(
                f"{EVENT_MANIFEST.relative_to(REPO_ROOT)}: "
                f"{class_name} events {event_class_counts[class_name]} != {expected['events']}"
            )
        if event_windows[class_name] != expected["windows"]:
            problems.append(
                f"{EVENT_MANIFEST.relative_to(REPO_ROOT)}: "
                f"{class_name} clean windows {event_windows[class_name]} != {expected['windows']}"
            )
        expected_s0_s6_rows = expected["windows"] * 7
        if event_s0_s6_rows[class_name] != expected_s0_s6_rows:
            problems.append(
                f"{EVENT_MANIFEST.relative_to(REPO_ROOT)}: "
                f"{class_name} S0-S6 rows {event_s0_s6_rows[class_name]} != {expected_s0_s6_rows}"
            )

    split_rows, _ = read_csv(FIVE_SEED_SPLIT_AUDIT)
    if len(split_rows) != 5 * MANUSCRIPT_TOTAL_EVENTS:
        problems.append(
            f"{FIVE_SEED_SPLIT_AUDIT.relative_to(REPO_ROOT)}: "
            f"row count {len(split_rows)} != {5 * MANUSCRIPT_TOTAL_EVENTS}"
        )
    split_by_seed: dict[str, list[dict[str, str]]] = defaultdict(list)
    split_map: dict[tuple[str, str], dict[str, str]] = {}
    for row in split_rows:
        seed = row.get("seed", "")
        event_id = row.get("event_id", "")
        split_by_seed[seed].append(row)
        key = (seed, event_id)
        if key in split_map:
            problems.append(f"{FIVE_SEED_SPLIT_AUDIT.relative_to(REPO_ROOT)}: duplicate key {key}")
        split_map[key] = row
    if set(split_by_seed) != FIVE_SEEDS:
        problems.append(f"{FIVE_SEED_SPLIT_AUDIT.relative_to(REPO_ROOT)}: seeds {sorted(split_by_seed)} != {sorted(FIVE_SEEDS)}")
    for seed in sorted(FIVE_SEEDS):
        rows_for_seed = split_by_seed.get(seed, [])
        if len(rows_for_seed) != MANUSCRIPT_TOTAL_EVENTS:
            problems.append(
                f"{FIVE_SEED_SPLIT_AUDIT.relative_to(REPO_ROOT)}: "
                f"seed {seed} rows {len(rows_for_seed)} != {MANUSCRIPT_TOTAL_EVENTS}"
            )
        split_counts = defaultdict(int)
        for row in rows_for_seed:
            split_counts[row.get("split", "")] += 1
            if row.get("clean_windows") != "18":
                problems.append(f"{FIVE_SEED_SPLIT_AUDIT.relative_to(REPO_ROOT)}: seed {seed} has clean_windows={row.get('clean_windows')}")
            if row.get("s0_s6_rows") != "126":
                problems.append(f"{FIVE_SEED_SPLIT_AUDIT.relative_to(REPO_ROOT)}: seed {seed} has s0_s6_rows={row.get('s0_s6_rows')}")
        expected_split_counts = {"train": 103, "val": 15, "test": 30}
        if dict(split_counts) != expected_split_counts:
            problems.append(
                f"{FIVE_SEED_SPLIT_AUDIT.relative_to(REPO_ROOT)}: "
                f"seed {seed} split counts {dict(split_counts)} != {expected_split_counts}"
            )

    prediction_rows, _ = read_csv(FIVE_SEED_TEST_PREDICTIONS)
    if len(prediction_rows) != 5 * 7 * 30 * 18:
        problems.append(f"{FIVE_SEED_TEST_PREDICTIONS.relative_to(REPO_ROOT)}: row count {len(prediction_rows)} != 18900")
    prediction_counts: dict[tuple[str, str], int] = defaultdict(int)
    window_counts: dict[tuple[str, str, str], int] = defaultdict(int)
    max_probability_sum_error = 0.0
    for row in prediction_rows:
        seed = row.get("seed", "")
        scenario = row.get("scenario", "")
        event_id = row.get("event_id", "")
        window_id = row.get("window_id", "")
        if row.get("model") != "RAAF-BiPAC-Mamba":
            problems.append(f"{FIVE_SEED_TEST_PREDICTIONS.relative_to(REPO_ROOT)}: unexpected model={row.get('model')}")
        if seed not in FIVE_SEEDS:
            problems.append(f"{FIVE_SEED_TEST_PREDICTIONS.relative_to(REPO_ROOT)}: unexpected seed={seed}")
        if scenario not in SCENARIOS:
            problems.append(f"{FIVE_SEED_TEST_PREDICTIONS.relative_to(REPO_ROOT)}: unexpected scenario={scenario}")
        split_row = split_map.get((seed, event_id))
        if split_row is None:
            problems.append(f"{FIVE_SEED_TEST_PREDICTIONS.relative_to(REPO_ROOT)}: prediction without split row {(seed, event_id)}")
        else:
            if split_row.get("split") != "test" or row.get("split") != "test":
                problems.append(f"{FIVE_SEED_TEST_PREDICTIONS.relative_to(REPO_ROOT)}: non-test row {(seed, event_id)}")
            if split_row.get("split_hash") != row.get("split_hash"):
                problems.append(f"{FIVE_SEED_TEST_PREDICTIONS.relative_to(REPO_ROOT)}: split_hash mismatch {(seed, event_id)}")
        probabilities = [
            float(row.get("p_coal", "nan")),
            float(row.get("p_gangue", "nan")),
            float(row.get("p_empty", "nan")),
        ]
        if any((not math.isfinite(value)) or value < -1e-12 or value > 1 + 1e-12 for value in probabilities):
            problems.append(f"{FIVE_SEED_TEST_PREDICTIONS.relative_to(REPO_ROOT)}: probability out of range {(seed, scenario, event_id, window_id)}")
        probability_sum_error = abs(sum(probabilities) - 1.0)
        max_probability_sum_error = max(max_probability_sum_error, probability_sum_error)
        predicted_label = CLASS_LABELS[max(range(3), key=lambda idx: probabilities[idx])]
        if predicted_label != row.get("y_pred_window"):
            problems.append(f"{FIVE_SEED_TEST_PREDICTIONS.relative_to(REPO_ROOT)}: argmax mismatch {(seed, scenario, event_id, window_id)}")
        prediction_counts[(seed, scenario)] += 1
        window_counts[(seed, scenario, event_id)] += 1
    if max_probability_sum_error > 1e-5:
        problems.append(
            f"{FIVE_SEED_TEST_PREDICTIONS.relative_to(REPO_ROOT)}: "
            f"max probability-sum error {max_probability_sum_error} > 1e-5"
        )
    for seed in sorted(FIVE_SEEDS):
        seed_total = sum(count for (count_seed, _scenario), count in prediction_counts.items() if count_seed == seed)
        if seed_total != 7 * 30 * 18:
            problems.append(f"{FIVE_SEED_TEST_PREDICTIONS.relative_to(REPO_ROOT)}: seed {seed} rows {seed_total} != 3780")
        for scenario in sorted(SCENARIOS):
            count = prediction_counts[(seed, scenario)]
            if count != 30 * 18:
                problems.append(f"{FIVE_SEED_TEST_PREDICTIONS.relative_to(REPO_ROOT)}: seed {seed} {scenario} rows {count} != 540")
            events = [event_id for (event_seed, event_scenario, event_id), event_count in window_counts.items() if event_seed == seed and event_scenario == scenario]
            if len(events) != 30:
                problems.append(f"{FIVE_SEED_TEST_PREDICTIONS.relative_to(REPO_ROOT)}: seed {seed} {scenario} events {len(events)} != 30")
            for event_id in events:
                if window_counts[(seed, scenario, event_id)] != 18:
                    problems.append(
                        f"{FIVE_SEED_TEST_PREDICTIONS.relative_to(REPO_ROOT)}: "
                        f"seed {seed} {scenario} {event_id} windows {window_counts[(seed, scenario, event_id)]} != 18"
                    )

    rows_by_seed_scenario: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in prediction_rows:
        rows_by_seed_scenario[(row.get("seed", ""), row.get("scenario", ""))].append(row)
    metric_by_seed_scenario: dict[tuple[str, str], dict[str, float]] = {}
    for seed in sorted(FIVE_SEEDS):
        for scenario in sorted(SCENARIOS):
            _correct, _total, acc, precision, recall, f1 = macro_metrics(
                rows_by_seed_scenario[(seed, scenario)], pred_column="y_pred_window"
            )
            metric_by_seed_scenario[(seed, scenario)] = {
                "acc": acc,
                "precision": precision,
                "recall": recall,
                "f1": f1,
            }

    def display(values: list[float]) -> str:
        return f"{statistics.mean(values):.2f}+/-{statistics.stdev(values):.2f}"

    audit_values: dict[str, str] = {}
    for metric in ["acc", "f1"]:
        per_seed_avg = []
        for seed in sorted(FIVE_SEEDS):
            per_seed_avg.append(
                sum(metric_by_seed_scenario[(seed, scenario)][metric] for scenario in sorted(SCENARIOS))
                / len(SCENARIOS)
            )
        audit_values[f"Avg7_{metric}"] = display(per_seed_avg)
        audit_values[f"S6_{metric}"] = display(
            [metric_by_seed_scenario[(seed, "S6")][metric] for seed in sorted(FIVE_SEEDS)]
        )
    for key, retained_value in RETAINED_TABLE4_HEADLINE.items():
        audit_mean = float(audit_values[key].split("+/-", 1)[0])
        retained_mean = float(retained_value.split("+/-", 1)[0])
        if abs(audit_mean - retained_mean) > 0.03:
            problems.append(
                f"{FIVE_SEED_TEST_PREDICTIONS.relative_to(REPO_ROOT)}: "
                f"{key} audit mean {audit_values[key]} differs from retained Table 4 {retained_value} by >0.03 pp"
            )

    print("Five-seed audit artifacts:")
    print(f"  event manifest: {len(event_rows)} events")
    print(f"  split audit: {len(split_rows)} rows across seeds {', '.join(sorted(FIVE_SEEDS))}")
    print(f"  test predictions: {len(prediction_rows)} rows")
    print(
        "  retained Table 4 headline values: "
        f"Avg7 Acc {RETAINED_TABLE4_HEADLINE['Avg7_acc']}, "
        f"S6 Acc {RETAINED_TABLE4_HEADLINE['S6_acc']}, "
        f"Avg7 F1 {RETAINED_TABLE4_HEADLINE['Avg7_f1']}, "
        f"S6 F1 {RETAINED_TABLE4_HEADLINE['S6_f1']}"
    )
    print(
        "  event-window audit recomputation: "
        f"Avg7 Acc {audit_values.get('Avg7_acc')}, "
        f"S6 Acc {audit_values.get('S6_acc')}, "
        f"Avg7 F1 {audit_values.get('Avg7_f1')}, "
        f"S6 F1 {audit_values.get('S6_f1')}"
    )

    return problems


def macro_metrics(rows: list[dict[str, str]], pred_column: str = "y_pred") -> tuple[int, int, float, float, float, float]:
    correct = sum(1 for row in rows if row.get("y_true") == row.get(pred_column))
    total = len(rows)
    precision_values = []
    recall_values = []
    f1_values = []
    for class_label in CLASS_LABELS:
        tp = sum(1 for row in rows if row.get("y_true") == class_label and row.get(pred_column) == class_label)
        fp = sum(1 for row in rows if row.get("y_true") != class_label and row.get(pred_column) == class_label)
        fn = sum(1 for row in rows if row.get("y_true") == class_label and row.get(pred_column) != class_label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        precision_values.append(precision)
        recall_values.append(recall)
        f1_values.append(f1)
    return (
        correct,
        total,
        100.0 * correct / total,
        100.0 * sum(precision_values) / len(precision_values),
        100.0 * sum(recall_values) / len(recall_values),
        100.0 * sum(f1_values) / len(f1_values),
    )


def validate_supplementary_source_group_artifacts() -> list[str]:
    problems: list[str] = []
    for path in [
        SUPPLEMENTARY_SOURCE_GROUP_PREDICTIONS,
        SUPPLEMENTARY_SOURCE_GROUP_SEED_METRICS,
        SUPPLEMENTARY_SOURCE_GROUP_SUMMARY,
    ]:
        if not path.exists():
            problems.append(f"missing supplementary source-group artifact: {path.relative_to(REPO_ROOT)}")
    if problems:
        return problems

    prediction_rows, fields = read_csv(SUPPLEMENTARY_SOURCE_GROUP_PREDICTIONS)
    expected_fields = ["model", "seed", "sample_id", "source_group_id", "scenario", "y_true", "y_pred"]
    if fields != expected_fields:
        problems.append(f"{SUPPLEMENTARY_SOURCE_GROUP_PREDICTIONS.relative_to(REPO_ROOT)}: fields {fields} != {expected_fields}")
    if len(prediction_rows) != 5 * 7 * 533:
        problems.append(f"{SUPPLEMENTARY_SOURCE_GROUP_PREDICTIONS.relative_to(REPO_ROOT)}: row count {len(prediction_rows)} != 18655")

    keys = set()
    rows_by_seed_scenario: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in prediction_rows:
        if row.get("model") != "RAAF-BiPAC-Mamba":
            problems.append(f"{SUPPLEMENTARY_SOURCE_GROUP_PREDICTIONS.relative_to(REPO_ROOT)}: unexpected model={row.get('model')}")
        seed = row.get("seed", "")
        scenario = row.get("scenario", "")
        if seed not in FIVE_SEEDS:
            problems.append(f"{SUPPLEMENTARY_SOURCE_GROUP_PREDICTIONS.relative_to(REPO_ROOT)}: unexpected seed={seed}")
        if scenario not in SCENARIOS:
            problems.append(f"{SUPPLEMENTARY_SOURCE_GROUP_PREDICTIONS.relative_to(REPO_ROOT)}: unexpected scenario={scenario}")
        if row.get("y_true") not in CLASS_LABELS or row.get("y_pred") not in CLASS_LABELS:
            problems.append(f"{SUPPLEMENTARY_SOURCE_GROUP_PREDICTIONS.relative_to(REPO_ROOT)}: invalid label in row {row}")
        key = (row.get("model"), seed, scenario, row.get("source_group_id"))
        if key in keys:
            problems.append(f"{SUPPLEMENTARY_SOURCE_GROUP_PREDICTIONS.relative_to(REPO_ROOT)}: duplicate key {key}")
        keys.add(key)
        rows_by_seed_scenario[(seed, scenario)].append(row)

    metric_by_seed_scenario: dict[tuple[str, str], dict[str, float]] = {}
    for seed in sorted(FIVE_SEEDS):
        for scenario in sorted(SCENARIOS):
            rows = rows_by_seed_scenario[(seed, scenario)]
            if len(rows) != 533:
                problems.append(
                    f"{SUPPLEMENTARY_SOURCE_GROUP_PREDICTIONS.relative_to(REPO_ROOT)}: "
                    f"seed {seed} {scenario} rows {len(rows)} != 533"
                )
            _correct, _total, acc, precision, recall, f1 = macro_metrics(rows)
            metric_by_seed_scenario[(seed, scenario)] = {
                "acc": acc,
                "precision": precision,
                "recall": recall,
                "f1": f1,
            }

    def display(values: list[float]) -> str:
        return f"{statistics.mean(values):.2f}+/-{statistics.stdev(values):.2f}"

    computed_summary: dict[str, str] = {}
    for metric in ["acc", "precision", "recall", "f1"]:
        for scenario in sorted(SCENARIOS):
            computed_summary[f"{scenario}_{metric}"] = display(
                [metric_by_seed_scenario[(seed, scenario)][metric] for seed in sorted(FIVE_SEEDS)]
            )
        per_seed = []
        for seed in sorted(FIVE_SEEDS):
            per_seed.append(
                sum(metric_by_seed_scenario[(seed, scenario)][metric] for scenario in sorted(SCENARIOS))
                / len(SCENARIOS)
            )
        computed_summary[f"Avg7_{metric}"] = display(per_seed)

    summary_rows, _ = read_csv(SUPPLEMENTARY_SOURCE_GROUP_SUMMARY)
    if len(summary_rows) != 1:
        problems.append(f"{SUPPLEMENTARY_SOURCE_GROUP_SUMMARY.relative_to(REPO_ROOT)}: row count {len(summary_rows)} != 1")
    else:
        summary_row = summary_rows[0]
        for key, expected_value in computed_summary.items():
            if summary_row.get(key) != expected_value:
                problems.append(
                    f"{SUPPLEMENTARY_SOURCE_GROUP_SUMMARY.relative_to(REPO_ROOT)}: "
                    f"{key} {summary_row.get(key)} != {expected_value}"
                )

    print("Supplementary source-group audit artifacts:")
    print(f"  predictions: {len(prediction_rows)} rows, 533 source groups per seed and scenario")
    print(
        "  supplementary recomputation: "
        f"Avg7 Acc {computed_summary.get('Avg7_acc')}, "
        f"S6 Acc {computed_summary.get('S6_acc')}, "
        f"Avg7 F1 {computed_summary.get('Avg7_f1')}, "
        f"S6 F1 {computed_summary.get('S6_f1')}"
    )

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
    problems.extend(validate_model_reference())
    problems.extend(validate_supplementary_source_group_artifacts())
    problems.extend(validate_five_seed_artifacts())
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
