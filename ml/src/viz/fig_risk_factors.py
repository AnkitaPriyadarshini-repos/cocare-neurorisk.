"""Figure 18: Multifactor Risk Factor Analysis & Adjusted Odds Ratios.

Directly adapts and extends Albert-L-Phan's epidemiological regression approach,
providing a multifactor correlation heatmap and adjusted odds ratios (with 95% CIs)
for demographic and cognitive features.
"""
import os
import json
import matplotlib.pyplot as plt
import numpy as np
from .theme import apply_axes_style, add_figure_footer, save_figure_pair


def create_risk_factors_figure(theme: dict, mode: str) -> plt.Figure:
    with open("ml/reports/risk_factors.json", "r") as f:
        data = json.load(f)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.2), facecolor=theme["bg"])
    
    # --- SUBPLOT 1: Correlation Matrix Heatmap ---
    apply_axes_style(ax1, theme, grid=False)
    
    corr_dict = data["correlation_matrix"]
    features = ["Age", "EDUC", "SES", "MMSE", "target"]
    display_labels = ["Age", "Education", "SES Tier", "MMSE Score", "Dementia Risk"]
    
    matrix = np.zeros((len(features), len(features)))
    for i, f1 in enumerate(features):
        for j, f2 in enumerate(features):
            matrix[i, j] = corr_dict[f1][f2]
            
    cmap = "Blues_r" if mode == "light" else "mako"
    im = ax1.imshow(matrix, cmap="coolwarm", vmin=-1.0, vmax=1.0)
    
    ax1.set_xticks(range(len(features)))
    ax1.set_yticks(range(len(features)))
    ax1.set_xticklabels(display_labels, fontsize=10, rotation=25, ha="right", fontweight="bold")
    ax1.set_yticklabels(display_labels, fontsize=10, fontweight="bold")
    ax1.set_title("Multifactor Feature Correlation Heatmap\n(Pearson Correlation r)", fontsize=12, fontweight="bold", pad=12)
    
    # Annotate values
    for i in range(len(features)):
        for j in range(len(features)):
            val = matrix[i, j]
            text_color = "#FFFFFF" if abs(val) > 0.4 else theme["text"]
            ax1.text(j, i, f"{val:+.2f}", ha="center", va="center", fontsize=9.5, fontweight="bold", color=text_color)
            
    cbar = fig.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(colors=theme["text_secondary"])

    # --- SUBPLOT 2: Adjusted Odds Ratios Forest Plot ---
    apply_axes_style(ax2, theme)
    
    ors = data["odds_ratios"]
    labels = [item["feature"] for item in ors]
    estimates = [item["odds_ratio"] for item in ors]
    ci_lows = [item["ci_lower"] for item in ors]
    ci_highs = [item["ci_upper"] for item in ors]
    p_vals = [item["p_value"] for item in ors]
    
    y_pos = np.arange(len(labels))
    
    # Neutral reference line at OR = 1.0
    ax2.axvline(1.0, color=theme["baseline"], linestyle="--", lw=1.5, alpha=0.8, label="Neutral Line (OR = 1.0)")
    
    for i in range(len(labels)):
        or_val = estimates[i]
        low = ci_lows[i]
        high = ci_highs[i]
        color = theme["danger"] if or_val > 1.2 else (theme["success"] if or_val < 0.9 else theme["accent_primary"])
        
        # Horizontal error bar
        ax2.errorbar(or_val, y_pos[i], xerr=[[or_val - low], [high - or_val]], fmt="o", color=color,
                     ecolor=color, elinewidth=2.2, capsize=5, markersize=8)
        
        # Annotation text on right
        ax2.text(high + 0.05, y_pos[i], f"OR={or_val:.2f} [{low:.2f}-{high:.2f}], p {p_vals[i]}",
                 va="center", fontsize=9, fontweight="bold", color=theme["text"])
        
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(labels, fontsize=10.5, fontweight="bold")
    ax2.set_xlabel("Adjusted Odds Ratio (OR with 95% CI)", fontsize=11, labelpad=8)
    ax2.set_xlim(0.4, 3.2)
    ax2.set_title("Adjusted Odds Ratios for Dementia Risk\n(Multivariate Logistic Regression)", fontsize=12, fontweight="bold", pad=12)
    ax2.invert_yaxis()  # top-down
    ax2.legend(loc="lower right", framealpha=0.85, facecolor=theme["card_bg"], edgecolor=theme["border"], fontsize=9)

    add_figure_footer(
        fig, theme,
        dataset="OASIS-1 Longitudinal (N=373 visits, 150 subjects; Multivariate Regularized Model)",
        disclaimer="Standardized odds ratios with 95% CIs | Screening demonstration only, NOT clinical diagnosis"
    )
    plt.tight_layout(rect=[0.02, 0.05, 0.98, 0.96])
    return fig


def run(output_dir="docs/showcase/figures", data_dir="docs/showcase/data"):
    with open("ml/reports/risk_factors.json", "r") as f:
        data = json.load(f)
    return save_figure_pair(
        create_risk_factors_figure,
        "18_risk_factor_odds_ratios",
        data_payload=data,
        output_dir=output_dir,
        data_dir=data_dir
    )


generate = run


if __name__ == "__main__":
    run()
