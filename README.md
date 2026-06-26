# RAAF-BiPAC-Mamba reproducibility package

This repository provides a public, de-identified reproducibility package for the manuscript on roughness-guided acoustic-vibration coal-gangue recognition with RAAF-BiPAC-Mamba.

The package is designed for peer-review inspection and metric reconstruction. It contains a public representative clean-event subset, manifests, split audits, an architecture-only PyTorch model definition, configuration files, prediction tables, summary tables, validation reports, and lightweight scripts. It does not contain the complete proprietary field database or the full raw equipment-noise recordings.

## Important scope statement

This repository is not a complete raw training-data release. The public event files are a de-identified representative one-quarter subset of the real measured clean-event files. They preserve the same two-channel format and window-construction rule reported in the manuscript, but they do not include all clean events and are not the full raw S0-S6 experimental dataset. In particular, the restricted raw equipment-noise recordings needed to reconstruct all noisy scenarios from raw files are not included.

Therefore, retraining only from `data_sample/clean_events/` is outside the manuscript protocol and should not be used as the check for the manuscript tables. The manuscript metrics should be checked by using the released split files, prediction CSVs, summary CSVs, validation reports, and metric-reconstruction scripts in this repository. The retained primary Table 4 window-level audit uses `results/primary_event_level/test_predictions_5seeds.csv`, where each seed-scenario pair contains 540 event-window predictions. The `results/primary_window_level/` source-group files are retained as a supplementary source-group audit and are not the Table 4 denominator.

## Public scope

Included:

- `data_sample/clean_events/`: 37 public clean-event files forming a representative one-quarter subset of the manuscript clean-event set.
- `metadata/sample_data_manifest.csv`: file-level manifest with row counts, channel counts, window settings, and SHA-256 checksums.
- `metadata/event_split_audit_10seeds.csv`: event-disjoint split audit used by the released prediction tables.
- `results/primary_event_level/test_predictions_5seeds.csv`: retained five-seed event-window probability export used for the primary Table 4 window-level audit.
- `results/primary_window_level/group_disjoint_predictions_raaf_5seeds.csv`: supplementary five-seed source-group audit file with 533 source groups per seed-scenario pair.
- `model.py`: architecture-only PyTorch reference implementation of RAAF-BiPAC-Mamba. It defines the dual-stream convolutional stems, bidirectional Mamba blocks, cross-modal attention, RAAF fusion, PAC helpers, GRL layer, material classifier, and noise-scenario discriminator. It does not include a data loader, training loop, checkpoint loading, dataset paths, normalization statistics, or private run metadata.
- `configs/`: reconstruction and training-configuration notes.
- `results/`: released seed-level predictions, metrics, baseline/control tables, roughness/threshold artifacts, and validation reports.
- `scripts/`: standard-library scripts for checking the package, rebuilding window indexes, exporting splits, and recomputing event-level metrics.

Restricted:

- The complete raw field observations.
- Full raw equipment-noise recordings.
- Full raw validation dataset and any enterprise-confidential database records.
- Full internal training infrastructure, runnable training pipeline, private trained models, and checkpoints that cannot be released under current institutional and enterprise restrictions.

The released clean-event files are real measured two-channel records provided with file integrity, class labels, channel layout, windowing rule, split logic, and metric-reconstruction evidence. They should not be interpreted as the complete clean-event set or the complete raw dataset used for every reported experiment.

See `docs/WHAT_CAN_BE_VERIFIED.md` before comparing repository outputs with manuscript results.

## Sample data closure

The clean public sample contains:

| Class | Event files | Windows per event | Clean windows |
|---|---:|---:|---:|
| coal | 12 | 18 | 216 |
| gangue | 14 | 18 | 252 |
| empty | 11 | 18 | 198 |
| total | 37 | 18 | 666 |

Each event file contains 20000 rows and 2 channels. The released windowing rule is:

- window length: 2048 samples
- step size: 1024 samples
- clean windows per event: `floor((20000 - 2048) / 1024) + 1 = 18`

## Directory guide

```text
configs/
data_sample/clean_events/
docs/
metadata/
model.py
results/
scripts/
```

Important files:

- `docs/DATA_RELEASE_SCOPE.md`: what can and cannot be made public, plus manuscript-ready wording.
- `docs/REPRODUCIBILITY_MAP.md`: maps reviewer-facing concerns to released files.
- `docs/WHAT_CAN_BE_VERIFIED.md`: explains which checks reproduce manuscript evidence and which checks are outside the public-release scope.
- `model.py`: architecture-only PyTorch model definition; optional `torch` and `mamba_ssm` are required only if a reader wants to instantiate the model. The package validator checks this file statically and does not import PyTorch.
- `scripts/validate_package.py`: package-level self-check.
- `scripts/make_windows.py`: checks event files and optionally exports a window index.
- `scripts/export_splits.py`: exports per-seed event splits.
- `scripts/compute_event_metrics.py`: recomputes event-level accuracy, macro precision, macro recall, macro F1, and confusion matrices from prediction CSVs.
- `scripts/noise_overlay_reference.py`: reference formula for SNR-based noise overlay; raw noise files are not included.
- `results/primary_event_level/test_predictions_5seeds.csv`: five-seed event-window probability audit for the retained primary Table 4 protocol.
- `results/primary_window_level/group_disjoint_predictions_raaf_5seeds.csv` and `results/primary_window_level/group_disjoint_summary_raaf_5seeds.csv`: supplementary source-group predictions and recomputed summary for RAAF-BiPAC-Mamba. These files are not the Table 4 denominator.

## Quick checks

Run from the repository root:

```bash
python scripts/validate_package.py
python scripts/make_windows.py --check-only
python scripts/export_splits.py
python scripts/compute_event_metrics.py results/primary_event_level/event_predictions_10seeds_v2.csv --group-cols model,scenario --out-dir outputs/metrics_primary
python scripts/compute_event_metrics.py results/statistics_and_confusion/T12_group_lonso_s6_primary_model_predictions.csv --group-cols protocol,model,held_out --out-dir outputs/metrics_group_lonso_s6
```

The scripts use only the Python standard library and read text files with UTF-8 BOM support.

The first command verifies the public clean-event subset, the architecture-only model reference, the retained five-seed Table 4 event-window audit, and the supplementary source-group audit. The metric commands verify the released event-level prediction CSVs. The public clean-event subset alone is not intended to retrain the full RAAF-BiPAC-Mamba model or regenerate all S0-S6 manuscript tables from raw data.

## Data availability statement

After the public repository is uploaded, insert the final repository URL into the manuscript. A suggested statement is provided in `docs/DATA_RELEASE_SCOPE.md`.

## Repository URL

https://github.com/ww1282949132-design/jvc-raaf-bipac-mamba-repro
