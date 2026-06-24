# Data release scope

## What is public in this package

This package releases a de-identified public clean-event sample and reproducibility artifacts:

- 148 representative clean controlled-platform event files.
- Event-level file manifest with row counts, channels, window settings, and SHA-256 hashes.
- Event-disjoint split audit files.
- Model and reconstruction configuration notes.
- Released prediction CSVs, seed-level metric CSVs, summary tables, validation reports, and statistical-control artifacts.
- Standard-library scripts for checking the sample data, exporting splits, and recomputing event-level metrics.

The clean public sample closes exactly to the manuscript clean-event counts:

| Class | Events | Windows/event | Clean windows |
|---|---:|---:|---:|
| coal | 49 | 18 | 882 |
| gangue | 57 | 18 | 1026 |
| empty | 42 | 18 | 756 |
| total | 148 | 18 | 2664 |

## What remains restricted

The following materials are not publicly released:

- Complete proprietary field observations.
- Full raw equipment-noise recordings.
- Full raw validation dataset and any enterprise-confidential records.
- Private training infrastructure and checkpoints that are not approved for release.

The released sample data are sufficient to verify data format, class labels, two-channel layout, window construction, split format, and metric-reconstruction logic. They are not the complete raw dataset used for all reported experiments. A model trained only on the public clean-event sample is not expected to reproduce the manuscript's S0-S6 results, because the restricted raw equipment-noise recordings and full raw experimental dataset are not included.

## Suggested manuscript wording

Use this after the final GitHub URL is created:

```text
A public reproducibility package containing de-identified clean-event sample files, data manifests, split indices, model/training configurations, analysis scripts, seed-level prediction/metric CSVs, and validation reports is available at https://github.com/ww1282949132-design/jvc-raaf-bipac-mamba-repro. The released clean-event files match the clean-event class counts and window construction reported in the manuscript, but they are not the complete raw S0-S6 experimental dataset. The complete proprietary field observations, equipment-noise recordings, and full raw validation dataset are not publicly available because of legal/commercial restrictions and project confidentiality requirements. The public sample data are provided to demonstrate file format, class labels, windowing, split logic, and metric reconstruction; the reported metrics should be verified from the released prediction and metric CSVs rather than by retraining only on the public clean-event sample. Additional restricted materials may be requested from the corresponding author subject to institutional and enterprise approval.
```

## Suggested response-letter wording

```text
We have added a public reproducibility package. Because the full field database and raw equipment-noise recordings are subject to institutional and enterprise restrictions, we cannot publicly release the complete raw dataset. Instead, the repository provides a de-identified clean-event sample matching the reported clean-event class counts and window construction, event/data manifests, split-audit files, model/training configuration notes, prediction and metric CSVs, validation reports, and scripts for reconstructing the window index, event splits, and reported event-level metrics. We have clarified that training only on the public clean-event sample is a different experiment and is not intended to reproduce the complete S0-S6 manuscript tables. This release allows readers to inspect the data structure, verify the event-disjoint split logic, and recompute the reported metrics while respecting the data-sharing constraints.
```
