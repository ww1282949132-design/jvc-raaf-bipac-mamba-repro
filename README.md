# RAAF-BiPAC-Mamba reproducibility package

This repository provides a public, de-identified reproducibility package for the manuscript on roughness-guided acoustic-vibration coal-gangue recognition with RAAF-BiPAC-Mamba.

The package is designed for peer-review inspection and metric reconstruction. It contains public clean-event sample files, manifests, split audits, configuration files, prediction tables, summary tables, validation reports, and lightweight scripts. It does not contain the complete proprietary field database or the full raw equipment-noise recordings.

## Important scope statement

This repository is not a complete raw training-data release. The public event files match the clean-event class counts and window-construction rule reported in the manuscript, but they are not the full raw S0-S6 experimental dataset. In particular, the restricted raw equipment-noise recordings needed to reconstruct all noisy scenarios from raw files are not included.

Therefore, training a new model only on `data_sample/clean_events/` is a different experiment and should not be expected to reproduce the manuscript tables. The manuscript metrics should be checked by using the released split files, prediction CSVs, summary CSVs, validation reports, and metric-reconstruction scripts in this repository.

## Public scope

Included:

- `data_sample/clean_events/`: 148 public clean-event files matching the reported clean-event class counts and window construction.
- `metadata/sample_data_manifest.csv`: file-level manifest with row counts, channel counts, window settings, and SHA-256 checksums.
- `metadata/event_split_audit_10seeds.csv`: event-disjoint split audit used by the released prediction tables.
- `configs/`: reconstruction and training-configuration notes.
- `results/`: released seed-level predictions, metrics, baseline/control tables, roughness/threshold artifacts, and validation reports.
- `scripts/`: standard-library scripts for checking the package, rebuilding window indexes, exporting splits, and recomputing event-level metrics.

Restricted:

- The complete raw field observations.
- Full raw equipment-noise recordings.
- Full raw validation dataset and any enterprise-confidential database records.
- Internal training infrastructure and private checkpoints that cannot be released under current institutional and enterprise restrictions.

The public sample data demonstrate the file format, class labels, channel layout, windowing rule, split logic, and metric-reconstruction workflow. They should not be interpreted as the complete raw dataset used for every reported experiment.

See `docs/WHAT_CAN_BE_VERIFIED.md` before comparing repository outputs with manuscript results.

## Sample data closure

The clean public sample contains:

| Class | Event files | Windows per event | Clean windows |
|---|---:|---:|---:|
| coal | 49 | 18 | 882 |
| gangue | 57 | 18 | 1026 |
| empty | 42 | 18 | 756 |
| total | 148 | 18 | 2664 |

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
results/
scripts/
```

Important files:

- `docs/DATA_RELEASE_SCOPE.md`: what can and cannot be made public, plus manuscript-ready wording.
- `docs/REPRODUCIBILITY_MAP.md`: maps reviewer-facing concerns to released files.
- `docs/WHAT_CAN_BE_VERIFIED.md`: explains which checks reproduce manuscript evidence and which checks are outside the public-release scope.
- `scripts/validate_package.py`: package-level self-check.
- `scripts/make_windows.py`: checks event files and optionally exports a window index.
- `scripts/export_splits.py`: exports per-seed event splits.
- `scripts/compute_event_metrics.py`: recomputes event-level accuracy, macro precision, macro recall, macro F1, and confusion matrices from prediction CSVs.
- `scripts/noise_overlay_reference.py`: reference formula for SNR-based noise overlay; raw noise files are not included.

## Quick checks

Run from the repository root:

```bash
python scripts/validate_package.py
python scripts/make_windows.py --check-only
python scripts/export_splits.py
python scripts/compute_event_metrics.py results/primary_event_level/event_predictions_10seeds_v2.csv --group-cols model,scenario --out-dir outputs/metrics_primary
python scripts/compute_event_metrics.py results/statistics_and_confusion/T12_group_lonso_s6_primary_model_predictions.csv --group-cols protocol,model,held_out --out-dir outputs/metrics_group_lonso_s6
```

The scripts use only the Python standard library.

The first two commands verify the public clean-event sample. The metric commands verify the released prediction CSVs. The public clean-event sample alone is not intended to retrain the full RAAF-BiPAC-Mamba model or regenerate all S0-S6 manuscript tables from raw data.

## Data availability statement

After the public repository is uploaded, insert the final repository URL into the manuscript. A suggested statement is provided in `docs/DATA_RELEASE_SCOPE.md`.

## Repository URL

https://github.com/ww1282949132-design/jvc-raaf-bipac-mamba-repro
