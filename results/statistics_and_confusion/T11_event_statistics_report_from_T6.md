# T11 Event-Level Statistical Evidence From Released Prediction Tables

This report summarizes the event-level paired statistical evidence derived from the released prediction table:

- `results/baseline_and_controls/event_predictions_9models_10seeds_complete.csv`

The companion machine-readable outputs are:

- `results/statistics_and_confusion/T11_pairwise_event_tests_from_T6.csv`
- `results/statistics_and_confusion/T11_per_class_recall_bootstrap_from_T6.csv`

## Key Paired Event-Accuracy Tests

| Comparison | Scope | Ours (%) | Baseline (%) | Diff (pp) | Paired bootstrap 95% CI (pp) | McNemar b/c | Exact p | n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| RAAF-BiPAC-Mamba vs HMBCNN-style | Avg7 | 93.43 | 87.29 | 6.14 | [4.38, 7.90] | 252/123 | <1e-6 | 2100 |
| RAAF-BiPAC-Mamba vs HMBCNN-style | S6 | 90.33 | 83.00 | 7.33 | [2.00, 12.67] | 46/24 | 0.0115 | 300 |
| RAAF-BiPAC-Mamba vs Plain Mamba | Avg7 | 93.43 | 88.19 | 5.24 | [3.62, 6.86] | 222/112 | <1e-6 | 2100 |
| RAAF-BiPAC-Mamba vs Plain Mamba | S6 | 90.33 | 83.67 | 6.67 | [1.33, 12.00] | 44/24 | 0.0205 | 300 |
| RAAF-BiPAC-Mamba vs Bi-Mamba | Avg7 | 93.43 | 89.71 | 3.71 | [2.10, 5.33] | 200/122 | 1.63e-05 | 2100 |
| RAAF-BiPAC-Mamba vs Bi-Mamba | S6 | 90.33 | 86.33 | 4.00 | [-0.67, 8.68] | 34/22 | 0.141 | 300 |

## Proposed-Model S6 Event-Level Per-Class Recall

| Class | Support events | Recall (%) | Stratified bootstrap 95% CI (%) |
|---|---:|---:|---:|
| coal | 100 | 88.00 | [82.00, 94.00] |
| gangue | 110 | 87.27 | [80.91, 92.73] |
| empty | 90 | 96.67 | [93.33, 100.00] |

## Integrity Checks

| Check | Requirement | Result |
|---|---|---|
| Row count | 9 models x 10 seeds x 7 scenarios x 30 events | 18900 rows |
| Unique prediction keys | No duplicated model-seed-scenario-event keys | 0 duplicates |
| Model set | Nine model variants present | Passed |
| Seed set | Seeds 42-51 present | Passed |
| Scenario set | S0-S6 present | Passed |
| Per-group event count | 30 events per model-seed-scenario group | Passed |
| Per-class event count | Coal/gangue/empty counts match the released split audit | Passed |
| Probability values | Finite values within [0, 1] | Passed |
| Probability closure | Maximum sum error approximately zero | 1.00000230319e-10 |
| Argmax consistency | Predicted label matches maximum class probability | 0 mismatches |
| Paired event sets | All compared models share the same seed-scenario-event keys | Passed |

## Statistical Methods

- Accuracy and macro-F1 paired differences use stratified event bootstrap with `B=5000`.
- Avg7 bootstrap strata are seed, scenario and class.
- S6 bootstrap strata are seed and class.
- McNemar tests use paired predictions from the same seed, scenario and event ID.
- Exact binomial McNemar p-values are reported for discordant event pairs.

## Interpretation

RAAF-BiPAC-Mamba improves over HMBCNN-style, Plain Mamba and Bi-Mamba on Avg7 and S6 event accuracy. The strongest baseline comparison is Bi-Mamba: the proposed model improves Avg7 event accuracy by 3.71 pp with a 95% paired-bootstrap CI of [2.10, 5.33], while the S6 improvement is 4.00 pp with a wider CI of [-0.67, 8.68] and McNemar p=0.141. The S6 result is therefore reported as a directional event-level gain rather than a conventionally significant paired-test result.

The S6 class-level recall profile shows that coal and gangue are more difficult than the empty class under severe mixed noise, which is consistent with the coal-gangue confusion pattern reported in the manuscript.

## Released File Hashes

- `results/baseline_and_controls/event_predictions_9models_10seeds_complete.csv`: `9bc3a38c79a0c4ec57a638a8dfd1be7a8ea9051cf0034e810a477daaf60c0a69`
- `results/statistics_and_confusion/T11_pairwise_event_tests_from_T6.csv`: `345bc790a16d9aae3719a6e2f28dc6d6e4df8e19cb763e89f8185e03d454df4c`
- `results/statistics_and_confusion/T11_per_class_recall_bootstrap_from_T6.csv`: `ff3410ed0431a3d6a856aefba7392e62936dbd8e2c65a0edae7e0369e406a256`
