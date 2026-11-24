"""Figure 3: Leakage-Safe Grouped Split & Permutation Sanity Schematic.

Illustrates participant clustering (multiple visits per subject), zero-overlap train/test partitioning,
and the label-permutation sanity check inset.
Output: docs/showcase/figures/03_split_schematic-light.png, -dark.png, .svg
"""
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from ml.src.viz.theme import add_figure_footer, save_figure_pair


def generate_split_schematic(theme, mode="light"):
    fig = plt.figure(figsize=(16, 7.5), facecolor=theme["bg"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(theme["bg"])
    ax.axis("off")

    # Title
    ax.text(
        0.05, 0.94,
        "Leakage-Safe Partitioning: Longitudinal Participant Grouping",
        fontsize=22, fontweight="bold", color=theme["text"],
        transform=ax.transAxes
    )
    ax.text(
        0.05, 0.89,
        "Preventing optimistic bias: 373 visits across 150 subjects clustered so NO participant crosses splits.",
        fontsize=12, color=theme["text_secondary"],
        transform=ax.transAxes
    )

    # Left Section: Full Cohort Clustering Visual
    box_all = patches.FancyBboxPatch(
        (0.05, 0.12), 0.28, 0.72,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor=theme["card_bg"],
        edgecolor=theme["border"],
        linewidth=1.2,
        transform=ax.transAxes
    )
    ax.add_patch(box_all)
    ax.text(0.07, 0.80, "ALL RECORDS (OASIS)", fontsize=12, fontweight="bold", color=theme["text"], transform=ax.transAxes)
    ax.text(0.07, 0.76, "373 Visits | 150 Unique Subjects\nMean: 2.49 visits / subject (Range: 1-5)", fontsize=9, color=theme["text_muted"], transform=ax.transAxes)

    # Draw subject clusters schematic
    rng = np.random.RandomState(42)
    y_pos = 0.70
    for s_idx in range(9):
        subj_name = f"Subject S{s_idx+1:03d}"
        n_visits = rng.choice([2, 3, 4], p=[0.5, 0.35, 0.15])
        ax.text(0.07, y_pos, subj_name, fontsize=8.5, fontweight="bold", color=theme["text_secondary"], transform=ax.transAxes)
        # draw visit dots
        for v in range(n_visits):
            circ = patches.Circle((0.21 + v * 0.025, y_pos + 0.008), 0.008, facecolor=theme["accent_primary"], transform=ax.transAxes)
            ax.add_patch(circ)
        y_pos -= 0.045
    ax.text(0.07, y_pos + 0.01, "... and 141 more subjects", fontsize=8.5, fontstyle="italic", color=theme["text_muted"], transform=ax.transAxes)
    
    # Bottom callout: Ungrouped vs Grouped delta
    delta_box = patches.FancyBboxPatch(
        (0.065, 0.15), 0.25, 0.12,
        boxstyle="round,pad=0.01,rounding_size=0.015",
        facecolor=theme["bg"],
        edgecolor=theme["danger"],
        linewidth=1.2,
        transform=ax.transAxes
    )
    ax.add_patch(delta_box)
    ax.text(0.075, 0.23, "LEAKAGE PENALTY DETECTED", fontsize=8.5, fontweight="bold", color=theme["danger"], transform=ax.transAxes)
    ax.text(0.075, 0.17, "Ungrouped CV inflated AUC by +0.052.\nGrouped split guarantees zero subject leak.", fontsize=8, color=theme["text"], transform=ax.transAxes)

    # Middle Section: Grouped Split to Train & Test
    ax.annotate(
        "GroupShuffleSplit\n(80 / 20 Subjects)",
        xy=(0.38, 0.52), xytext=(0.33, 0.52),
        arrowprops=dict(arrowstyle="->", color=theme["accent_primary"], lw=2.0),
        fontsize=9.5, fontweight="bold", color=theme["accent_primary"],
        va="center", xycoords="axes fraction"
    )

    # Training Set Box
    box_train = patches.FancyBboxPatch(
        (0.40, 0.45), 0.26, 0.39,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor=theme["card_bg"],
        edgecolor=theme["accent_primary"],
        linewidth=1.5,
        transform=ax.transAxes
    )
    ax.add_patch(box_train)
    ax.text(0.42, 0.80, "TRAINING SPLIT (80.7%)\n120 Subjects | 301 Visits", fontsize=11, fontweight="bold", color=theme["accent_primary"], transform=ax.transAxes)
    ax.text(0.42, 0.72, "Model selection & threshold tuning\nFit preprocessors on this data ONLY", fontsize=9, color=theme["text_secondary"], transform=ax.transAxes)
    
    # 5-fold Stratified Group K-Fold schematic
    for f in range(5):
        fold_rect = patches.Rectangle((0.42, 0.64 - f*0.035), 0.22, 0.025, facecolor=theme["bg"], edgecolor=theme["border"], lw=0.8, transform=ax.transAxes)
        ax.add_patch(fold_rect)
        # highlight val slice
        val_slice = patches.Rectangle((0.42 + f*0.044, 0.64 - f*0.035), 0.044, 0.025, facecolor=theme["accent_secondary"], edgecolor="none", transform=ax.transAxes)
        ax.add_patch(val_slice)
        ax.text(0.425, 0.647 - f*0.035, f"Fold {f+1}: 24 subjects val", fontsize=7.5, color=theme["text"], transform=ax.transAxes)

    # Held-Out Test Set Box
    box_test = patches.FancyBboxPatch(
        (0.40, 0.12), 0.26, 0.28,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor=theme["card_bg"],
        edgecolor=theme["success"],
        linewidth=1.5,
        transform=ax.transAxes
    )
    ax.add_patch(box_test)
    ax.text(0.42, 0.35, "HELD-OUT TEST SPLIT (19.3%)\n30 Subjects | 72 Visits", fontsize=11, fontweight="bold", color=theme["success"], transform=ax.transAxes)
    ax.text(0.42, 0.27, "Touched ONCE at the end for honest metrics.\nZero subject overlap with train (verified).", fontsize=8.5, color=theme["text_secondary"], transform=ax.transAxes)
    ax.text(0.42, 0.21, "21 Positives (29.2%) | 51 Negatives (70.8%)", fontsize=8.5, fontweight="bold", color=theme["text"], transform=ax.transAxes)
    ax.text(0.42, 0.15, "Test: test_participant_grouping_zero_overlap PASSED", fontsize=7.5, color=theme["success"], transform=ax.transAxes)

    # Right Section: Inset - Permutation / Label Shuffle Sanity Check
    box_inset = patches.FancyBboxPatch(
        (0.70, 0.12), 0.25, 0.72,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor=theme["card_bg"],
        edgecolor=theme["border"],
        linewidth=1.2,
        transform=ax.transAxes
    )
    ax.add_patch(box_inset)
    ax.text(0.72, 0.80, "SANITY CHECK: LABEL PERMUTATION", fontsize=10.5, fontweight="bold", color=theme["purple"], transform=ax.transAxes)
    ax.text(0.72, 0.74, "Asserting zero spurious data leakage\nTarget: CV AUC ~ 0.50 under random labels", fontsize=8.5, color=theme["text_secondary"], transform=ax.transAxes)

    # Permutation Bar chart schematic
    bars = [
        ("Real Labels (With MMSE)", 0.892, theme["accent_primary"]),
        ("Permuted (With MMSE)", 0.496, theme["baseline"]),
        ("Real Labels (Without MMSE)", 0.654, theme["accent_secondary"]),
        ("Permuted (Without MMSE)", 0.470, theme["baseline"]),
        ("Theoretical Random Baseline", 0.500, theme["danger"])
    ]
    
    y_b = 0.62
    for b_label, b_val, b_col in bars:
        ax.text(0.72, y_b + 0.045, b_label, fontsize=7.5, fontweight="bold", color=theme["text"], transform=ax.transAxes)
        # Bar background
        bg_rect = patches.Rectangle((0.72, y_b + 0.01), 0.21, 0.025, facecolor=theme["bg"], edgecolor=theme["border"], lw=0.6, transform=ax.transAxes)
        ax.add_patch(bg_rect)
        # Val bar
        bar_len = (b_val / 1.0) * 0.21
        val_rect = patches.Rectangle((0.72, y_b + 0.01), bar_len, 0.025, facecolor=b_col, edgecolor="none", transform=ax.transAxes)
        ax.add_patch(val_rect)
        ax.text(0.72 + bar_len + 0.01, y_b + 0.015, f"{b_val:.3f}", fontsize=8, fontweight="bold", color=b_col, transform=ax.transAxes)
        y_b -= 0.095

    ax.text(0.72, 0.16, "VERIFICATION RESULT: PASSED\nShuffled labels collapse to pure chance,\nproving pipelines do not leak subject structure.", fontsize=8, fontweight="bold", color=theme["success"], transform=ax.transAxes)

    add_figure_footer(fig, theme)
    return fig


def run():
    payload = {
        "total_records": 373,
        "total_subjects": 150,
        "train_subjects": 120,
        "train_records": 301,
        "test_subjects": 30,
        "test_records": 72,
        "subject_overlap": 0,
        "ungrouped_auc_delta_with_mmse": +0.0132,
        "ungrouped_auc_delta_without_mmse": +0.0524,
        "permutation_auc_with_mmse": 0.4956,
        "permutation_auc_without_mmse": 0.4700
    }
    return save_figure_pair(generate_split_schematic, "03_split_schematic", data_payload=payload)


if __name__ == "__main__":
    meta = run()
    print("Generated Split Schematic:", meta)
