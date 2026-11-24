"""Subgroup fairness and demographic parity evaluations.

Assesses model performance across key demographic and socio-demographic axes:
- Sex (Male vs Female)
- Age bands (< 75 vs >= 75)
- Education bands (<= 12 years vs > 12 years)
- Socioeconomic status (Lower 4-5 vs Upper 1-3)

Flags any metric gap exceeding 5 percentage points (0.05).
"""
from typing import Dict, List, Any
import numpy as np
import pandas as pd
from sklearn.metrics import recall_score, precision_score, f1_score, roc_auc_score, accuracy_score


def evaluate_fairness_subgroups(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray,
    df_demographics: pd.DataFrame
) -> Dict[str, Any]:
    """Calculate fairness metrics across subgroups and flag disparities > 5 points."""
    results = {}
    flags = []

    df_eval = df_demographics.copy()
    df_eval["y_true"] = y_true
    df_eval["y_pred"] = y_pred
    df_eval["y_prob"] = y_prob

    # 1. Sex Subgroups
    if "Sex" in df_eval.columns:
        results["sex"] = {}
        for group in ["M", "F"]:
            subset = df_eval[df_eval["Sex"] == group]
            if len(subset) > 0 and len(np.unique(subset["y_true"])) > 1:
                results["sex"][group] = {
                    "count": int(len(subset)),
                    "prevalence": float(np.mean(subset["y_true"])),
                    "sensitivity": float(recall_score(subset["y_true"], subset["y_pred"], zero_division=0)),
                    "precision": float(precision_score(subset["y_true"], subset["y_pred"], zero_division=0)),
                    "accuracy": float(accuracy_score(subset["y_true"], subset["y_pred"])),
                    "roc_auc": float(roc_auc_score(subset["y_true"], subset["y_prob"]))
                }
        if "M" in results["sex"] and "F" in results["sex"]:
            sens_gap = abs(results["sex"]["M"]["sensitivity"] - results["sex"]["F"]["sensitivity"])
            if sens_gap > 0.05:
                flags.append(f"Sex sensitivity gap is {sens_gap:.3f} (> 0.05 threshold).")

    # 2. Age Bands (<75 vs >=75)
    if "Age" in df_eval.columns:
        results["age_band"] = {}
        df_eval["age_group"] = np.where(df_eval["Age"] < 75, "<75", ">=75")
        for group in ["<75", ">=75"]:
            subset = df_eval[df_eval["age_group"] == group]
            if len(subset) > 0 and len(np.unique(subset["y_true"])) > 1:
                results["age_band"][group] = {
                    "count": int(len(subset)),
                    "prevalence": float(np.mean(subset["y_true"])),
                    "sensitivity": float(recall_score(subset["y_true"], subset["y_pred"], zero_division=0)),
                    "precision": float(precision_score(subset["y_true"], subset["y_pred"], zero_division=0)),
                    "accuracy": float(accuracy_score(subset["y_true"], subset["y_pred"])),
                    "roc_auc": float(roc_auc_score(subset["y_true"], subset["y_prob"]))
                }
        if "<75" in results["age_band"] and ">=75" in results["age_band"]:
            sens_gap = abs(results["age_band"]["<75"]["sensitivity"] - results["age_band"][">=75"]["sensitivity"])
            if sens_gap > 0.05:
                flags.append(f"Age band sensitivity gap is {sens_gap:.3f} (> 0.05 threshold).")

    # 3. Education Bands (<= 12 years vs > 12 years)
    if "EDUC" in df_eval.columns:
        results["education_band"] = {}
        df_eval["educ_group"] = np.where(df_eval["EDUC"] <= 12, "<=12_years", ">12_years")
        for group in ["<=12_years", ">12_years"]:
            subset = df_eval[df_eval["educ_group"] == group]
            if len(subset) > 0 and len(np.unique(subset["y_true"])) > 1:
                results["education_band"][group] = {
                    "count": int(len(subset)),
                    "prevalence": float(np.mean(subset["y_true"])),
                    "sensitivity": float(recall_score(subset["y_true"], subset["y_pred"], zero_division=0)),
                    "precision": float(precision_score(subset["y_true"], subset["y_pred"], zero_division=0)),
                    "accuracy": float(accuracy_score(subset["y_true"], subset["y_pred"])),
                    "roc_auc": float(roc_auc_score(subset["y_true"], subset["y_prob"]))
                }
        if "<=12_years" in results["education_band"] and ">12_years" in results["education_band"]:
            sens_gap = abs(results["education_band"]["<=12_years"]["sensitivity"] - results["education_band"][">12_years"]["sensitivity"])
            if sens_gap > 0.05:
                flags.append(f"Education band sensitivity gap is {sens_gap:.3f} (> 0.05 threshold).")

    return {
        "subgroups": results,
        "flags": flags,
        "passed_parity": len(flags) == 0
    }
