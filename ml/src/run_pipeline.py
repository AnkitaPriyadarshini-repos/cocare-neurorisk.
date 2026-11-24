"""Master CLI orchestrator for Cognitive Risk Screening ML pipeline.

Targets:
- eda: Missingness, correlations, class distributions, publication PNGs
- train: 5-fold CV model comparison, pipeline training, threshold optimization
- evaluate: Final test evaluation, bootstrap 95% CIs, calibration, fairness audit
- explain: SHAP plots and runtime explainability validation
- export: Copy artifacts to backend/models/
- all: Execute complete pipeline end-to-end
"""
import os
import sys
import json
import argparse
import logging
from typing import Dict, Any
import numpy as np
import pandas as pd

from sklearn.model_selection import StratifiedGroupKFold
from sklearn.linear_model import LogisticRegression

# Import local pipeline modules
from ml.src.datasets.oasis import load_oasis
from ml.src.preprocess import clean_raw_data, build_preprocessor
from ml.src.train import train_single_variant, compare_models
from ml.src.evaluate import compute_metrics, bootstrap_metrics
from ml.src.explain import explain_one
from ml.src.export import export_model_artifacts
from ml.src.fairness import evaluate_fairness_subgroups

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def run_eda(data_path: str, figures_dir: str, reports_dir: str) -> Dict[str, Any]:
    """Execute exploratory data analysis and generate publication figures."""
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    X_raw, y_raw, groups = load_oasis(data_path, baseline_only=False)
    df_raw = X_raw.copy()
    df_raw["target"] = y_raw

    # Missingness analysis
    missing_table = pd.DataFrame({
        "column": df_raw.columns,
        "missing_count": df_raw.isna().sum().values,
        "missing_pct": (df_raw.isna().mean() * 100).round(2).values
    })
    missing_table.to_csv(os.path.join(reports_dir, "missingness_table.csv"), index=False)

    # Clean data for distribution checks
    df_clean, dq_report = clean_raw_data(df_raw)
    with open(os.path.join(reports_dir, "data_quality_report.json"), "w", encoding="utf-8") as f:
        json.dump(dq_report, f, indent=2)

    # Class distributions overall and by sex
    class_dist = {
        "total_records": len(df_clean),
        "target_prevalence": float(df_clean["target"].mean()),
        "target_counts": df_clean["target"].value_counts().to_dict(),
        "by_sex": df_clean.groupby("Sex")["target"].agg(["count", "mean"]).to_dict(orient="index") if "Sex" in df_clean else {}
    }
    with open(os.path.join(reports_dir, "class_distribution_summary.json"), "w", encoding="utf-8") as f:
        json.dump(class_dist, f, indent=2)

    # Try generating PNG plots if matplotlib is available
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        # 1. Target distribution by sex
        fig, ax = plt.subplots(figsize=(6, 4))
        df_clean.groupby(["Sex", "target"]).size().unstack(fill_value=0).plot(kind="bar", stacked=True, ax=ax, color=["#2b5c8f", "#d95f02"])
        ax.set_title("Cognitive Risk Distribution by Sex (0=Nondemented, 1=Demented)")
        ax.set_xlabel("Sex")
        ax.set_ylabel("Count")
        ax.legend(["Nondemented", "Impaired / At Risk"])
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "class_distribution_by_sex.png"), dpi=300)
        plt.close()

        # 2. Age vs MMSE boxplot
        if "MMSE" in df_clean.columns:
            fig, ax = plt.subplots(figsize=(6, 4))
            df_clean.boxplot(column="MMSE", by="target", ax=ax)
            ax.set_title("MMSE Score Distribution by Cognitive Status")
            ax.set_xlabel("Target Status (0 = Nondemented, 1 = Impaired / At Risk)")
            ax.set_ylabel("MMSE Total Score")
            plt.suptitle("")
            plt.tight_layout()
            plt.savefig(os.path.join(figures_dir, "mmse_distribution_by_target.png"), dpi=300)
            plt.close()

        # 3. Missingness bar chart
        fig, ax = plt.subplots(figsize=(8, 4))
        missing_table.plot(x="column", y="missing_pct", kind="bar", ax=ax, color="#7570b3", legend=False)
        ax.set_title("Missing Data Percentage per Feature")
        ax.set_ylabel("Percent Missing (%)")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "missingness_percentage.png"), dpi=300)
        plt.close()

        logging.info("EDA figures successfully generated.")
    except ImportError:
        logging.warning("Matplotlib not available; skipping PNG rendering, tables saved.")

    return class_dist


def run_pipeline(seed: int = 42):
    """Run full pipeline: Train both variants, evaluate on test, explain, export."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, "ml", "data", "oasis_longitudinal.csv")
    figures_dir = os.path.join(base_dir, "ml", "reports", "figures")
    reports_dir = os.path.join(base_dir, "ml", "reports")
    artifacts_dir = os.path.join(base_dir, "ml", "artifacts")
    backend_models_dir = os.path.join(base_dir, "backend", "models")

    # Step 1: EDA
    logging.info("=== STEP 1: Running EDA ===")
    run_eda(data_path, figures_dir, reports_dir)

    # Step 2: Load data and perform stratified participant split
    logging.info("=== STEP 2: Splitting Data by Participant ===")
    X_raw, y_raw, groups = load_oasis(data_path)
    X_clean, _ = clean_raw_data(X_raw)

    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    train_idx, test_idx = next(sgkf.split(X_clean, y_raw, groups=groups))

    X_train, X_test = X_clean.iloc[train_idx].copy(), X_clean.iloc[test_idx].copy()
    y_train, y_test = y_raw.iloc[train_idx].copy(), y_raw.iloc[test_idx].copy()
    groups_train = groups.iloc[train_idx].copy()

    # Verify no participant leakage
    train_subjects = set(groups.iloc[train_idx])
    test_subjects = set(groups.iloc[test_idx])
    overlap = train_subjects.intersection(test_subjects)
    assert len(overlap) == 0, f"DATA LEAKAGE: {len(overlap)} subjects present in both train and test!"
    logging.info(f"Verified participant isolation: 0 subject overlap. Train N={len(X_train)} ({len(train_subjects)} subjects), Test N={len(X_test)} ({len(test_subjects)} subjects).")

    # Step 3: Train Variant 'with_mmse'
    logging.info("=== STEP 3: Training Variant 'with_mmse' ===")
    pipe_with, meta_with, comp_with = train_single_variant(
        variant_name="model_with_mmse",
        X_train=X_train,
        y_train=y_train,
        groups_train=groups_train,
        X_test=X_test,
        y_test=y_test,
        numeric_features=["Age", "EDUC", "SES", "MMSE"],
        categorical_features=["Sex"],
        seed=seed,
        target_sensitivity=0.85
    )
    comp_with.to_csv(os.path.join(reports_dir, "model_comparison_with_mmse.csv"), index=False)
    export_model_artifacts("model_with_mmse", pipe_with, meta_with, artifacts_dir, backend_models_dir)

    # Step 4: Train Variant 'without_mmse' (Strictly no MMSE anywhere!)
    logging.info("=== STEP 4: Training Variant 'without_mmse' ===")
    pipe_without, meta_without, comp_without = train_single_variant(
        variant_name="model_without_mmse",
        X_train=X_train,
        y_train=y_train,
        groups_train=groups_train,
        X_test=X_test,
        y_test=y_test,
        numeric_features=["Age", "EDUC", "SES"],
        categorical_features=["Sex"],
        seed=seed,
        target_sensitivity=0.85
    )
    comp_without.to_csv(os.path.join(reports_dir, "model_comparison_without_mmse.csv"), index=False)
    export_model_artifacts("model_without_mmse", pipe_without, meta_without, artifacts_dir, backend_models_dir)

    # Step 5: Save Model Comparison Summary
    combined_comp = pd.concat([
        comp_with.assign(variant="with_mmse"),
        comp_without.assign(variant="without_mmse")
    ], ignore_index=True)
    combined_comp.to_csv(os.path.join(reports_dir, "model_comparison.csv"), index=False)

    # Step 6: Generate ROC and Calibration curves
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from sklearn.metrics import roc_curve, auc
        from sklearn.calibration import calibration_curve

        # ROC Curve comparison
        plt.figure(figsize=(6, 5))
        for pipe, meta, label, color in [
            (pipe_with, meta_with, "With MMSE", "#1b9e77"),
            (pipe_without, meta_without, "Without MMSE", "#d95f02")
        ]:
            probs = pipe.predict_proba(X_test)[:, 1]
            fpr, tpr, _ = roc_curve(y_test, probs)
            roc_val = auc(fpr, tpr)
            plt.plot(fpr, tpr, color=color, lw=2, label=f"{label} (AUC = {roc_val:.3f})")

        plt.plot([0, 1], [0, 1], color="navy", lw=1, linestyle="--")
        plt.xlabel("False Positive Rate (1 - Specificity)")
        plt.ylabel("True Positive Rate (Sensitivity)")
        plt.title("Receiver Operating Characteristic (Held-Out Test)")
        plt.legend(loc="lower right")
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "roc_curve_comparison.png"), dpi=300)
        plt.close()

        # Calibration Curves
        plt.figure(figsize=(6, 5))
        for pipe, meta, label, color in [
            (pipe_with, meta_with, "With MMSE", "#1b9e77"),
            (pipe_without, meta_without, "Without MMSE", "#d95f02")
        ]:
            probs = pipe.predict_proba(X_test)[:, 1]
            prob_true, prob_pred = calibration_curve(y_test, probs, n_bins=5)
            plt.plot(prob_pred, prob_true, marker="o", color=color, lw=2, label=label)

        plt.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Perfect Calibration")
        plt.xlabel("Mean Predicted Probability")
        plt.ylabel("Observed Fraction of Positives")
        plt.title("Calibration Reliability Diagram (Held-Out Test)")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "calibration_curve.png"), dpi=300)
        plt.close()

        logging.info("Evaluation figures generated successfully.")
    except Exception as e:
        logging.warning(f"Could not generate ROC/Calibration figures: {e}")

    logging.info("=== Pipeline execution complete! Both variants exported successfully. ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run cognitive risk ML pipeline.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    args = parser.parse_args()
    run_pipeline(seed=args.seed)
