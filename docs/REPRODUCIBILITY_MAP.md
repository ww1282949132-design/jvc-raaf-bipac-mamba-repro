# Reproducibility map

This file maps common reviewer concerns to the released repository contents.

| Reviewer concern | Released evidence |
|---|---|
| What do the raw input files look like? | `data_sample/clean_events/coal`, `data_sample/clean_events/gangue`, `data_sample/clean_events/empty` |
| Is the public clean-event subset internally consistent? | `metadata/sample_data_manifest.csv`, `scripts/validate_package.py` |
| Where are the full manuscript clean-event counts documented? | `metadata/event_manifest.csv`, `metadata/event_split_audit_10seeds.csv`, `metadata/physical_event_split_audit_5seeds.csv` |
| How are windows constructed? | `configs/reproduction_config.json`, `scripts/make_windows.py` |
| Are event IDs and splits auditable? | `metadata/event_split_audit_10seeds.csv`, `metadata/physical_event_split_audit_5seeds.csv`, `scripts/export_splits.py` |
| Can the primary Table 4 RAAF window-level protocol be audited? | `results/primary_event_level/test_predictions_5seeds.csv`, `metadata/physical_event_split_audit_5seeds.csv`, `scripts/validate_package.py` |
| Can event-level metrics be recomputed from predictions? | `results/primary_event_level/event_predictions_10seeds_v2.csv`, `scripts/compute_event_metrics.py` |
| What are the source-group files in `results/primary_window_level/` for? | They provide a supplementary 533-source-group audit for RAAF-BiPAC-Mamba. They are not the primary Table 4 denominator. |
| Is model code available for architecture inspection? | Yes. `model.py` provides an architecture-only PyTorch reference for the dual-stream stems, bidirectional Mamba blocks, cross-modal attention, RAAF fusion, PAC helpers, GRL layer, material classifier, and noise-scenario discriminator. It excludes data loading, training loops, private checkpoints, and private environment settings. |
| Are baseline and control configurations documented? | `results/baseline_and_controls/T7_fair_baseline_config_table.csv`, `results/baseline_and_controls/T7_fair_baseline_profile_table.csv` |
| Are PAC controls available? | `results/baseline_and_controls/T8_pac_control_*` |
| Are empty-class controls available? | `results/baseline_and_controls/T9_empty_rule_*` |
| Are roughness thresholds and sensitivity artifacts available? | `results/roughness_and_thresholds/T10_*` |
| Are statistical tests and class-level diagnostics available? | `results/statistics_and_confusion/T11_*` |
| Is stricter group/LONSO evidence available? | `results/statistics_and_confusion/T12_group_lonso_s6_*` |
| Can raw noise overlay be reconstructed from this release alone? | No. The formula and config are released in `scripts/noise_overlay_reference.py` and `configs/reproduction_config.json`, and the manuscript reports the temporal partition and SNR/checksum audit. However, the full raw equipment-noise recordings are restricted, so the public package cannot recreate S0-S6 noisy scenarios from raw files. |
| Can the full manuscript be retrained from only the public clean-event files? | No. Retraining only from `data_sample/clean_events/` is outside the manuscript protocol because the full raw S0-S6 dataset and raw equipment-noise recordings are restricted. |

## Minimal reviewer workflow

1. Run `python scripts/validate_package.py` to verify the released clean-event subset.
2. Run `python scripts/make_windows.py --check-only` to verify the window rule.
3. Run `python scripts/export_splits.py` to inspect the event split files.
4. Inspect `model.py` for the architecture-only model definition and `scripts/noise_overlay_reference.py` for the SNR overlay formula.
5. Check the retained Table 4 event-window audit and supplementary source-group audit with `scripts/validate_package.py`.
6. Recompute event-level metrics from the released prediction CSVs with `scripts/compute_event_metrics.py`.
7. Compare recomputed outputs in `outputs/` with the released summary and validation reports.

Do not compare manuscript metrics against a new training run performed only on `data_sample/clean_events/`. That would use only the representative clean subset and omit the restricted noisy scenarios, so it would be outside the manuscript protocol.
