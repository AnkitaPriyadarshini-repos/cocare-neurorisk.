"""Figure 13: Sample Efficiency Learning Curve & LASI-DAD Scaling Motivation.

Plots Stratified Group CV ROC-AUC and Brier Score as a function of training sample size (N=50 to 301).
Demonstrates sample efficiency plateau for demographic-only model and motivates transition to LASI-DAD (N~3000+).
Output: docs/showcase/figures/13_learning_curve-light.png, -dark.png
"""
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from ml.src.viz.theme import add_figure_footer, apply_axes_style, save_figure_pair


def generate_learning_curve(theme, mode="light"):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.8), facecolor=theme["bg"])
    fig.subplots_adjust(top=0.86, bottom=0.12, wspace=0.28)

    fig.suptitle(
        "CO CARE : Sample Efficiency Learning Curve & LASI-DAD Scaling Motivation",
        fontsize=18, fontweight="bold", color=theme["text"], y=0.96
    )
    fig.text(
        0.5, 0.91,
        "Tracking model convergence across training sample sizes (N=50 to 301) to identify capacity bottlenecks.",
        fontsize=11, color=theme["text_secondary"], ha="center"
    )

    with open("ml/reports/learning_curve.json") as f:
        lc_data = json.load(f)
        
    sizes = np.array(lc_data["sample_sizes"])
    
    # 1. Panel A: ROC-AUC vs Training Set Size
    apply_axes_style(ax1, theme)
    
    auc_w_mean = np.array(lc_data["with_mmse"]["roc_auc_mean"])
    auc_w_std  = np.array(lc_data["with_mmse"]["roc_auc_std"])
    auc_wo_mean = np.array(lc_data["without_mmse"]["roc_auc_mean"])
    auc_wo_std  = np.array(lc_data["without_mmse"]["roc_auc_std"])
    
    # Plot With MMSE
    ax1.plot(sizes, auc_w_mean, marker='o', lw=2.5, color=theme["accent_primary"], label="With MMSE (CV ROC-AUC)", zorder=4)
    ax1.fill_between(sizes, auc_w_mean - 1.96*auc_w_std, auc_w_mean + 1.96*auc_w_std, color=theme["accent_primary"], alpha=0.15, zorder=2)
    
    # Plot Without MMSE
    ax1.plot(sizes, auc_wo_mean, marker='s', lw=2.2, color=theme["accent_secondary"], label="Without MMSE (Demographics Only)", zorder=4)
    ax1.fill_between(sizes, auc_wo_mean - 1.96*auc_wo_std, auc_wo_mean + 1.96*auc_wo_std, color=theme["accent_secondary"], alpha=0.15, zorder=2)
    
    # Scaling projection arrow citing LASI-DAD protocol
    ax1.annotate(
        "LASI-DAD Target Cohort\n(Lee et al., 2020; Bloom et al., 2021)\nTarget N~3,137 (Access agreement pending)\nProjected Demographics Power Lift",
        xy=(301, 0.655), xytext=(170, 0.50),
        fontsize=8.5, fontweight="bold", color=theme["success"],
        arrowprops=dict(arrowstyle="->", color=theme["success"], lw=1.5),
        bbox=dict(boxstyle="square,pad=0.3", fc=theme["card_bg"], ec=theme["success"], lw=0.8),
        zorder=5
    )

    ax1.set_xticks(sizes)
    ax1.set_xticklabels(["50\n(~20 subj)", "100\n(~40 subj)", "150\n(~60 subj)", "200\n(~80 subj)", "250\n(~100 subj)", "301\n(120 subj)"], fontsize=8.5)
    ax1.set_xlabel("Training Set Size: Visits [Approx. Participants]", fontsize=10, fontweight="bold")
    ax1.set_ylabel("5-Fold Stratified Group CV ROC-AUC", fontsize=10, fontweight="bold")
    ax1.set_title("Panel A: Discriminative Convergence Trajectory", fontsize=11, fontweight="bold", pad=10)
    ax1.set_xlim(35, 325)
    ax1.set_ylim(0.45, 0.98)
    ax1.legend(loc="lower right", frameon=True, facecolor=theme["card_bg"], edgecolor=theme["border"], fontsize=8.5)

    # 2. Panel B: Calibration Loss (Brier Score)
    apply_axes_style(ax2, theme)
    
    brier_w = np.array(lc_data["with_mmse"]["brier_score_mean"])
    brier_wo = np.array(lc_data["without_mmse"]["brier_score_mean"])
    
    ax2.plot(sizes, brier_w, marker='o', lw=2.5, color=theme["accent_primary"], label="With MMSE (Brier Score)", zorder=4)
    ax2.plot(sizes, brier_wo, marker='s', lw=2.2, color=theme["accent_secondary"], label="Without MMSE (Brier Score)", zorder=4)
    
    # Baseline line
    ax2.axhline(0.252, color=theme["baseline"], linestyle="--", lw=1.2, label="Prevalence Baseline (0.252)", zorder=2)
    
    ax2.set_xticks(sizes)
    ax2.set_xticklabels(["50\n(~20 subj)", "100\n(~40 subj)", "150\n(~60 subj)", "200\n(~80 subj)", "250\n(~100 subj)", "301\n(120 subj)"], fontsize=8.5)
    ax2.set_xlabel("Training Set Size: Visits [Approx. Participants]", fontsize=10, fontweight="bold")
    ax2.set_ylabel("Mean Brier Score (Lower is Better)", fontsize=10, fontweight="bold")
    ax2.set_title("Panel B: Calibration Error vs Sample Size", fontsize=11, fontweight="bold", pad=10)
    ax2.set_xlim(40, 320)
    ax2.set_ylim(0.08, 0.30)
    ax2.legend(loc="upper right", frameon=True, facecolor=theme["card_bg"], edgecolor=theme["border"], fontsize=8.5)

    add_figure_footer(fig, theme)
    return fig


def run():
    with open("ml/reports/learning_curve.json") as f:
        payload = json.load(f)
    return save_figure_pair(generate_learning_curve, "13_learning_curve", data_payload=payload)


if __name__ == "__main__":
    meta = run()
    print("Generated Learning Curve:", meta)
