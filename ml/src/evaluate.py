"""Model evaluation with bootstrap confidence intervals and threshold optimization."""
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import (
    recall_score,
    precision_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    accuracy_score,
    confusion_matrix,
    brier_score_loss,
    roc_curve
)


def compute_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.5
) -> Dict[str, float]:
    """Compute sensitivity, specificity, precision, F1, ROC-AUC, PR-AUC, accuracy, Brier."""
    y_pred = (y_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    precision = precision_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    accuracy = accuracy_score(y_true, y_pred)
    brier = brier_score_loss(y_true, y_prob)

    try:
        roc_auc = roc_auc_score(y_true, y_prob)
    except Exception:
        roc_auc = 0.5

    try:
        pr_auc = average_precision_score(y_true, y_prob)
    except Exception:
        pr_auc = 0.0

    return {
        "sensitivity": float(sensitivity),
        "specificity": float(specificity),
        "precision": float(precision),
        "f1": float(f1),
        "accuracy": float(accuracy),
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
        "brier_score": float(brier),
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn)
    }


def find_optimal_threshold(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    target_sensitivity: float = 0.85
) -> float:
    """Find decision threshold targeting >= target_sensitivity (or Youden's J).

    For screening, false negatives are more harmful than false positives.
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)

    # First attempt: find threshold where sensitivity >= target_sensitivity with max specificity
    candidates = []
    for t in thresholds:
        if 0.0 < t < 1.0:
            m = compute_metrics(y_true, y_prob, threshold=t)
            if m["sensitivity"] >= target_sensitivity:
                candidates.append((m["specificity"], t))

    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return float(candidates[0][1])

    # Fallback: Youden's J statistic (sensitivity + specificity - 1)
    j_scores = tpr - fpr
    best_idx = np.argmax(j_scores)
    best_t = thresholds[best_idx]
    return float(np.clip(best_t, 0.1, 0.9))


def bootstrap_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float,
    n_bootstraps: int = 1000,
    seed: int = 42
) -> Dict[str, Dict[str, float]]:
    """Compute 95% bootstrap confidence intervals for all metrics."""
    rng = np.random.RandomState(seed)
    n_samples = len(y_true)
    bootstrapped_metrics = {
        "sensitivity": [],
        "specificity": [],
        "precision": [],
        "f1": [],
        "accuracy": [],
        "roc_auc": [],
        "pr_auc": []
    }

    for _ in range(n_bootstraps):
        indices = rng.randint(0, n_samples, n_samples)
        if len(np.unique(y_true[indices])) < 2:
            continue
        m = compute_metrics(y_true[indices], y_prob[indices], threshold)
        for k in bootstrapped_metrics:
            bootstrapped_metrics[k].append(m[k])

    summary = {}
    for k, values in bootstrapped_metrics.items():
        if len(values) > 0:
            summary[k] = {
                "mean": float(np.mean(values)),
                "ci_lower": float(np.percentile(values, 2.5)),
                "ci_upper": float(np.percentile(values, 97.5))
            }
        else:
            summary[k] = {"mean": 0.0, "ci_lower": 0.0, "ci_upper": 0.0}

    return summary
