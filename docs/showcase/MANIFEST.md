# CO CARE Showcase Figures Manifest

> **Transparency & Reproducibility Guarantee**: Every figure below is generated deterministically from real saved result artifacts (`ml/reports/*.json|csv`). Zero numbers are cherry-picked or invented. All figures are rendered in both Light and Dark GitHub-compatible themes and optimized to < 400 KB.

**Generated on**: 2026-11-24 15:06:17 UTC  
**Target Dataset**: `oasis`  
**Total Figures**: 19  

| ID | Figure Name | Description | Source Artifact | Script | Light (KB) | Dark (KB) | Data Sidecar |
|:---|:---|:---|:---|:---|:---:|:---:|:---:|
| `01` | **hero_banner** | Hero Banner with 4 live headline stats and badges | `ml/reports/cv_metrics.json, ml/reports/test_metrics.json` | [`ml/src/viz/fig_hero.py`](ml/src/viz/fig_hero.py) | 214 | 213 | [`JSON`](docs/showcase/data\01_hero_banner.json) |
| `02` | **pipeline_architecture** | Decoupled pipeline: Offline training vs Online serverless runtime | `Architecture specification` | [`ml/src/viz/fig_architecture.py`](ml/src/viz/fig_architecture.py) | 280 | 277 | [`JSON`](docs/showcase/data\02_pipeline_architecture.json) |
| `03` | **split_schematic** | Longitudinal participant grouping and permutation check inset | `ml/reports/class_distribution_summary.json, AUDIT.md` | [`ml/src/viz/fig_split.py`](ml/src/viz/fig_split.py) | 323 | 316 | [`JSON`](docs/showcase/data\03_split_schematic.json) |
| `04` | **data_overview** | Class distribution overall, by sex, age band, and missingness table | `ml/reports/class_distribution_summary.json, missingness_table.csv` | [`ml/src/viz/fig_data.py`](ml/src/viz/fig_data.py) | 247 | 247 | [`JSON`](docs/showcase/data\04_data_overview.json) |
| `05` | **model_leaderboard** | 5 Candidate model repeated CV comparison and serverless Pareto frontier | `ml/reports/cv_metrics.json, ml/reports/model_benchmarks.json` | [`ml/src/viz/fig_leaderboard.py`](ml/src/viz/fig_leaderboard.py) | 252 | 248 | [`JSON`](docs/showcase/data\05_model_leaderboard.json) |
| `06` | **roc_pr_curves** | Held-out test ROC and PR curves with bootstrap 95% CIs and operating points | `ml/reports/test_metrics.json` | [`ml/src/viz/fig_curves.py`](ml/src/viz/fig_curves.py) | 79 | 359 | [`JSON`](docs/showcase/data\06_roc_pr_curves.json) |
| `07` | **threshold_tradeoff** | Sensitivity/specificity trade-off curves with shaded operating zones | `ml/reports/threshold_operating_points.json` | [`ml/src/viz/fig_threshold.py`](ml/src/viz/fig_threshold.py) | 318 | 308 | [`JSON`](docs/showcase/data\07_threshold_tradeoff.json) |
| `08` | **calibration** | Reliability diagram across 10 probability bins and prediction histogram | `ml/reports/test_metrics.json` | [`ml/src/viz/fig_calibration.py`](ml/src/viz/fig_calibration.py) | 233 | 227 | [`JSON`](docs/showcase/data\08_calibration.json) |
| `09` | **confusion_matrices** | Side-by-side confusion matrices with counts and bootstrap 95% CIs | `ml/reports/test_metrics.json` | [`ml/src/viz/fig_confusion.py`](ml/src/viz/fig_confusion.py) | 203 | 201 | [`JSON`](docs/showcase/data\09_confusion_matrices.json) |
| `10` | **ablation_value_added** | Stepped progression showing marginal lift from demographics and MMSE | `ml/reports/cv_metrics.json, test_metrics.json` | [`ml/src/viz/fig_ablation.py`](ml/src/viz/fig_ablation.py) | 220 | 208 | [`JSON`](docs/showcase/data\10_ablation_value_added.json) |
| `11` | **explainability** | Global odds ratios, synthetic waterfall, and occlusion vs SHAP parity | `ml/reports/explainability.json` | [`ml/src/viz/fig_explainability.py`](ml/src/viz/fig_explainability.py) | 342 | 341 | [`JSON`](docs/showcase/data\11_explainability.json) |
| `12` | **fairness_forest_plot** | Subgroup parity across Sex, Age, and Education with underpowered flags | `ml/reports/subgroup_metrics.json` | [`ml/src/viz/fig_fairness.py`](ml/src/viz/fig_fairness.py) | 220 | 219 | [`JSON`](docs/showcase/data\12_fairness_forest_plot.json) |
| `13` | **learning_curve** | Sample efficiency convergence curve motivating LASI-DAD transition | `ml/reports/learning_curve.json` | [`ml/src/viz/fig_learning.py`](ml/src/viz/fig_learning.py) | 296 | 286 | [`JSON`](docs/showcase/data\13_learning_curve.json) |
| `14` | **model_card_glance** | Executive one-page model card infographic covering use, data, and ethics | `MODEL_CARD.md` | [`ml/src/viz/fig_modelcard.py`](ml/src/viz/fig_modelcard.py) | 95 | 100 | [`JSON`](docs/showcase/data\14_model_card_glance.json) |
| `15` | **signature_visual** | Animated CV fold convergence GIF and static high-res fallback | `Cross-validation fold evaluations` | [`ml/src/viz/fig_animated.py`](ml/src/viz/fig_animated.py) | 276 | 263 | [`JSON`](docs/showcase/data\15_signature_visual.json) |
| `16` | **training_loss_convergence** | Training dynamics: Cross-entropy loss reduction and accuracy trajectory across solver iterations | `ml/reports/training_convergence.json` | [`ml/src/viz/fig_training_curves.py`](ml/src/viz/fig_training_curves.py) | 258 | 246 | [`JSON`](docs/showcase/data\16_training_loss_convergence.json) |
| `17` | **class_wise_evaluation** | Class-wise Precision, Recall, Specificity, and F1 comparison with 95% cluster-bootstrap CIs | `ml/reports/class_wise_metrics.json` | [`ml/src/viz/fig_class_metrics.py`](ml/src/viz/fig_class_metrics.py) | 167 | 163 | [`JSON`](docs/showcase/data\17_class_wise_evaluation.json) |
| `18` | **risk_factor_odds_ratios** | Multifactor Pearson correlation matrix heatmap and multivariate adjusted odds ratios | `ml/reports/risk_factors.json` | [`ml/src/viz/fig_risk_factors.py`](ml/src/viz/fig_risk_factors.py) | 259 | 256 | [`JSON`](docs/showcase/data\18_risk_factor_odds_ratios.json) |
| `19` | **longitudinal_trajectory** | Longitudinal risk progression and conversion inflection points across clinical visits | `ml/reports/longitudinal_trajectories.json` | [`ml/src/viz/fig_longitudinal.py`](ml/src/viz/fig_longitudinal.py) | 271 | 260 | [`JSON`](docs/showcase/data\19_longitudinal_trajectory.json) |

## Reproduction Commands
```bash
# Regenerate all figures deterministically
make figures

# Run figures for future LASI-DAD cohort release
make figures DATASET=lasi_dad
```
