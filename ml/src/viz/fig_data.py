"""Figure 4: Data Distribution & Missingness Overview.

Small multiples visualizing cohort balance across Target, Age bands, Sex, Education,
and tabular missingness matrix summary.
Output: docs/showcase/figures/04_data_overview-light.png, -dark.png
"""
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from ml.src.viz.theme import add_figure_footer, apply_axes_style, save_figure_pair


def generate_data_overview(theme, mode="light"):
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), facecolor=theme["bg"])
    fig.subplots_adjust(top=0.88, bottom=0.10, hspace=0.35, wspace=0.28)
    
    # Global Title
    fig.suptitle(
        "CO CARE : OASIS Cohort Demographic Profile & Data Quality",
        fontsize=18, fontweight="bold", color=theme["text"], y=0.96
    )
    fig.text(
        0.5, 0.92,
        "Class balance across demographic strata (N=373 records, 150 participants) and missingness profile.",
        fontsize=11, color=theme["text_secondary"], ha="center"
    )

    # 1. Target Class Distribution (Top-Left)
    ax1 = axes[0, 0]
    apply_axes_style(ax1, theme)
    categories = ["Non-Demented\n(CDR = 0)", "Impaired / Dementia\n(CDR > 0)"]
    counts = [206, 167]
    pcts = [c / sum(counts) * 100 for c in counts]
    colors = [theme["baseline"], theme["accent_primary"]]
    bars = ax1.bar(categories, counts, color=colors, width=0.55, edgecolor=theme["border"], zorder=3)
    ax1.set_ylabel("Participant Visits (Count)", fontsize=10, fontweight="bold")
    ax1.set_title("Overall Class Distribution (Prevalence: 44.8%)", fontsize=11, fontweight="bold", pad=10)
    ax1.set_ylim(0, 250)
    for bar, c, p in zip(bars, counts, pcts):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 6, f"N={c} ({p:.1f}%)", ha="center", fontsize=9.5, fontweight="bold", color=theme["text"])

    # 2. Target Prevalence by Sex (Top-Right)
    ax2 = axes[0, 1]
    apply_axes_style(ax2, theme)
    sex_groups = ["Female (N=213)", "Male (N=160)"]
    neg_counts = [142, 64]
    pos_counts = [71, 96]
    w = 0.45
    ax2.bar(sex_groups, neg_counts, label="Non-Demented", color=theme["baseline"], width=w, edgecolor=theme["border"], zorder=3)
    ax2.bar(sex_groups, pos_counts, bottom=neg_counts, label="Impaired (CDR>0)", color=theme["accent_primary"], width=w, edgecolor=theme["border"], zorder=3)
    ax2.set_ylabel("Visits (Count)", fontsize=10, fontweight="bold")
    ax2.set_title("Class Stratification by Sex (F: 33.3% vs M: 60.0% Impaired)", fontsize=11, fontweight="bold", pad=10)
    ax2.set_ylim(0, 250)
    ax2.legend(loc="upper right", frameon=True, facecolor=theme["card_bg"], edgecolor=theme["border"], fontsize=8.5)
    # text labels
    ax2.text(0, 213 + 6, "33.3% Impaired", ha="center", fontsize=9, fontweight="bold", color=theme["text"])
    ax2.text(1, 160 + 6, "60.0% Impaired", ha="center", fontsize=9, fontweight="bold", color=theme["text"])

    # 3. Prevalence by Age Band (Bottom-Left)
    ax3 = axes[1, 0]
    apply_axes_style(ax3, theme)
    age_bands = ["< 70 years", "70 - 79 years", "80+ years"]
    age_totals = [66, 186, 121]
    age_pos = [17, 86, 64]
    age_prev = [p / t * 100 for p, t in zip(age_pos, age_totals)]
    bars3 = ax3.bar(age_bands, age_prev, color=theme["accent_secondary"], width=0.55, edgecolor=theme["border"], zorder=3)
    ax3.set_ylabel("Impairment Prevalence (%)", fontsize=10, fontweight="bold")
    ax3.set_title("Prevalence Across Age Bands (Age Gradient)", fontsize=11, fontweight="bold", pad=10)
    ax3.set_ylim(0, 75)
    for bar, p, t, pos in zip(bars3, age_prev, age_totals, age_pos):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, f"{p:.1f}%\n({pos}/{t})", ha="center", fontsize=8.5, fontweight="bold", color=theme["text"])

    # 4. Missingness Profile (Bottom-Right)
    ax4 = axes[1, 1]
    apply_axes_style(ax4, theme)
    features = ["Subject ID", "Age", "Sex", "EDUC", "SES", "MMSE"]
    missing_pcts = [0.0, 0.0, 0.0, 0.0, 5.09, 0.54]
    missing_counts = [0, 0, 0, 0, 19, 2]
    colors4 = [theme["success"] if p == 0 else theme["danger"] for p in missing_pcts]
    bars4 = ax4.barh(features, missing_pcts, color=colors4, height=0.55, edgecolor=theme["border"], zorder=3)
    ax4.set_xlabel("Missingness Rate (%)", fontsize=10, fontweight="bold")
    ax4.set_title("Missing Data Profile (Median Imputed inside Pipeline)", fontsize=11, fontweight="bold", pad=10)
    ax4.set_xlim(0, 12)
    for bar, p, c in zip(bars4, missing_pcts, missing_counts):
        text_label = "0.0% (Clean)" if p == 0 else f"{p:.2f}% (N={c})"
        ax4.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2, text_label, va="center", fontsize=8.5, fontweight="bold", color=theme["text"])

    add_figure_footer(fig, theme)
    return fig


def run():
    payload = {
        "total_records": 373,
        "prevalence": 0.4477,
        "counts": {"non_demented": 206, "impaired": 167},
        "sex_prevalence": {"Female": 0.3333, "Male": 0.6000},
        "age_prevalence": {"<70": 0.2576, "70-79": 0.4624, "80+": 0.5289},
        "missingness": {"SES_pct": 5.09, "SES_count": 19, "MMSE_pct": 0.54, "MMSE_count": 2, "others_pct": 0.0}
    }
    return save_figure_pair(generate_data_overview, "04_data_overview", data_payload=payload)


if __name__ == "__main__":
    meta = run()
    print("Generated Data Overview:", meta)
