"""Figure 17: Class-Wise Diagnostic Performance Breakdown.

Directly adapts and improves upon classical model evaluation charts (e.g. JacobW4's eval_metrics.png),
comparing Precision, Recall (Sensitivity), Specificity, and F1-Score for Class 0 (Cognitively Normal)
vs. Class 1 (Cognitive Risk) with rigorous 95% cluster-bootstrap confidence intervals.
"""
import os
import json
import matplotlib.pyplot as plt
import numpy as np
from .theme import apply_axes_style, add_figure_footer, save_figure_pair


def create_class_metrics_figure(theme: dict, mode: str) -> plt.Figure:
    with open("ml/reports/class_wise_metrics.json", "r") as f:
        data = json.load(f)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.2), facecolor=theme["bg"])
    
    metrics = ["Precision", "Recall / Sens.", "Specificity", "F1-Score"]
    
    # --- SUBPLOT 1: Model With MMSE (Cognitive-Augmented) ---
    apply_axes_style(ax1, theme)
    
    # Data for With MMSE
    c0_w = data["with_mmse"]["class_0_healthy"]
    c1_w = data["with_mmse"]["class_1_risk"]
    
    vals_c0_w = [c0_w["precision"], c0_w["recall_specificity"], c0_w["recall_specificity"], c0_w["f1_score"]]
    err_c0_w_low = [c0_w["precision"] - c0_w["precision_ci"][0], c0_w["recall_specificity"] - c0_w["recall_ci"][0], c0_w["recall_specificity"] - c0_w["recall_ci"][0], c0_w["f1_score"] - c0_w["f1_ci"][0]]
    err_c0_w_high = [c0_w["precision_ci"][1] - c0_w["precision"], c0_w["recall_ci"][1] - c0_w["recall_specificity"], c0_w["recall_ci"][1] - c0_w["recall_specificity"], c0_w["f1_ci"][1] - c0_w["f1_score"]]
    
    vals_c1_w = [c1_w["precision"], c1_w["recall_sensitivity"], c0_w["recall_specificity"], c1_w["f1_score"]]
    err_c1_w_low = [c1_w["precision"] - c1_w["precision_ci"][0], c1_w["recall_sensitivity"] - c1_w["recall_ci"][0], c0_w["recall_specificity"] - c0_w["recall_ci"][0], c1_w["f1_score"] - c1_w["f1_ci"][0]]
    err_c1_w_high = [c1_w["precision_ci"][1] - c1_w["precision"], c1_w["recall_ci"][1] - c1_w["recall_sensitivity"], c0_w["recall_ci"][1] - c0_w["recall_specificity"], c1_w["f1_ci"][1] - c1_w["f1_score"]]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, vals_c0_w, width, yerr=[err_c0_w_low, err_c0_w_high], capsize=4,
                    color=theme["accent_primary"], label="Class 0: Cognitively Normal (N=51)", alpha=0.9, edgecolor=theme["border"])
    bars2 = ax1.bar(x + width/2, vals_c1_w, width, yerr=[err_c1_w_low, err_c1_w_high], capsize=4,
                    color=theme["cyan"], label="Class 1: Cognitive Risk (N=21)", alpha=0.9, edgecolor=theme["border"])
    
    ax1.set_title("Variant B: Cognitive-Augmented (With MMSE)\nOverall Accuracy: 79.2% | Specificity: 74.5% [61.1%, 87.5%]", fontsize=11.5, fontweight="bold", pad=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics, fontsize=10.5, fontweight="bold")
    ax1.set_ylabel("Score (0.0 to 1.0)", fontsize=11)
    ax1.set_ylim(0.0, 1.15)
    ax1.legend(loc="upper right", framealpha=0.85, facecolor=theme["card_bg"], edgecolor=theme["border"], fontsize=9)
    
    for b in bars1 + bars2:
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width()/2, h + 0.03, f"{h*100:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=theme["text"])

    # Callout in subplot 1
    ax1.text(0.5, 0.05, "With MMSE: High Specificity (74.5%) prevents false alarms",
             ha="center", fontsize=9, fontweight="bold", color=theme["success"],
             transform=ax1.transAxes,
             bbox=dict(boxstyle="round,pad=0.3", fc=theme["card_bg"], ec=theme["success"], lw=0.9))

    # --- SUBPLOT 2: Model Without MMSE (Demographics Only) ---
    apply_axes_style(ax2, theme)
    
    c0_wo = data["without_mmse"]["class_0_healthy"]
    c1_wo = data["without_mmse"]["class_1_risk"]
    
    vals_c0_wo = [c0_wo["precision"], c0_wo["recall_specificity"], c0_wo["recall_specificity"], c0_wo["f1_score"]]
    err_c0_wo_low = [c0_wo["precision"] - c0_wo["precision_ci"][0], c0_wo["recall_specificity"] - c0_wo["recall_ci"][0], c0_wo["recall_specificity"] - c0_wo["recall_ci"][0], c0_wo["f1_score"] - c0_wo["f1_ci"][0]]
    err_c0_wo_high = [c0_wo["precision_ci"][1] - c0_wo["precision"], c0_wo["recall_ci"][1] - c0_wo["recall_specificity"], c0_wo["recall_ci"][1] - c0_wo["recall_specificity"], c0_wo["f1_ci"][1] - c0_wo["f1_score"]]
    
    vals_c1_wo = [c1_wo["precision"], c1_wo["recall_sensitivity"], c0_wo["recall_specificity"], c1_wo["f1_score"]]
    err_c1_wo_low = [c1_wo["precision"] - c1_wo["precision_ci"][0], c1_wo["recall_sensitivity"] - c1_wo["recall_ci"][0], c0_wo["recall_specificity"] - c0_wo["recall_ci"][0], c1_wo["f1_score"] - c1_wo["f1_ci"][0]]
    err_c1_wo_high = [c1_wo["precision_ci"][1] - c1_wo["precision"], c1_wo["recall_ci"][1] - c1_wo["recall_sensitivity"], c0_wo["recall_ci"][1] - c0_wo["recall_specificity"], c1_wo["f1_ci"][1] - c1_wo["f1_score"]]
    
    bars3 = ax2.bar(x - width/2, vals_c0_wo, width, yerr=[err_c0_wo_low, err_c0_wo_high], capsize=4,
                    color=theme["baseline"], label="Class 0: Cognitively Normal (N=51)", alpha=0.9, edgecolor=theme["border"])
    bars4 = ax2.bar(x + width/2, vals_c1_wo, width, yerr=[err_c1_wo_low, err_c1_wo_high], capsize=4,
                    color=theme["accent_secondary"], label="Class 1: Cognitive Risk (N=21)", alpha=0.9, edgecolor=theme["border"])
    
    ax2.set_title("Variant A: Demographic Baseline (Without MMSE)\nOverall Accuracy: 51.4% | Specificity: 35.3% [14.8%, 57.7%]", fontsize=11.5, fontweight="bold", pad=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(metrics, fontsize=10.5, fontweight="bold")
    ax2.set_ylabel("Score (0.0 to 1.0)", fontsize=11)
    ax2.set_ylim(0.0, 1.15)
    ax2.legend(loc="upper right", framealpha=0.85, facecolor=theme["card_bg"], edgecolor=theme["border"], fontsize=9)
    
    for b in bars3 + bars4:
        h = b.get_height()
        ax2.text(b.get_x() + b.get_width()/2, h + 0.03, f"{h*100:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=theme["text"])

    # Callout in subplot 2
    ax2.text(0.5, 0.05, "Without MMSE: High Sensitivity (90.0%), Low Specificity (~35%)",
             ha="center", fontsize=9, fontweight="bold", color=theme["accent_secondary"],
             transform=ax2.transAxes,
             bbox=dict(boxstyle="round,pad=0.3", fc=theme["card_bg"], ec=theme["accent_secondary"], lw=0.9))

    add_figure_footer(
        fig, theme,
        dataset="OASIS-1 Held-out Test Set (N=72 visits, 30 subjects, 2,000 Cluster Bootstrap Resamples)",
        disclaimer="Error bars represent 95% participant-clustered bootstrap CIs | Screening demonstration only"
    )
    plt.tight_layout(rect=[0.02, 0.05, 0.98, 0.96])
    return fig


def run(output_dir="docs/showcase/figures", data_dir="docs/showcase/data"):
    with open("ml/reports/class_wise_metrics.json", "r") as f:
        data = json.load(f)
    return save_figure_pair(
        create_class_metrics_figure,
        "17_class_wise_evaluation",
        data_payload=data,
        output_dir=output_dir,
        data_dir=data_dir
    )


generate = run


if __name__ == "__main__":
    run()
