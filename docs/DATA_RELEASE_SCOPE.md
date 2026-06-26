# Data release scope

## What is public in this package

This package releases a de-identified representative public clean-event subset and reproducibility artifacts:

- 37 de-identified real measured clean controlled-platform event files, corresponding to approximately one quarter of the manuscript clean-event set.
- Event-level file manifest with row counts, channels, window settings, and SHA-256 hashes.
- Event-disjoint split audit files.
- Architecture-only PyTorch model definition in `model.py`.
- Model and reconstruction configuration notes.
- Released event-window prediction CSVs, supplementary source-group prediction CSVs, event-level prediction CSVs, seed-level metric CSVs, summary tables, validation reports, and statistical-control artifacts.
- Standard-library scripts for checking the sample data, exporting splits, and recomputing event-level metrics.

The clean public subset contains:

| Class | Events | Windows/event | Clean windows |
|---|---:|---:|---:|
| coal | 12 | 18 | 216 |
| gangue | 14 | 18 | 252 |
| empty | 11 | 18 | 198 |
| total | 37 | 18 | 666 |

## What remains restricted

The following materials are not publicly released:

- Complete proprietary field observations.
- Full raw equipment-noise recordings.
- Full raw validation dataset and any enterprise-confidential records.
- Full private training infrastructure, runnable training pipeline, private trained models, and checkpoints that are not approved for release.

The released clean-event subset is sufficient to verify data format, class labels, two-channel layout, window construction, split format, and metric-reconstruction logic on representative real measured files. The architecture-only `model.py` file supports inspection of the model structure described in the manuscript, but it is not a complete training pipeline and does not include private checkpoints. The retained primary Table 4 RAAF window-level protocol is audited from the released event-window probability export, while event-level metrics are checked from released event-level prediction files. The released source-group files are supplementary consistency audits rather than the Table 4 denominator. The clean-event files are not the complete raw dataset used for all reported experiments. Retraining only from the public clean-event subset is outside the manuscript protocol, because the restricted raw equipment-noise recordings and full raw experimental dataset are not included.

## Suggested manuscript wording

Use this after the final GitHub URL is created:

```text
A public reproducibility package containing a de-identified representative subset of real measured clean-event files, data manifests, split indices, an architecture-only PyTorch model definition (`model.py`), model/training configurations, analysis scripts, event-window prediction CSVs, supplementary source-group audit CSVs, event-level prediction/metric CSVs, and validation reports is available at https://github.com/ww1282949132-design/jvc-raaf-bipac-mamba-repro. The released clean-event files preserve the class labels, two-channel format and window construction reported in the manuscript, but they are a representative subset rather than the complete clean-event set or the complete raw S0-S6 experimental dataset. The complete proprietary field observations, equipment-noise recordings, full raw validation dataset, full internal training pipeline and checkpoints are not publicly available because of legal/commercial restrictions and project confidentiality requirements. The released clean-event subset provides file format, class labels, windowing, split logic, and metric-reconstruction evidence; the reported metrics should be verified from the released prediction, metric, and audit CSVs rather than by retraining only from the public clean-event subset. Additional restricted materials may be requested from the corresponding author subject to institutional and enterprise approval.
```

## Suggested response-letter wording

```text
We have added a public reproducibility package. Because the full field database and raw equipment-noise recordings are subject to institutional and enterprise restrictions, we cannot publicly release the complete raw dataset or the private training pipeline/checkpoints. Instead, the repository provides a de-identified representative subset of real measured clean-event files preserving the reported class labels, two-channel format and window construction, event/data manifests, split-audit files, an architecture-only PyTorch model definition (`model.py`), model/training configuration notes, the retained event-window probability export for the primary window-level table audit, supplementary source-group audit CSVs, event-level prediction and metric CSVs, validation reports, and scripts for reconstructing the window index, event splits, and reported metrics. The noise-overlay formula and configuration are provided for audit, while the raw equipment-noise recordings themselves remain restricted. We have clarified that retraining only from the public clean-event subset is outside the manuscript protocol and is not intended to reproduce the complete S0-S6 manuscript tables. This release allows readers to inspect representative data structure and model architecture, verify the event-disjoint split logic, and recompute the reported metrics while respecting the data-sharing constraints.
```
