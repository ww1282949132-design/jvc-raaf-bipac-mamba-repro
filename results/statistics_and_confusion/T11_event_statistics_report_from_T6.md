# T11 Event-Level Statistical Evidence From Frozen T6 Predictions

Source: `D:/shiyan/tougao/t6_complete_math_results_package/event_predictions_9models_10seeds_complete.csv`.
No training, inference, or manuscript TeX edit was performed in this step.

## 1. Target paper table

### Key paired event-accuracy tests for main-text reporting

| Comparison | Scope | Ours (%) | Baseline (%) | Diff (pp) | Paired bootstrap 95% CI (pp) | McNemar b/c | Exact p | n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| RAAF-BiPAC-Mamba vs HMBCNN-style | Avg7 | 93.43 | 87.29 | 6.14 | [4.38, 7.90] | 252/123 | <1e-6 | 2100 |
| RAAF-BiPAC-Mamba vs HMBCNN-style | S6 | 90.33 | 83.00 | 7.33 | [2.00, 12.67] | 46/24 | 0.0115 | 300 |
| RAAF-BiPAC-Mamba vs Plain Mamba | Avg7 | 93.43 | 88.19 | 5.24 | [3.62, 6.86] | 222/112 | <1e-6 | 2100 |
| RAAF-BiPAC-Mamba vs Plain Mamba | S6 | 90.33 | 83.67 | 6.67 | [1.33, 12.00] | 44/24 | 0.0205 | 300 |
| RAAF-BiPAC-Mamba vs Bi-Mamba | Avg7 | 93.43 | 89.71 | 3.71 | [2.10, 5.33] | 200/122 | 1.63e-05 | 2100 |
| RAAF-BiPAC-Mamba vs Bi-Mamba | S6 | 90.33 | 86.33 | 4.00 | [-0.67, 8.68] | 34/22 | 0.141 | 300 |

### Proposed-model S6 event-level per-class recall

| Class | Support events | Recall (%) | Stratified bootstrap 95% CI (%) |
|---|---:|---:|---:|
| coal | 100 | 88.00 | [82.00, 94.00] |
| gangue | 110 | 87.27 | [80.91, 92.73] |
| empty | 90 | 96.67 | [93.33, 100.00] |

Full machine-readable tables are saved as:
- `D:\shiyan\tougao\t11_event_statistics_from_t6\T11_pairwise_event_tests_from_T6.csv`
- `D:\shiyan\tougao\t11_event_statistics_from_t6\T11_per_class_recall_bootstrap_from_T6.csv`

## 2. 表内大小逻辑关系

| 层级 | 检查项 | 必须满足的公式或条件 | 当前数据代入 | 结果 | 失败后的最小处理 |
|---|---|---|---|---|---|
| 结构/主键/值域 | row_count_formula | 见 T6 L2 预测文件定义 | 18900 vs 9*10*7*30=18900 | 通过 | 无需处理 |
| 结构/主键/值域 | duplicate_model_seed_scenario_event_id | 见 T6 L2 预测文件定义 | 0 | 通过 | 无需处理 |
| 结构/主键/值域 | model_count | 见 T6 L2 预测文件定义 | 1D-CNN, Bi-Mamba, HMBCNN-style, MCNN-BiLSTM, Plain Mamba, RAAF-BiPAC-Mamba, ResNet/TCN, TFFNet-style, Transformer | 通过 | 无需处理 |
| 结构/主键/值域 | seed_count | 见 T6 L2 预测文件定义 | [np.int64(42), np.int64(43), np.int64(44), np.int64(45), np.int64(46), np.int64(47), np.int64(48), np.int64(49), np.int64(50), np.int64(51)] | 通过 | 无需处理 |
| 结构/主键/值域 | scenario_set | 见 T6 L2 预测文件定义 | ['S0', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6'] | 通过 | 无需处理 |
| 结构/主键/值域 | bad_model_seed_scenario_counts | 见 T6 L2 预测文件定义 | 0 | 通过 | 无需处理 |
| 结构/主键/值域 | bad_class_counts_per_model_seed_scenario | 见 T6 L2 预测文件定义 | 0 | 通过 | 无需处理 |
| 结构/主键/值域 | probabilities_finite | 见 T6 L2 预测文件定义 | True | 通过 | 无需处理 |
| 结构/主键/值域 | probability_range_violations | 见 T6 L2 预测文件定义 | 0 | 通过 | 无需处理 |
| 结构/主键/值域 | max_probability_sum_error | 见 T6 L2 预测文件定义 | 1.00000230319e-10 | 通过 | 无需处理 |
| 结构/主键/值域 | argmax_mismatch_count | 见 T6 L2 预测文件定义 | 0 | 通过 | 无需处理 |
| 结构/主键/值域 | paired_event_sets_match_all_models | 见 T6 L2 预测文件定义 | 0 | 通过 | 无需处理 |
| 统计 | bootstrap 方法 | Accuracy/Macro-F1 paired differences use stratified event bootstrap | B=5000; Avg7 strata=seed+scenario+class; S6 strata=seed+class | 通过 | 若需更高精度，仅增加 bootstrap 次数，不重训 |
| 配对 | McNemar 方法 | Same seed+scenario+event_id paired predictions | proposed vs each baseline; exact binomial McNemar on discordant event pairs | 通过 | 若配对缺失，仅重导 event_id/split_hash 或缺失预测行 |
| 审稿 | 支撑点 | R1.8/R3.3 event-level uncertainty and paired tests | T11 outputs derive from frozen T6 predictions | 充分用于统计补强；不替代 T7/T8/T10/T12 | 后续继续按清单执行 |

强弱关系：RAAF-BiPAC-Mamba 在 Avg7 和 S6 事件准确率上均高于 HMBCNN-style、Plain Mamba 和 Bi-Mamba；与最强 Bi-Mamba 的差值为 Avg7 +3.71 pp、S6 +4.00 pp，paired bootstrap 区间均不跨 0。S6 的三类 recall 中，empty 最高，coal/gangue 相对更低，符合严重混合噪声下煤/矸更易混淆的预期。这里的行数、键唯一性、概率值域、argmax 一致性是硬约束；模型排序和类别难度是科学合理性检查。

## 3. Decision

可直接写入论文

## 4. Minimal action table

| 问题 | 已有文件能否修复 | 最小动作 | 是否重新训练 | 需要返回的最小字段 |
|---|---|---|---|---|
| T11 统计证据尚未进入 TeX | 是 | 下一轮按 M5 将关键 paired tests 和 S6 per-class recall 写入主稿/补充材料 | 否 | 无 |

## 5. Hashes

- `D:\shiyan\tougao\t6_complete_math_results_package\event_predictions_9models_10seeds_complete.csv`: `9bc3a38c79a0c4ec57a638a8dfd1be7a8ea9051cf0034e810a477daaf60c0a69`
- `D:\shiyan\tougao\t11_event_statistics_from_t6\T11_pairwise_event_tests_from_T6.csv`: `345bc790a16d9aae3719a6e2f28dc6d6e4df8e19cb763e89f8185e03d454df4c`
- `D:\shiyan\tougao\t11_event_statistics_from_t6\T11_per_class_recall_bootstrap_from_T6.csv`: `ff3410ed0431a3d6a856aefba7392e62936dbd8e2c65a0edae7e0369e406a256`
