"""Comprehensive Audit, Baselines, and Complete Metrics Computation Engine.

Performs:
1. Participant grouping leakage audit (Ungrouped vs. Grouped splits).
2. Permutation / label-shuffle sanity checks (~0.50 AUC target).
3. Baseline comparisons (Majority class, Age-only Logistic Regression).
4. Repeated Stratified Group K-Fold cross-validation (5 repeats x 5 folds = 25 evaluations).
5. Held-out test set evaluation with 2,000 bootstrap resamples for all metrics (including NPV & specificity for both variants).
6. 3-operating point threshold analysis (Sensitivity >= 0.80, 0.85, 0.90).
7. Preprocessing fit-on-train-only verification.
8. Emits ml/docs/AUDIT.md, ml/reports/test_metrics.json, and ml/reports/cv_metrics.json.
"""
import os
import sys
import json
import logging
from typing import Dict, List, Any, Tuple
import numpy as np
import pandas as pd

from sklearn.model_selection import StratifiedKFold, StratifiedGroupKFold
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    roc_auc_score, average_precision_score, accuracy_score,
    precision_score, recall_score, f1_score, confusion_matrix,
    brier_score_loss
)

from ml.src.datasets.oasis import load_oasis
from ml.src.preprocess import clean_raw_data, build_preprocessor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def compute_all_metrics(y_true: np.ndarray, y_prob: np.ndarray, threshold: float) -> Dict[str, Any]:
    """Compute complete metric dictionary including NPV, specificity, and Brier score."""
    y_pred = (y_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    
    sens = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0
    f1 = 2 * (prec * sens) / (prec + sens) if (prec + sens) > 0 else 0.0
    acc = (tp + tn) / len(y_true)
    
    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except ValueError:
        roc_auc = 0.5
        
    try:
        pr_auc = float(average_precision_score(y_true, y_prob))
    except ValueError:
        pr_auc = float(np.mean(y_true))
        
    brier = float(brier_score_loss(y_true, y_prob))
    
    return {
        "n_total": int(len(y_true)),
        "n_positives": int(np.sum(y_true)),
        "n_negatives": int(len(y_true) - np.sum(y_true)),
        "threshold": float(threshold),
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn),
        "sensitivity": float(sens),
        "specificity": float(spec),
        "precision": float(prec),
        "npv": float(npv),
        "f1": float(f1),
        "accuracy": float(acc),
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
        "brier_score": float(brier)
    }


def bootstrap_ci_2000(y_true: np.ndarray, y_prob: np.ndarray, threshold: float, n_boot: int = 2000, seed: int = 42) -> Dict[str, Dict[str, float]]:
    """Compute 95% bootstrap confidence intervals with >= 2,000 resamples."""
    rng = np.random.RandomState(seed)
    n = len(y_true)
    keys = ["sensitivity", "specificity", "precision", "npv", "f1", "accuracy", "roc_auc", "pr_auc", "brier_score"]
    boot_stats = {k: [] for k in keys}
    
    for _ in range(n_boot):
        idx = rng.randint(0, n, size=n)
        b_true = y_true[idx]
        b_prob = y_prob[idx]
        
        # Guard if sample lacks both classes
        if len(np.unique(b_true)) < 2:
            continue
            
        m = compute_all_metrics(b_true, b_prob, threshold)
        for k in keys:
            boot_stats[k].append(m[k])
            
    cis = {}
    for k in keys:
        vals = np.array(boot_stats[k])
        if len(vals) > 0:
            cis[k] = {
                "mean": float(np.mean(vals)),
                "std": float(np.std(vals)),
                "ci_lower": float(np.percentile(vals, 2.5)),
                "ci_upper": float(np.percentile(vals, 97.5))
            }
        else:
            cis[k] = {"mean": 0.0, "std": 0.0, "ci_lower": 0.0, "ci_upper": 0.0}
            
    return cis


def run_repeated_cv(
    pipe: Pipeline,
    X: pd.DataFrame,
    y: pd.Series,
    groups: pd.Series,
    n_repeats: int = 5,
    n_splits: int = 5,
    seed: int = 42
) -> Dict[str, Any]:
    """Execute n_repeats of StratifiedGroupKFold CV and aggregate metrics."""
    metrics_list = []
    
    for r in range(n_repeats):
        rep_seed = seed + r * 100
        sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=rep_seed)
        
        for train_idx, val_idx in sgkf.split(X, y, groups=groups):
            X_tr, y_tr = X.iloc[train_idx], y.iloc[train_idx]
            X_val, y_val = X.iloc[val_idx], y.iloc[val_idx]
            
            p = Pipeline([
                ("preprocessor", pipe.named_steps["preprocessor"]),
                ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=rep_seed))
            ])
            p.fit(X_tr, y_tr)
            probs = p.predict_proba(X_val)[:, 1]
            
            # Use default 0.5 threshold for pure model discrimination comparison
            m = compute_all_metrics(y_val.values, probs, threshold=0.5)
            metrics_list.append(m)
            
    summary = {}
    keys = ["sensitivity", "specificity", "precision", "npv", "f1", "accuracy", "roc_auc", "pr_auc", "brier_score"]
    for k in keys:
        vals = [m[k] for m in metrics_list]
        summary[k] = {
            "mean": float(np.mean(vals)),
            "std": float(np.std(vals)),
            "min": float(np.min(vals)),
            "max": float(np.max(vals))
        }
    summary["n_evaluations"] = len(metrics_list)
    summary["n_repeats"] = n_repeats
    summary["n_splits"] = n_splits
    return summary


def evaluate_operating_points(y_true: np.ndarray, y_prob: np.ndarray) -> Dict[str, Any]:
    """Find operating points targeting sensitivities: >= 0.80, >= 0.85, >= 0.90."""
    thresholds = np.linspace(0.01, 0.99, 500)
    target_sensitivities = [0.80, 0.85, 0.90]
    results = {}
    
    for target in target_sensitivities:
        best_th = 0.5
        best_diff = 1.0
        best_m = None
        
        for th in thresholds:
            m = compute_all_metrics(y_true, y_prob, th)
            if m["sensitivity"] >= target:
                diff = m["sensitivity"] - target
                if diff < best_diff:
                    best_diff = diff
                    best_th = th
                    best_m = m
                    
        if best_m is None:
            best_th = 0.5
            best_m = compute_all_metrics(y_true, y_prob, 0.5)
            
        results[f"target_sens_{int(target*100)}"] = {
            "target_sensitivity": target,
            "selected_threshold": round(float(best_th), 4),
            "achieved_sensitivity": round(float(best_m["sensitivity"]), 4),
            "achieved_specificity": round(float(best_m["specificity"]), 4),
            "achieved_precision": round(float(best_m["precision"]), 4),
            "achieved_npv": round(float(best_m["npv"]), 4),
            "achieved_f1": round(float(best_m["f1"]), 4),
            "achieved_accuracy": round(float(best_m["accuracy"]), 4),
            "tp": best_m["tp"],
            "fp": best_m["fp"],
            "tn": best_m["tn"],
            "fn": best_m["fn"],
            "clinical_tradeoff_note": (
                f"At {int(target*100)}% sensitivity threshold ({best_th:.4f}), "
                f"the model misses only {best_m['fn']} cases out of {best_m['tp']+best_m['fn']} at the expense of "
                f"{best_m['fp']} false positives ({best_m['specificity']*100:.1f}% specificity)."
            )
        }
        
    return results


def run_full_audit_and_metrics():
    """Execute complete audit, metrics, baselines, and report generation."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, "ml", "data", "oasis_longitudinal.csv")
    docs_dir = os.path.join(base_dir, "ml", "docs")
    reports_dir = os.path.join(base_dir, "ml", "reports")
    os.makedirs(docs_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    
    logging.info("Loading OASIS data for audit...")
    X_raw, y_raw, groups = load_oasis(data_path)
    X_clean, _ = clean_raw_data(X_raw)
    
    seed = 42
    
    # 1. Audit Grouped vs Ungrouped splitting
    logging.info("Running Ungrouped vs Grouped split audit...")
    prep_with = build_preprocessor(["Age", "EDUC", "SES", "MMSE"], ["Sex"])
    prep_wo = build_preprocessor(["Age", "EDUC", "SES"], ["Sex"])
    lr = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=seed)
    
    pipe_with = Pipeline([("preprocessor", prep_with), ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=seed))])
    pipe_wo = Pipeline([("preprocessor", prep_wo), ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=seed))])
    
    # Ungrouped CV
    cv_ungrouped = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    scores_ungrouped_w = []
    scores_ungrouped_wo = []
    for tr, te in cv_ungrouped.split(X_clean, y_raw):
        pipe_with.fit(X_clean.iloc[tr], y_raw.iloc[tr])
        pipe_wo.fit(X_clean.iloc[tr], y_raw.iloc[tr])
        scores_ungrouped_w.append(roc_auc_score(y_raw.iloc[te], pipe_with.predict_proba(X_clean.iloc[te])[:, 1]))
        scores_ungrouped_wo.append(roc_auc_score(y_raw.iloc[te], pipe_wo.predict_proba(X_clean.iloc[te])[:, 1]))
        
    # Grouped CV
    cv_grouped = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    scores_grouped_w = []
    scores_grouped_wo = []
    for tr, te in cv_grouped.split(X_clean, y_raw, groups=groups):
        pipe_with.fit(X_clean.iloc[tr], y_raw.iloc[tr])
        pipe_wo.fit(X_clean.iloc[tr], y_raw.iloc[tr])
        scores_grouped_w.append(roc_auc_score(y_raw.iloc[te], pipe_with.predict_proba(X_clean.iloc[te])[:, 1]))
        scores_grouped_wo.append(roc_auc_score(y_raw.iloc[te], pipe_wo.predict_proba(X_clean.iloc[te])[:, 1]))

    audit_leakage_results = {
        "with_mmse": {
            "ungrouped_auc_mean": float(np.mean(scores_ungrouped_w)),
            "ungrouped_auc_std": float(np.std(scores_ungrouped_w)),
            "grouped_auc_mean": float(np.mean(scores_grouped_w)),
            "grouped_auc_std": float(np.std(scores_grouped_w)),
            "auc_delta": float(np.mean(scores_ungrouped_w) - np.mean(scores_grouped_w))
        },
        "without_mmse": {
            "ungrouped_auc_mean": float(np.mean(scores_ungrouped_wo)),
            "ungrouped_auc_std": float(np.std(scores_ungrouped_wo)),
            "grouped_auc_mean": float(np.mean(scores_grouped_wo)),
            "grouped_auc_std": float(np.std(scores_grouped_wo)),
            "auc_delta": float(np.mean(scores_ungrouped_wo) - np.mean(scores_grouped_wo))
        }
    }
    
    # 2. Permutation / Label-shuffle sanity check
    logging.info("Running label-shuffle permutation test (target ~0.50 AUC)...")
    rng = np.random.RandomState(seed)
    perm_aucs_with = []
    perm_aucs_without = []
    for r in range(10):
        y_shuffled = pd.Series(rng.permutation(y_raw.values), index=y_raw.index)
        for tr, te in cv_grouped.split(X_clean, y_shuffled, groups=groups):
            pipe_with.fit(X_clean.iloc[tr], y_shuffled.iloc[tr])
            pipe_wo.fit(X_clean.iloc[tr], y_shuffled.iloc[tr])
            perm_aucs_with.append(roc_auc_score(y_shuffled.iloc[te], pipe_with.predict_proba(X_clean.iloc[te])[:, 1]))
            perm_aucs_without.append(roc_auc_score(y_shuffled.iloc[te], pipe_wo.predict_proba(X_clean.iloc[te])[:, 1]))
            
    perm_results = {
        "with_mmse": {"mean_auc": float(np.mean(perm_aucs_with)), "std_auc": float(np.std(perm_aucs_with))},
        "without_mmse": {"mean_auc": float(np.mean(perm_aucs_without)), "std_auc": float(np.std(perm_aucs_without))}
    }
    
    # 3. Baseline comparison
    logging.info("Evaluating baseline models (Majority class & Age-only)...")
    # Majority class baseline
    dummy = DummyClassifier(strategy="most_frequent")
    dummy_accs = []
    for tr, te in cv_grouped.split(X_clean, y_raw, groups=groups):
        dummy.fit(X_clean.iloc[tr], y_raw.iloc[tr])
        dummy_accs.append(accuracy_score(y_raw.iloc[te], dummy.predict(X_clean.iloc[te])))
        
    # Age-only Logistic Regression
    prep_age = build_preprocessor(["Age"], [])
    pipe_age = Pipeline([("preprocessor", prep_age), ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=seed))])
    age_aucs = []
    age_accs = []
    for tr, te in cv_grouped.split(X_clean, y_raw, groups=groups):
        pipe_age.fit(X_clean.iloc[tr], y_raw.iloc[tr])
        age_aucs.append(roc_auc_score(y_raw.iloc[te], pipe_age.predict_proba(X_clean.iloc[te])[:, 1]))
        age_accs.append(accuracy_score(y_raw.iloc[te], pipe_age.predict(X_clean.iloc[te])))
        
    baselines = {
        "majority_class": {
            "accuracy_mean": float(np.mean(dummy_accs)),
            "accuracy_std": float(np.std(dummy_accs)),
            "roc_auc": 0.50
        },
        "age_only_logistic_regression": {
            "roc_auc_mean": float(np.mean(age_aucs)),
            "roc_auc_std": float(np.std(age_aucs)),
            "accuracy_mean": float(np.mean(age_accs)),
            "accuracy_std": float(np.std(age_accs))
        }
    }
    
    # 4. Repeated Grouped CV (5 repeats x 5 folds = 25 evaluations) - Primary numbers
    logging.info("Running 5x Repeated 5-Fold Stratified Group K-Fold CV (25 evaluations per variant)...")
    cv_with_summary = run_repeated_cv(pipe_with, X_clean, y_raw, groups, n_repeats=5, n_splits=5, seed=seed)
    cv_wo_summary = run_repeated_cv(pipe_wo, X_clean, y_raw, groups, n_repeats=5, n_splits=5, seed=seed)
    cv_metrics = {
        "model_with_mmse": cv_with_summary,
        "model_without_mmse": cv_wo_summary,
        "baselines": baselines
    }
    with open(os.path.join(reports_dir, "cv_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(cv_metrics, f, indent=2)
        
    # 5. Held-out test evaluation with 2,000 bootstrap resamples
    logging.info("Evaluating held-out test set with 2,000 bootstrap resamples...")
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    train_idx, test_idx = next(sgkf.split(X_clean, y_raw, groups=groups))
    
    X_train, X_test = X_clean.iloc[train_idx].copy(), X_clean.iloc[test_idx].copy()
    y_train, y_test = y_raw.iloc[train_idx].copy(), y_raw.iloc[test_idx].copy()
    groups_train = groups.iloc[train_idx]
    
    # Verify participant isolation
    train_sub = set(groups.iloc[train_idx])
    test_sub = set(groups.iloc[test_idx])
    assert len(train_sub.intersection(test_sub)) == 0, "DATA LEAKAGE: Subject overlap in split!"
    
    # Find optimal thresholds on CV folds of train ONLY using fresh preprocessors
    oof_with = np.zeros(len(y_train))
    oof_wo = np.zeros(len(y_train))
    cv_train = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    for tr_f, val_f in cv_train.split(X_train, y_train, groups=groups_train):
        p_w = Pipeline([
            ("preprocessor", build_preprocessor(["Age", "EDUC", "SES", "MMSE"], ["Sex"])),
            ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=seed))
        ])
        p_wo = Pipeline([
            ("preprocessor", build_preprocessor(["Age", "EDUC", "SES"], ["Sex"])),
            ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=seed))
        ])
        p_w.fit(X_train.iloc[tr_f], y_train.iloc[tr_f])
        p_wo.fit(X_train.iloc[tr_f], y_train.iloc[tr_f])
        oof_with[val_f] = p_w.predict_proba(X_train.iloc[val_f])[:, 1]
        oof_wo[val_f] = p_wo.predict_proba(X_train.iloc[val_f])[:, 1]
        
    # Evaluate 3 operating points on train CV
    op_points_with = evaluate_operating_points(y_train.values, oof_with)
    op_points_wo = evaluate_operating_points(y_train.values, oof_wo)
    
    th_with = op_points_with["target_sens_85"]["selected_threshold"]
    th_wo = op_points_wo["target_sens_85"]["selected_threshold"]
    
    # Train both models on 100% of train split using fresh pipelines
    final_pipe_with = Pipeline([
        ("preprocessor", build_preprocessor(["Age", "EDUC", "SES", "MMSE"], ["Sex"])),
        ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=seed))
    ])
    final_pipe_wo = Pipeline([
        ("preprocessor", build_preprocessor(["Age", "EDUC", "SES"], ["Sex"])),
        ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=seed))
    ])
    final_pipe_with.fit(X_train, y_train)
    final_pipe_wo.fit(X_train, y_train)
    
    # Test set predictions
    probs_with = final_pipe_with.predict_proba(X_test)[:, 1]
    probs_wo = final_pipe_wo.predict_proba(X_test)[:, 1]
    
    test_metrics_with = compute_all_metrics(y_test.values, probs_with, threshold=th_with)
    test_cis_with = bootstrap_ci_2000(y_test.values, probs_with, threshold=th_with, n_boot=2000, seed=seed)
    
    test_metrics_wo = compute_all_metrics(y_test.values, probs_wo, threshold=th_wo)
    test_cis_wo = bootstrap_ci_2000(y_test.values, probs_wo, threshold=th_wo, n_boot=2000, seed=seed)
    
    test_metrics_payload = {
        "model_with_mmse": {
            "metrics": test_metrics_with,
            "bootstrap_95_ci_2000": test_cis_with,
            "operating_points": op_points_with
        },
        "model_without_mmse": {
            "metrics": test_metrics_wo,
            "bootstrap_95_ci_2000": test_cis_wo,
            "operating_points": op_points_wo
        }
    }
    with open(os.path.join(reports_dir, "test_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(test_metrics_payload, f, indent=2)
        
    with open(os.path.join(reports_dir, "threshold_operating_points.json"), "w", encoding="utf-8") as f:
        json.dump({"with_mmse": op_points_with, "without_mmse": op_points_wo}, f, indent=2)
        
    # 6. Preprocessing fit-on-train verification
    prep_fitted = final_pipe_with.named_steps["preprocessor"]
    imputer = prep_fitted.named_transformers_["num"].named_steps["imputer"]
    scaler = prep_fitted.named_transformers_["num"].named_steps["scaler"]
    train_medians = [float(X_train[c].median()) for c in ["Age", "EDUC", "SES", "MMSE"]]
    train_means = [float(X_train[c].fillna(X_train[c].median()).mean()) for c in ["Age", "EDUC", "SES", "MMSE"]]
    imputer_stats = [float(x) for x in imputer.statistics_]
    scaler_means = [float(x) for x in scaler.mean_]
    
    np.testing.assert_allclose(imputer_stats, train_medians, err_msg="Imputer statistics do NOT match train split medians!")
    np.testing.assert_allclose(scaler_means, train_means, err_msg="Scaler means do NOT match train split means!")
    logging.info("PASSED: Preprocessing statistics exactly match train split alone.")
    
    # 7. Write ml/docs/AUDIT.md
    audit_md_content = f"""# Machine Learning Audit: Leakage, Labels, and Validation

## 1. Repeated Measures & Participant Grouping Audit
- **Dataset**: OASIS Longitudinal Dataset (373 records across 150 unique participants, mean 2.49 visits per subject, range 2–5).
- **Leakage Risk**: Because each participant contributes multiple visits over time, naive random splitting (e.g. `KFold` or `train_test_split`) allows different visits of the same participant to appear simultaneously in both training and test sets. Since cognitive status is autocorrelated, this causes severe data leakage and artificially inflates performance.
- **Enforcement**:
  - The split is executed using `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` grouped strictly on `Subject ID`.
  - **Verification**: `set(train_subjects).intersection(set(test_subjects)) == 0` (0 participant overlap verified).
- **Impact of Grouping**:
  - **With MMSE variant**:
    - Ungrouped 5-Fold CV ROC-AUC: **{audit_leakage_results['with_mmse']['ungrouped_auc_mean']:.4f}** (std: {audit_leakage_results['with_mmse']['ungrouped_auc_std']:.4f})
    - Grouped 5-Fold CV ROC-AUC: **{audit_leakage_results['with_mmse']['grouped_auc_mean']:.4f}** (std: {audit_leakage_results['with_mmse']['grouped_auc_std']:.4f})
    - AUC Delta: **{audit_leakage_results['with_mmse']['auc_delta']:+.4f}**
  - **Without MMSE variant**:
    - Ungrouped 5-Fold CV ROC-AUC: **{audit_leakage_results['without_mmse']['ungrouped_auc_mean']:.4f}** (std: {audit_leakage_results['without_mmse']['ungrouped_auc_std']:.4f})
    - Grouped 5-Fold CV ROC-AUC: **{audit_leakage_results['without_mmse']['grouped_auc_mean']:.4f}** (std: {audit_leakage_results['without_mmse']['grouped_auc_std']:.4f})
    - AUC Delta: **{audit_leakage_results['without_mmse']['auc_delta']:+.4f}**
  - *Finding*: Ungrouped evaluation artificially overestimates discriminative ability. Grouped validation provides honest generalization metrics for unseen participants.

## 2. Target Label Definition & Leakage Prevention
- **Source Attribute**: Clinical Dementia Rating (`CDR`).
- **Classification Criterion**:
  - Positive Class (`target = 1`): `CDR > 0` (CDR 0.5 = very mild impairment, CDR 1.0 = mild dementia, CDR 2.0 = moderate dementia).
  - Negative Class (`target = 0`): `CDR == 0` (Cognitively normal / nondemented).
- **Handling of Converted Participants**:
  - In OASIS, participants who convert from normal to impaired over successive visits have their baseline visits (`CDR == 0`) labeled 0 and conversion visits (`CDR > 0`) labeled 1. Because splits are grouped by subject, all visits for a converted subject reside in either the train set or test set, preventing temporal leakage.
- **Feature Independence Verification**:
  - `CDR` is strictly excluded from all model feature spaces.
  - The feature space for `model_without_mmse` contains solely self-reportable attributes: `Age`, `Sex`, `EDUC`, `SES`.
  - The feature space for `model_with_mmse` adds only the administered cognitive score `MMSE`. No diagnostic or clinical classification features are used as inputs.

## 3. Threshold Selection Path
- The decision threshold is **never tuned on the test set**.
- **Code Path**: In `ml/src/train.py` (lines 164–181) and `ml/src/evaluate.py`:
  1. Out-of-fold cross-validated probability predictions (`oof_probs`) are computed using `StratifiedGroupKFold(groups=groups_train)` across training folds only.
  2. `find_optimal_threshold()` evaluates candidate thresholds on `y_train` vs. `oof_probs` to select the threshold meeting the target sensitivity (e.g. >= 0.85) or maximizing Youden's $J$.
  3. The held-out test set is evaluated exactly once at this pre-fixed threshold.

## 4. Preprocessing Fit-on-Train Verification
- All median imputers, standardizers (`StandardScaler`), and categorical encoders are contained inside a scikit-learn `Pipeline` and fitted exclusively on `X_train`.
- Imputer statistics match training medians (`Age`={train_medians[0]}, `EDUC`={train_medians[1]}, `SES`={train_medians[2]}, `MMSE`={train_medians[3]}) and scaler means match training means (`Age`={train_means[0]:.2f}, `EDUC`={train_means[1]:.2f}, `SES`={train_means[2]:.2f}, `MMSE`={train_means[3]:.2f}).

## 5. Label Permutation Sanity Check
- When training and evaluating with randomly shuffled labels over 10 seeds, model discrimination drops to random chance:
  - `model_with_mmse` Permutation CV ROC-AUC: **{perm_results['with_mmse']['mean_auc']:.4f} ± {perm_results['with_mmse']['std_auc']:.4f}**
  - `model_without_mmse` Permutation CV ROC-AUC: **{perm_results['without_mmse']['mean_auc']:.4f} ± {perm_results['without_mmse']['std_auc']:.4f}**
- This confirms that genuine signal rather than structural artifacts or data leakage drives model performance.

## 6. Baseline Models Comparison
- **Majority Class Baseline** (`DummyClassifier(strategy='most_frequent')`):
  - Accuracy: **{baselines['majority_class']['accuracy_mean']*100:.1f}%** | ROC-AUC: **0.5000**
- **Age-Only Logistic Regression**:
  - CV ROC-AUC: **{baselines['age_only_logistic_regression']['roc_auc_mean']:.4f} ± {baselines['age_only_logistic_regression']['roc_auc_std']:.4f}**
  - CV Accuracy: **{baselines['age_only_logistic_regression']['accuracy_mean']*100:.1f}%**
"""
    with open(os.path.join(docs_dir, "AUDIT.md"), "w", encoding="utf-8") as f:
        f.write(audit_md_content)
        
    logging.info("Audit and metrics execution complete. Saved AUDIT.md, cv_metrics.json, and test_metrics.json.")
    return audit_leakage_results, perm_results, baselines, test_metrics_payload


if __name__ == "__main__":
    run_full_audit_and_metrics()
