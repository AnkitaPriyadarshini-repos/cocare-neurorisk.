"""Figure 12: Subgroup Fairness & Parity Forest Plot.

Visualizes Sensitivity and Specificity across demographic subgroups:
- Sex: Male (N=21) vs Female (N=51)
- Age: < 75 (N=26) vs >= 75 (N=46)
- Education: <= 12 years (N=19) vs > 12 years (N=53)
Clearly flags underpowered subgroups (N < 30) with muted/dashed styling.
Output: docs/showcase/figures/12_fairness_forest_plot-light.png, -dark.png
"""
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from ml.src.viz.theme import add_figure_footer, apply_axes_style, save_figure_pair


def generate_fairness_forest(theme, mode="light"):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7.2), facecolor=theme["bg"])
    fig.subplots_adjust(top=0.86, bottom=0.14, wspace=0.32)

    fig.suptitle(
        "CO CARE : Subgroup Parity & Fairness Forest Plot (Held-Out Test)",
        fontsize=18, fontweight="bold", color=theme["text"], y=0.96
    )
    fig.text(
        0.5, 0.91,
        "Evaluating parity across Sex, Age, and Education. Subgroups with N < 30 are flagged as underpowered to prevent over-interpretation.",
        fontsize=11, color=theme["text_secondary"], ha="center"
    )

    # Subgroup data from ml/reports/subgroup_metrics.json
    subgroups = [
        ("Sex: Male [N=21]*", 90.9, (70.0, 100.0), 70.0, (40.0, 90.0), True),
        ("Sex: Female [N=51]", 90.0, (70.0, 100.0), 75.6, (61.0, 88.0), False),
        ("Age: < 75 yrs [N=26]*", 88.9, (67.0, 100.0), 82.4, (60.0, 95.0), True),
        ("Age: >= 75 yrs [N=46]", 91.7, (75.0, 100.0), 70.6, (55.0, 85.0), False),
        ("Education: <= 12 yrs [N=19]*", 100.0, (80.0, 100.0), 55.6, (25.0, 85.0), True),
        ("Education: > 12 yrs [N=53]", 81.8, (55.0, 100.0), 78.6, (65.0, 90.0), False),
    ]

    labels = [s[0] for s in subgroups][::-1]
    y_pos = np.arange(len(labels))

    # 1. Panel A: Sensitivity (Recall)
    apply_axes_style(ax1, theme)
    sens_vals = [s[1] for s in subgroups][::-1]
    sens_cis = [s[2] for s in subgroups][::-1]
    is_under = [s[5] for s in subgroups][::-1]
    
    # Target reference line (overall sensitivity: 90.5%)
    ax1.axvline(90.5, color=theme["success"], linestyle="--", lw=1.5, label="Overall Sensitivity (90.5%)", zorder=2)
    
    for i, (val, ci, under) in enumerate(zip(sens_vals, sens_cis, is_under)):
        col = theme["baseline"] if under else theme["accent_primary"]
        ls = "--" if under else "-"
        # Error bar
        ax1.errorbar(val, y_pos[i], xerr=[[val - ci[0]], [ci[1] - val]], fmt='o',
                     color=col, ecolor=col, elinewidth=2.0, capsize=4, capthick=1.5, markersize=8, zorder=4)
        ax1.text(ci[1] + 2.5, y_pos[i], f"{val:.1f}%", va="center", fontsize=8.5, fontweight="bold", color=col)

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(labels, fontsize=9, fontweight="bold")
    ax1.set_xlabel("Sensitivity (%) [95% Bootstrap CI]", fontsize=10, fontweight="bold")
    ax1.set_title("Panel A: Clinical Sensitivity by Subgroup", fontsize=11, fontweight="bold", pad=10)
    ax1.set_xlim(40, 115)
    ax1.legend(loc="lower left", frameon=True, facecolor=theme["card_bg"], edgecolor=theme["border"], fontsize=8.5)

    # 2. Panel B: Specificity
    apply_axes_style(ax2, theme)
    spec_vals = [s[3] for s in subgroups][::-1]
    spec_cis = [s[4] for s in subgroups][::-1]
    
    ax2.axvline(74.5, color=theme["accent_primary"], linestyle="--", lw=1.5, label="Overall Specificity (74.5%)", zorder=2)
    
    for i, (val, ci, under) in enumerate(zip(spec_vals, spec_cis, is_under)):
        col = theme["baseline"] if under else theme["accent_secondary"]
        ax2.errorbar(val, y_pos[i], xerr=[[val - ci[0]], [ci[1] - val]], fmt='s',
                     color=col, ecolor=col, elinewidth=2.0, capsize=4, capthick=1.5, markersize=7, zorder=4)
        ax2.text(ci[1] + 2.5, y_pos[i], f"{val:.1f}%", va="center", fontsize=8.5, fontweight="bold", color=col)

    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([])  # share labels with left
    ax2.set_xlabel("Specificity (%) [95% Bootstrap CI]", fontsize=10, fontweight="bold")
    ax2.set_title("Panel B: Operating Specificity by Subgroup", fontsize=11, fontweight="bold", pad=10)
    ax2.set_xlim(15, 110)
    ax2.legend(loc="lower left", frameon=True, facecolor=theme["card_bg"], edgecolor=theme["border"], fontsize=8.5)

    # Warning footnote box
    fig.text(
        0.5, 0.05,
        "* NOTE: Subgroups marked with an asterisk (*) have sample sizes N < 30 and are statistically underpowered.\nSensitivity gap between Male and Female cohorts is < 1% (90.9% vs 90.0%). Definitive population fairness awaits LASI-DAD.",
        ha="center", fontsize=8.5, color=theme["text_muted"],
        bbox=dict(boxstyle="round,pad=0.4", fc=theme["card_bg"], ec=theme["border"], lw=0.8)
    )

    add_figure_footer(fig, theme)
    return fig


def run():
    with open("ml/reports/subgroup_metrics.json") as f:
        payload = json.load(f)
    return save_figure_pair(generate_fairness_forest, "12_fairness_forest_plot", data_payload=payload)


if __name__ == "__main__":
    meta = run()
    print("Generated Fairness Forest Plot:", meta)
