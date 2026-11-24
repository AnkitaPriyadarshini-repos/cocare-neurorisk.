"""Training and cross-validation comparison engine for cognitive risk screening models.

Evaluates Logistic Regression, Random Forest, Gradient Boosting, SVM, and KNN
using identical CV folds on the training split, with honest participant grouping
and leakage-free pipelines.
"""
import os
import json
import logging
from typing import Dict, List, Any, Tuple
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import StratifiedGroupKFold, cross_validate, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV

from .preprocess import clean_raw_data, build_preprocessor
from .evaluate import compute_metrics, find_optimal_threshold, bootstrap_metrics
from .fairness import evaluate_fairness_subgroups

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_candidate_classifiers(seed: int = 42) -> Dict[str, Any]:
    """Define candidate estimators with class imbalance adjustments."""
    return {
        "LogisticRegression": LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            C=1.0,
            random_state=seed
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            class_weight="balanced",
            random_state=seed
        ),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=3,
            random_state=seed
        ),
        "SVM": SVC(
            kernel="rbf",
            probability=True,
            class_weight="balanced",
            C=1.0,
            random_state=seed
        ),
        "KNN": KNeighborsClassifier(
            n_neighbors=5,
            weights="distance"
        )
    }


def compare_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    groups_train: pd.Series,
    preprocessor,
    cv_folds: int = 5,
    seed: int = 42
) -> pd.DataFrame:
    """Run 5-fold cross-validation across all models and return comparison table."""
    candidates = get_candidate_classifiers(seed=seed)
    cv = StratifiedGroupKFold(n_splits=cv_folds, shuffle=True, random_state=seed)

    rows = []
    scoring = ["accuracy", "precision", "recall", "f1", "roc_auc"]

    for name, clf in candidates.items():
        pipe = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", clf)
        ])

        scores = cross_validate(
            pipe,
            X_train,
            y_train,
            groups=groups_train,
            cv=cv,
            scoring=scoring,
            return_train_score=False
        )

        rows.append({
            "model": name,
            "roc_auc_mean": float(np.mean(scores["test_roc_auc"])),
            "roc_auc_std": float(np.std(scores["test_roc_auc"])),
            "sensitivity_mean": float(np.mean(scores["test_recall"])),
            "sensitivity_std": float(np.std(scores["test_recall"])),
            "specificity_proxy": float(np.mean(scores["test_accuracy"])),
            "f1_mean": float(np.mean(scores["test_f1"])),
            "f1_std": float(np.std(scores["test_f1"])),
            "accuracy_mean": float(np.mean(scores["test_accuracy"])),
            "accuracy_std": float(np.std(scores["test_accuracy"]))
        })

    comparison_df = pd.DataFrame(rows).sort_values(by="roc_auc_mean", ascending=False)
    return comparison_df


def train_single_variant(
    variant_name: str,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    groups_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    numeric_features: List[str],
    categorical_features: List[str],
    seed: int = 42,
    target_sensitivity: float = 0.85
) -> Tuple[Pipeline, Dict[str, Any], pd.DataFrame]:
    """Train, tune threshold, evaluate on test once, and package metadata for one variant."""
    # Build leakage-free preprocessor
    preprocessor = build_preprocessor(numeric_features, categorical_features)

    # Model comparison across train folds
    comparison_df = compare_models(
        X_train=X_train,
        y_train=y_train,
        groups_train=groups_train,
        preprocessor=preprocessor,
        cv_folds=5,
        seed=seed
    )

    # Model selection:
    # LogisticRegression is prioritized if within 1-2 points of ensemble models because:
    # 1. Extremely lightweight bundle (< 10 KB file, zero latency)
    # 2. Perfect exact coefficient interpretability for Vercel serverless runtime
    # 3. Well-calibrated probabilities with balanced class weights
    top_model_name = comparison_df.iloc[0]["model"]
    lr_roc = comparison_df[comparison_df["model"] == "LogisticRegression"]["roc_auc_mean"].values[0]
    top_roc = comparison_df.iloc[0]["roc_auc_mean"]

    # Choose model
    if (top_roc - lr_roc) <= 0.03:
        chosen_model_name = "LogisticRegression"
        logging.info(f"[{variant_name}] Selecting LogisticRegression (lightweight, interpretable, within 3% of {top_model_name}).")
    else:
        chosen_model_name = top_model_name
        logging.info(f"[{variant_name}] Selecting {chosen_model_name} as top performer.")

    best_estimator = get_candidate_classifiers(seed=seed)[chosen_model_name]

    # Full pipeline
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", best_estimator)
    ])

    # Out-of-fold CV predictions on train to optimize decision threshold
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    oof_probs = np.zeros(len(y_train))

    for train_idx, val_idx in cv.split(X_train, y_train, groups=groups_train):
        fold_pipe = Pipeline([
            ("preprocessor", build_preprocessor(numeric_features, categorical_features)),
            ("classifier", get_candidate_classifiers(seed=seed)[chosen_model_name])
        ])
        fold_pipe.fit(X_train.iloc[train_idx], y_train.iloc[train_idx])
        oof_probs[val_idx] = fold_pipe.predict_proba(X_train.iloc[val_idx])[:, 1]

    # Threshold optimization on train CV predictions
    optimal_threshold = find_optimal_threshold(
        y_true=y_train.values,
        y_prob=oof_probs,
        target_sensitivity=target_sensitivity
    )

    # Fit final pipeline on 100% of train
    pipeline.fit(X_train, y_train)

    # Evaluate on held-out test ONCE
    test_probs = pipeline.predict_proba(X_test)[:, 1]
    test_metrics = compute_metrics(y_true=y_test.values, y_prob=test_probs, threshold=optimal_threshold)
    test_cis = bootstrap_metrics(y_true=y_test.values, y_prob=test_probs, threshold=optimal_threshold, seed=seed)

    # Fairness subgroup audit on test
    test_pred = (test_probs >= optimal_threshold).astype(int)
    fairness_report = evaluate_fairness_subgroups(
        y_true=y_test.values,
        y_pred=test_pred,
        y_prob=test_probs,
        df_demographics=X_test
    )

    # Reference medians/modes for runtime occlusion
    all_features = numeric_features + categorical_features
    reference_medians = {}
    for nf in numeric_features:
        reference_medians[nf] = float(X_train[nf].median())
    for cf in categorical_features:
        reference_medians[cf] = str(X_train[cf].mode()[0])

    # Synthetic / Aggregate background summary (NEVER raw participant rows)
    background_summary = {
        "n_samples": int(len(X_train)),
        "numeric_summaries": {
            nf: {
                "mean": float(X_train[nf].mean()),
                "std": float(X_train[nf].std()),
                "median": float(X_train[nf].median()),
                "p25": float(X_train[nf].quantile(0.25)),
                "p75": float(X_train[nf].quantile(0.75))
            } for nf in numeric_features
        },
        "categorical_distributions": {
            cf: (X_train[cf].value_counts(normalize=True).round(3)).to_dict()
            for cf in categorical_features
        }
    }

    metadata = {
        "variant": variant_name,
        "model_type": chosen_model_name,
        "features": {
            "numeric": numeric_features,
            "categorical": categorical_features,
            "all_ordered": all_features
        },
        "threshold": float(optimal_threshold),
        "risk_bands": {
            "lower": [0.0, float(round(optimal_threshold * 0.7, 3))],
            "moderate": [float(round(optimal_threshold * 0.7, 3)), float(round(optimal_threshold * 1.3, 3))],
            "higher": [float(round(optimal_threshold * 1.3, 3)), 1.0]
        },
        "sample_sizes": {
            "train": int(len(X_train)),
            "test": int(len(X_test)),
            "train_prevalence": float(np.mean(y_train)),
            "test_prevalence": float(np.mean(y_test))
        },
        "test_metrics": test_metrics,
        "test_metrics_95_ci": test_cis,
        "fairness_audit": fairness_report,
        "reference_medians": reference_medians,
        "background_summary": background_summary,
        "seed": seed,
        "library_versions": {
            "scikit_learn": "1.6.1",
            "joblib": "1.5.1"
        },
        "disclaimer": "This tool is a cognitive risk screening aid designed for preliminary assessment, NOT a clinical diagnosis."
    }

    return pipeline, metadata, comparison_df
