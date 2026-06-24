# Reproducibility map

This file maps common reviewer concerns to the released repository contents.

| Reviewer concern | Released evidence |
|---|---|
| What do the raw input files look like? | `data_sample/clean_events/coal`, `data_sample/clean_events/gangue`, `data_sample/clean_events/empty` |
| Are the clean event counts consistent with the manuscript? | `metadata/sample_data_manifest.csv`, `scripts/validate_package.py` |
| How are windows constructed? | `configs/reproduction_config.json`, `scripts/make_windows.py` |
| Are event IDs and splits auditable? | `metadata/event_split_audit_10seeds.csv`, `scripts/export_splits.py` |
| Can event-level metrics be recomputed from predictions? | `results/primary_event_level/event_predictions_10seeds_v2.csv`, `scripts/compute_event_metrics.py` |
| Are baseline and control configurations documented? | `results/baseline_and_controls/T7_fair_baseline_config_table.csv`, `results/baseline_and_controls/T7_fair_baseline_profile_table.csv` |
| Are PAC controls available? | `results/baseline_and_controls/T8_pac_control_*` |
| Are empty-class controls available? | `results/baseline_and_controls/T9_empty_rule_*` |
| Are roughness thresholds and sensitivity artifacts available? | `results/roughness_and_thresholds/T10_*` |
| Are statistical tests and class-level diagnostics available? | `results/statistics_and_confusion/T11_*` |
| Is stricter group/LONSO evidence available? | `results/statistics_and_confusion/T12_group_lonso_s6_*` |
| Is raw noise overlay fully reproducible? | Formula and config are released in `scripts/noise_overlay_reference.py`; full raw equipment-noise recordings are restricted. |
| Can the full manuscript be retrained from only the public sample files? | No. Training only on `data_sample/clean_events/` is a different experiment because the full raw S0-S6 dataset and raw equipment-noise recordings are restricted. |

## Minimal reviewer workflow

1. Run `python scripts/validate_package.py` to verify the released clean-event sample.
2. Run `python scripts/make_windows.py --check-only` to verify the window rule.
3. Run `python scripts/export_splits.py` to inspect the event split files.
4. Recompute metrics from the released prediction CSVs with `scripts/compute_event_metrics.py`.
5. Compare recomputed outputs in `outputs/` with the released summary and validation reports.

Do not compare manuscript metrics against a new training run performed only on `data_sample/clean_events/`. That would omit the restricted noisy scenarios and therefore would not match the manuscript protocol.

