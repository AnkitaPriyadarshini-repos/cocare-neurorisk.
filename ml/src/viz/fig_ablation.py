"""Figure 10: Ablation / Value-Added Progression Analysis.

Stepped progression chart demonstrating marginal value added across feature subsets:
1. Majority Class Baseline
2. Age-Only Logistic Regression
3. Demographics Only (Age, Sex, Education, SES)
4. Demographics + Cognitive Test (+ MMSE)
Clearly highlights that MMSE drives dominant ~0.24-0.25 AUC lift.
Output: docs/showcase/figures/10_ablation_value_added-light.png, -dark.png
"""
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from ml.src.viz.theme import add_figure_footer, apply_axes_style, save_figure_pair


def generate_ablation(theme, mode="light"):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.8), facecolor=theme["bg"])
    fig.subplots_adjust(top=0.86, bottom=0.12, wspace=0.28)

    fig.suptitle(
        "CO CARE : Feature Ablation & Marginal Value-Added Analysis",
        fontsize=18, fontweight="bold", color=theme["text"], y=0.96
    )
    fig.text(
        0.5, 0.91,
        "Quantifying the incremental discriminative contribution of cognitive testing over demographic baseline.",
        fontsize=11, color=theme["text_secondary"], ha="center"
    )

    stages = [
        "Majority Class\nBaseline",
        "Age-Only\nLogistic Reg.",
        "Demographics Only\n(Age, Sex, Educ, SES)",
        "Demographics +\nCognitive Test (+MMSE)"
    ]

    # Panel A: ROC-AUC Progression
    apply_axes_style(ax1, theme)
    
    cv_auc = [0.500, 0.434, 0.654, 0.892]
    cv_err = [0.000, 0.063, 0.062, 0.041]
    test_auc = [0.500, 0.450, 0.679, 0.929]
    
    x = np.arange(len(stages))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, cv_auc, width, yerr=[1.96*e for e in cv_err], capsize=4,
                    label="Primary 5x5 Group CV AUC (Mean ± 95% CI)", color=theme["accent_secondary"], edgecolor=theme["border"], zorder=3)
    bars2 = ax1.bar(x + width/2, test_auc, width,
                    label="Held-Out Test Set AUC", color=theme["accent_primary"], edgecolor=theme["border"], zorder=3)
    
    # Delta annotation between Demographics and +MMSE
    ax1.annotate(
        "Dominant Lift:\n+0.238 CV AUC\n(+0.250 Test AUC)",
        xy=(3 - width/2, 0.892), xytext=(2 - width/2, 0.78),
        fontsize=8.5, fontweight="bold", color=theme["success"],
        arrowprops=dict(arrowstyle="->", color=theme["success"], lw=1.5),
        bbox=dict(boxstyle="square,pad=0.3", fc=theme["card_bg"], ec=theme["success"], lw=0.8),
        zorder=5
    )
    
    # Chance baseline
    ax1.axhline(0.50, color=theme["baseline"], linestyle="--", lw=1.0, zorder=2)
    
    ax1.set_xticks(x)
    ax1.set_xticklabels(stages, fontsize=8.5, fontweight="bold")
    ax1.set_ylabel("ROC-AUC Score", fontsize=10, fontweight="bold")
    ax1.set_title("Panel A: Incremental Area Under the ROC Curve (AUC)", fontsize=11, fontweight="bold", pad=10)
    ax1.set_ylim(0, 1.08)
    ax1.legend(loc="upper left", frameon=True, facecolor=theme["card_bg"], edgecolor=theme["border"], fontsize=8.5)
    
    for bar in bars1:
        h = bar.get_height()
        if h > 0:
            ax1.text(bar.get_x() + bar.get_width()/2, h + 0.04, f"{h:.3f}", ha="center", fontsize=8, fontweight="bold", color=theme["text"])
    for bar in bars2:
        h = bar.get_height()
        if h > 0:
            ax1.text(bar.get_x() + bar.get_width()/2, h + 0.04, f"{h:.3f}", ha="center", fontsize=8, fontweight="bold", color=theme["text"])

    # Panel B: Sensitivity at Fixed High Specificity (>= 75%)
    apply_axes_style(ax2, theme)
    
    # Sensitivity achieved when holding Specificity at ~75%
    sens_at_spec = [0.00, 0.15, 0.42, 0.905]
    colors_sens = [theme["baseline"], theme["baseline"], theme["accent_secondary"], theme["success"]]
    bars3 = ax2.bar(stages, sens_at_spec, width=0.55, color=colors_sens, edgecolor=theme["border"], zorder=3)
    
    ax2.set_ylabel("Sensitivity (Recall at Specificity >= 75%)", fontsize=10, fontweight="bold")
    ax2.set_title("Panel B: Clinical Sensitivity at High Operating Specificity", fontsize=11, fontweight="bold", pad=10)
    ax2.set_ylim(0, 1.10)
    ax2.set_xticks(range(len(stages)))
    ax2.set_xticklabels(stages, fontsize=8.5, fontweight="bold")
    
    for bar, val in zip(bars3, sens_at_spec):
        pct_text = f"{val*100:.1f}%" if val > 0 else "0.0%"
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03, pct_text, ha="center", fontsize=9, fontweight="bold", color=theme["text"])

    ax2.text(
        0.5, 0.45,
        "TAKEAWAY:\nSelf-reportable demographics provide basic community risk prior (AUC 0.654),\nbut brief cognitive assessment (MMSE/HMSE) is strictly necessary to achieve\nhigh sensitivity (90.5%) without flooding secondary care with false alarms.",
        transform=ax2.transAxes, ha="center", va="center", fontsize=8.5,
        bbox=dict(boxstyle="round,pad=0.5", fc=theme["card_bg"], ec=theme["border"], lw=1.0)
    )

    add_figure_footer(fig, theme)
    return fig


def run():
    payload = {
        "ablation_stages": [
            {"stage": "Majority Class", "cv_auc": 0.500, "test_auc": 0.500},
            {"stage": "Age-Only Logistic", "cv_auc": 0.434, "test_auc": 0.450},
            {"stage": "Demographics Only", "cv_auc": 0.654, "test_auc": 0.679},
            {"stage": "Demographics + MMSE", "cv_auc": 0.892, "test_auc": 0.929}
        ],
        "marginal_lift_from_mmse": 0.2375
    }
    return save_figure_pair(generate_ablation, "10_ablation_value_added", data_payload=payload)


if __name__ == "__main__":
    meta = run()
    print("Generated Ablation:", meta)
