# What can and cannot be verified from this release

This note prevents a common misunderstanding: this repository is a public reproducibility package, not a complete raw training-data release.

## Can be verified directly

The following checks can be run directly from this repository:

- The public clean-event subset has 37 files: 12 coal, 14 gangue, and 11 empty.
- Each public event file has 20000 rows and 2 channels.
- The released window rule, 2048 samples with a 1024-sample step, gives 18 clean windows per event.
- The public clean-event subset closes to 666 clean windows.
- The event split audit can be exported by seed.
- The architecture of RAAF-BiPAC-Mamba can be inspected from `model.py`, including the convolutional stems, bidirectional Mamba blocks, cross-modal attention, RAAF fusion, PAC helpers, GRL layer, material classifier, and noise-scenario discriminator.
- The SNR-based noise-overlay formula and configuration can be inspected from `scripts/noise_overlay_reference.py` and `configs/reproduction_config.json`.
- The retained primary Table 4 RAAF window-level protocol can be audited from `results/primary_event_level/test_predictions_5seeds.csv`, using event-window predictions as the unit and 540 test windows per seed-scenario pair.
- Event-level metrics and confusion matrices can be recomputed from the released prediction CSVs.
- The released validation reports can be inspected for row counts, probability checks, split checks, and group-overlap checks. The 533-source-group files in `results/primary_window_level/` are supplementary source-group audits, not the primary Table 4 denominator.

## Cannot be verified from public raw files alone

The following checks are outside the scope of the public raw-file release:

- Reconstructing all S0-S6 raw noisy scenarios from raw clean and raw equipment-noise files.
- Retraining the full RAAF-BiPAC-Mamba model from scratch under the original internal training environment.
- Running the private training pipeline or reproducing private checkpoint files.
- Rebuilding private checkpoints.
- Reproducing all manuscript tables by training only on the representative subset in `data_sample/clean_events/`.

These are restricted because the complete field database, raw equipment-noise recordings, full internal training pipeline, trained models, and checkpoints cannot currently be publicly released.

## Correct comparison logic

Use the public clean-event subset to check data format, class labels, channel layout, file integrity, and window construction.

Use `model.py` to inspect the architecture described in the manuscript. Do not treat it as a complete runnable training release; it intentionally omits data loading, training loops, private checkpoints, and private environment settings.

Use `results/primary_event_level/test_predictions_5seeds.csv` to audit the retained primary Table 4 RAAF window-level protocol. Use `results/primary_window_level/group_disjoint_predictions_raaf_5seeds.csv` only as a supplementary source-group consistency audit. Use the released event-level prediction CSVs, metric CSVs, validation reports, and scripts to check the reported event-level metrics.

Do not treat a training run on `data_sample/clean_events/` as the manuscript protocol. It would be based only on a representative clean subset and would be missing the restricted noisy scenarios, so it would be outside the reported experimental setting.
