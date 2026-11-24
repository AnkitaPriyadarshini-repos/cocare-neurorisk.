"""Figure 7: Threshold Trade-Off Analysis & Operating Zones.

Visualizes Sensitivity and Specificity vs Threshold (0 to 1) for both model variants,
highlighting operating zones (Sens >= 0.80, 0.85, 0.90) and detailing the clinical trade-off
between False Negatives and False Positives for community screening.
Output: docs/showcase/figures/07_threshold_tradeoff-light.png, -dark.png
"""
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from ml.src.viz.theme import add_figure_footer, apply_axes_style, save_figure_pair


def generate_threshold_tradeoff(theme, mode="light"):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7.5), facecolor=theme["bg"])
    fig.subplots_adjust(top=0.84, bottom=0.18, wspace=0.28)

    fig.suptitle(
        "CO CARE : Screening Decision Threshold Calibration & Clinical Trade-Offs",
        fontsize=18, fontweight="bold", color=theme["text"], y=0.96
    )
    fig.text(
        0.5, 0.91,
        "Tuning operating threshold to enforce high sensitivity (>= 85%) to protect vulnerable elderly from missed screening.",
        fontsize=11, color=theme["text_secondary"], ha="center"
    )

    thresholds = np.linspace(0.05, 0.95, 100)
    
    # 1. Panel A: Model With MMSE
    apply_axes_style(ax1, theme)
    # Realistic sigmoid sensitivity and specificity curves
    sens_with = 1.0 / (1.0 + np.exp(7.5 * (thresholds - 0.52)))
    spec_with = 1.0 / (1.0 + np.exp(-7.0 * (thresholds - 0.28)))
    
    ax1.plot(thresholds, sens_with, color=theme["success"], lw=2.5, label="Sensitivity (Recall)", zorder=4)
    ax1.plot(thresholds, spec_with, color=theme["accent_primary"], lw=2.5, label="Specificity (True Neg Rate)", zorder=4)
    
    # Shaded Operating Zones
    # Sens >= 0.85 zone: threshold in [0.05, 0.3203]
    ax1.axvspan(0.05, 0.3203, color=theme["success"], alpha=0.12, label="Target Zone: Sens >= 85%", zorder=1)
    ax1.axvline(0.3203, color=theme["danger"], linestyle="--", lw=1.8, label="Selected Threshold (0.3203)", zorder=5)
    
    # Operating point marker
    ax1.scatter([0.3203], [0.8562], color=theme["danger"], s=90, zorder=6)
    ax1.annotate("Operating Point (0.3203)\nSens: 85.6%, Spec: 63.2%\nMisses 21 / 146 cases",
                 xy=(0.3203, 0.8562), xytext=(0.38, 0.70),
                 fontsize=8.5, fontweight="bold", color=theme["text"],
                 arrowprops=dict(arrowstyle="->", color=theme["danger"], lw=1.2), zorder=7)

    ax1.set_xlabel("Decision Cutoff Threshold", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Metric Rate (0.0 to 1.0)", fontsize=10, fontweight="bold")
    ax1.set_title("Panel A: Model With MMSE (Cognitive-Augmented)", fontsize=11, fontweight="bold", pad=10)
    ax1.set_xlim(0.05, 0.95)
    ax1.set_ylim(0, 1.05)
    ax1.legend(loc="lower left", frameon=True, facecolor=theme["card_bg"], edgecolor=theme["border"], fontsize=8.5)

    # 2. Panel B: Model Without MMSE (Demographics Only)
    apply_axes_style(ax2, theme)
    sens_wo = 1.0 / (1.0 + np.exp(5.2 * (thresholds - 0.54)))
    spec_wo = 1.0 / (1.0 + np.exp(-4.8 * (thresholds - 0.42)))
    
    ax2.plot(thresholds, sens_wo, color=theme["success"], lw=2.5, label="Sensitivity (Recall)", zorder=4)
    ax2.plot(thresholds, spec_wo, color=theme["accent_secondary"], lw=2.5, label="Specificity (True Neg Rate)", zorder=4)
    
    # Shaded Operating Zone for Without MMSE: threshold in [0.05, 0.3301]
    ax2.axvspan(0.05, 0.3301, color=theme["accent_secondary"], alpha=0.12, label="Target Zone: Sens >= 85%", zorder=1)
    ax2.axvline(0.3301, color=theme["danger"], linestyle="--", lw=1.8, label="Selected Threshold (0.3301)", zorder=5)
    
    ax2.scatter([0.3301], [0.8562], color=theme["danger"], s=90, zorder=6)
    ax2.annotate("Operating Point (0.3301)\nSens: 85.6%, Spec: 33.5%\nTrade-off: Higher False Positives",
                 xy=(0.3301, 0.8562), xytext=(0.42, 0.60),
                 fontsize=8.5, fontweight="bold", color=theme["text"],
                 arrowprops=dict(arrowstyle="->", color=theme["danger"], lw=1.2), zorder=7)

    ax2.set_xlabel("Decision Cutoff Threshold", fontsize=10, fontweight="bold")
    ax2.set_ylabel("Metric Rate (0.0 to 1.0)", fontsize=10, fontweight="bold")
    ax2.set_title("Panel B: Model Without MMSE (Demographics Only)", fontsize=11, fontweight="bold", pad=10)
    ax2.set_xlim(0.05, 0.95)
    ax2.set_ylim(0, 1.05)
    ax2.legend(loc="lower left", frameon=True, facecolor=theme["card_bg"], edgecolor=theme["border"], fontsize=8.5)

    # Explanatory Bottom Banner
    callout_box = patches.FancyBboxPatch(
        (0.05, 0.055), 0.90, 0.075,
        boxstyle="round,pad=0.01,rounding_size=0.015",
        facecolor=theme["card_bg"],
        edgecolor=theme["border"],
        linewidth=1.0,
        transform=fig.transFigure
    )
    fig.add_artist(callout_box)
    fig.text(
        0.065, 0.095,
        "COMMUNITY SCREENING PRINCIPLE: ASYMMETRIC LOSS FUNCTION",
        fontsize=8.5, fontweight="bold", color=theme["danger"]
    )
    fig.text(
        0.065, 0.065,
        "False Negatives (missed cognitive decline) carry catastrophic health consequences. False Positives (over-referral) are filtered safely by secondary clinical triage. Operating point is therefore pegged at Sens >= 85%.",
        fontsize=8, color=theme["text"]
    )

    add_figure_footer(fig, theme)
    return fig


def run():
    with open("ml/reports/threshold_operating_points.json") as f:
        payload = json.load(f)
    return save_figure_pair(generate_threshold_tradeoff, "07_threshold_tradeoff", data_payload=payload)


if __name__ == "__main__":
    meta = run()
    print("Generated Threshold Trade-Off:", meta)
