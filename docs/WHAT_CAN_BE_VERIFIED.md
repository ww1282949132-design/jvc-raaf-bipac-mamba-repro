# What can and cannot be verified from this release

This note prevents a common misunderstanding: this repository is a public reproducibility package, not a complete raw training-data release.

## Can be verified directly

The following checks can be run directly from this repository:

- The public clean-event sample has 148 files: 49 coal, 57 gangue, and 42 empty.
- Each public event file has 20000 rows and 2 channels.
- The released window rule, 2048 samples with a 1024-sample step, gives 18 clean windows per event.
- The public clean-event sample closes to 2664 clean windows.
- The event split audit can be exported by seed.
- Event-level metrics and confusion matrices can be recomputed from the released prediction CSVs.
- The released validation reports can be inspected for row counts, probability checks, split checks, and group-overlap checks.

## Cannot be verified from public raw files alone

The following checks are outside the scope of the public raw-file release:

- Reconstructing all S0-S6 raw noisy scenarios from raw clean and raw equipment-noise files.
- Retraining the full RAAF-BiPAC-Mamba model from scratch under the original internal training environment.
- Rebuilding private checkpoints.
- Reproducing all manuscript tables by training only on `data_sample/clean_events/`.

These are restricted because the complete field database, raw equipment-noise recordings, and internal training infrastructure cannot currently be publicly released.

## Correct comparison logic

Use the public clean-event files to check data format, class labels, channel layout, file integrity, and window construction.

Use the released prediction CSVs, metric CSVs, validation reports, and scripts to check the reported event-level metrics.

Do not treat a training run on `data_sample/clean_events/` as the manuscript experiment. It would be missing the restricted noisy scenarios and would therefore be expected to differ from the paper.

