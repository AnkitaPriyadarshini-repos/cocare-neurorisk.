# CO CARE Showcase Figures Manifest

> **Transparency & Reproducibility Guarantee**: Every figure below is generated deterministically from real saved result artifacts (`ml/reports/*.json|csv`). Zero numbers are cherry-picked or invented. All figures are rendered in both Light and Dark GitHub-compatible themes and optimized to < 400 KB.

**Generated on**: 2026-11-24 12:55:45 UTC  
**Target Dataset**: `oasis`  
**Total Figures**: 15  

| ID | Figure Name | Description | Source Artifact | Script | Light (KB) | Dark (KB) | Data Sidecar |
|:---|:---|:---|:---|:---|:---:|:---:|:---:|
| `01` | **hero_banner** | Hero Banner with 4 live headline stats and badges | `ml/reports/cv_metrics.json, ml/reports/test_metrics.json` | [`ml/src/viz/fig_hero.py`](ml/src/viz/fig_hero.py) | 210 | 209 | [`JSON`](docs/showcase/data\01_hero_banner.json) |
| `02` | **pipeline_architecture** | Decoupled pipeline: Offline training vs Online serverless runtime | `Architecture specification` | [`ml/src/viz/fig_architecture.py`](ml/src/viz/fig_architecture.py) | 281 | 278 | [`JSON`](docs/showcase/data\02_pipeline_architecture.json) |
| `03` | **split_schematic** | Longitudinal participant grouping and permutation check inset | `ml/reports/class_distribution_summary.json, AUDIT.md` | [`ml/src/viz/fig_split.py`](ml/src/viz/fig_split.py) | 324 | 317 | [`JSON`](docs/showcase/data\03_split_schematic.json) |
| `04` | **data_overview** | Class distribution overall, by sex, age band, and missingness table | `ml/reports/class_distribution_summary.json, missingness_table.csv` | [`ml/src/viz/fig_data.py`](ml/src/viz/fig_data.py) | 248 | 248 | [`JSON`](docs/showcase/data\04_data_overview.json) |
| `05` | **model_leaderboard** | 5 Candidate model repeated CV comparison and serverless Pareto frontier | `ml/reports/cv_metrics.json, ml/reports/model_benchmarks.json` | [`ml/src/viz/fig_leaderboard.py`](ml/src/viz/fig_leaderboard.py) | 252 | 249 | [`JSON`](docs/showcase/data\05_model_leaderboard.json) |
| `06` | **roc_pr_curves** | Held-out test ROC and PR curves with bootstrap 95% CIs and operating points | `ml/reports/test_metrics.json` | [`ml/src/viz/fig_curves.py`](ml/src/viz/fig_curves.py) | 79 | 83 | [`JSON`](docs/showcase/data\06_roc_pr_curves.json) |
| `07` | **threshold_tradeoff** | Sensitivity/specificity trade-off curves with shaded operating zones | `ml/reports/threshold_operating_points.json` | [`ml/src/viz/fig_threshold.py`](ml/src/viz/fig_threshold.py) | 319 | 309 | [`JSON`](docs/showcase/data\07_threshold_tradeoff.json) |
| `08` | **calibration** | Reliability diagram across 10 probability bins and prediction histogram | `ml/reports/test_metrics.json` | [`ml/src/viz/fig_calibration.py`](ml/src/viz/fig_calibration.py) | 234 | 228 | [`JSON`](docs/showcase/data\08_calibration.json) |
| `09` | **confusion_matrices** | Side-by-side confusion matrices with counts and bootstrap 95% CIs | `ml/reports/test_metrics.json` | [`ml/src/viz/fig_confusion.py`](ml/src/viz/fig_confusion.py) | 204 | 202 | [`JSON`](docs/showcase/data\09_confusion_matrices.json) |
| `10` | **ablation_value_added** | Stepped progression showing marginal lift from demographics and MMSE | `ml/reports/cv_metrics.json, test_metrics.json` | [`ml/src/viz/fig_ablation.py`](ml/src/viz/fig_ablation.py) | 221 | 209 | [`JSON`](docs/showcase/data\10_ablation_value_added.json) |
| `11` | **explainability** | Global odds ratios, synthetic waterfall, and occlusion vs SHAP parity | `ml/reports/explainability.json` | [`ml/src/viz/fig_explainability.py`](ml/src/viz/fig_explainability.py) | 344 | 343 | [`JSON`](docs/showcase/data\11_explainability.json) |
| `12` | **fairness_forest_plot** | Subgroup parity across Sex, Age, and Education with underpowered flags | `ml/reports/subgroup_metrics.json` | [`ml/src/viz/fig_fairness.py`](ml/src/viz/fig_fairness.py) | 220 | 219 | [`JSON`](docs/showcase/data\12_fairness_forest_plot.json) |
| `13` | **learning_curve** | Sample efficiency convergence curve motivating LASI-DAD transition | `ml/reports/learning_curve.json` | [`ml/src/viz/fig_learning.py`](ml/src/viz/fig_learning.py) | 297 | 287 | [`JSON`](docs/showcase/data\13_learning_curve.json) |
| `14` | **model_card_glance** | Executive one-page model card infographic covering use, data, and ethics | `MODEL_CARD.md` | [`ml/src/viz/fig_modelcard.py`](ml/src/viz/fig_modelcard.py) | 95 | 100 | [`JSON`](docs/showcase/data\14_model_card_glance.json) |
| `15` | **signature_visual** | Animated CV fold convergence GIF and static high-res fallback | `Cross-validation fold evaluations` | [`ml/src/viz/fig_animated.py`](ml/src/viz/fig_animated.py) | 277 | 264 | [`JSON`](docs/showcase/data\15_signature_visual.json) |

## Reproduction Commands
```bash
# Regenerate all figures deterministically
make figures

# Run figures for future LASI-DAD cohort release
make figures DATASET=lasi_dad
```
