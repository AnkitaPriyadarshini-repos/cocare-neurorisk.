"""Figure 9: Confusion Matrices with Bootstrap CIs.

Side-by-side confusion matrices for Model With MMSE and Model Without MMSE
on held-out test cohort (N=72), showing counts, row-normalized rates, and 95% bootstrap CIs.
Output: docs/showcase/figures/09_confusion_matrices-light.png, -dark.png
"""
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from ml.src.viz.theme import add_figure_footer, apply_axes_style, save_figure_pair


def generate_confusion_matrices(theme, mode="light"):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.8), facecolor=theme["bg"])
    fig.subplots_adjust(top=0.86, bottom=0.12, wspace=0.32)

    fig.suptitle(
        "CO CARE : Held-Out Test Confusion Matrices (N=72 Visits, 30 Participants)",
        fontsize=18, fontweight="bold", color=theme["text"], y=0.96
    )
    fig.text(
        0.5, 0.91,
        "Cell counts and row-normalized rates with 2,000-resample bootstrap 95% confidence intervals.",
        fontsize=11, color=theme["text_secondary"], ha="center"
    )

    # Matrix data from ml/reports/test_metrics.json
    # Model with MMSE: TP=19, FN=2, TN=38, FP=13 (threshold=0.3203)
    # Model without MMSE: TP=19, FN=2, TN=18, FP=33 (threshold=0.3301)
    
    matrices = [
        {
            "ax": ax1,
            "title": "Model With MMSE (Cognitive-Augmented)\nThreshold = 0.3203 | Accuracy: 79.2% [69.4%, 88.9%]",
            "tp": 19, "fn": 2, "tn": 38, "fp": 13,
            "sens": 90.5, "sens_ci": "75.0% - 100.0%",
            "spec": 74.5, "spec_ci": "62.3% - 86.5%",
            "prec": 59.4, "npv": 95.0,
            "theme_accent": theme["accent_primary"]
        },
        {
            "ax": ax2,
            "title": "Model Without MMSE (Demographics Only)\nThreshold = 0.3301 | Accuracy: 51.4% [38.9%, 62.5%]",
            "tp": 19, "fn": 2, "tn": 18, "fp": 33,
            "sens": 90.5, "sens_ci": "75.0% - 100.0%",
            "spec": 35.3, "spec_ci": "22.7% - 47.9%",
            "prec": 36.5, "npv": 90.0,
            "theme_accent": theme["accent_secondary"]
        }
    ]

    for m in matrices:
        ax = m["ax"]
        ax.set_facecolor(theme["bg"])
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 2)
        ax.axis("off")
        
        ax.set_title(m["title"], fontsize=11, fontweight="bold", color=theme["text"], pad=12)
        
        # Grid blocks
        # [0, 1] is TN, [1, 1] is FP
        # [0, 0] is FN, [1, 0] is TP
        cells = [
            # TN (Col 0, Row 1)
            {"x": 0.05, "y": 1.05, "w": 0.88, "h": 0.88, "cnt": m["tn"], "tot": m["tn"]+m["fp"],
             "pct": m["spec"], "ci": m["spec_ci"], "label": "True Negative (TN)", "color": theme["card_bg"],
             "text_color": theme["text"], "border": theme["border"]},
            # FP (Col 1, Row 1)
            {"x": 1.05, "y": 1.05, "w": 0.88, "h": 0.88, "cnt": m["fp"], "tot": m["tn"]+m["fp"],
             "pct": 100 - m["spec"], "ci": f"{100-74.5:.1f}%", "label": "False Positive (FP)", "color": theme["card_bg"],
             "text_color": theme["danger"], "border": theme["danger"]},
            # FN (Col 0, Row 0)
            {"x": 0.05, "y": 0.05, "w": 0.88, "h": 0.88, "cnt": m["fn"], "tot": m["tp"]+m["fn"],
             "pct": 100 - m["sens"], "ci": f"{100-90.5:.1f}%", "label": "False Negative (FN)", "color": theme["card_bg"],
             "text_color": theme["danger"], "border": theme["danger"]},
            # TP (Col 1, Row 0)
            {"x": 1.05, "y": 0.05, "w": 0.88, "h": 0.88, "cnt": m["tp"], "tot": m["tp"]+m["fn"],
             "pct": m["sens"], "ci": m["sens_ci"], "label": "True Positive (TP)", "color": theme["card_bg"],
             "text_color": theme["success"], "border": theme["success"]}
        ]
        
        for c in cells:
            rect = patches.FancyBboxPatch(
                (c["x"], c["y"]), c["w"], c["h"],
                boxstyle="round,pad=0.015,rounding_size=0.03",
                facecolor=c["color"],
                edgecolor=c["border"],
                linewidth=1.5 if c["border"] != theme["border"] else 1.0
            )
            ax.add_patch(rect)
            
            # Label
            ax.text(c["x"] + c["w"]/2, c["y"] + c["h"] - 0.18, c["label"],
                    ha="center", fontsize=9.5, fontweight="bold", color=c["text_color"])
            # Count
            ax.text(c["x"] + c["w"]/2, c["y"] + c["h"]/2 - 0.02, f"N = {c['cnt']}",
                    ha="center", fontsize=22, fontweight="bold", color=theme["text"])
            # Normalized rate & CI
            rate_text = f"{c['pct']:.1f}% of actual\n[95% CI: {c['ci']}]" if "ci" in c else f"{c['pct']:.1f}%"
            ax.text(c["x"] + c["w"]/2, c["y"] + 0.18, rate_text,
                    ha="center", fontsize=8.5, color=theme["text_secondary"])

        # Row & Column annotations
        ax.text(-0.02, 1.48, "Actual Non-Demented\n(N=51)", ha="right", va="center", fontsize=9, fontweight="bold", color=theme["text"])
        ax.text(-0.02, 0.48, "Actual Impaired / CDR>0\n(N=21)", ha="right", va="center", fontsize=9, fontweight="bold", color=theme["text"])
        ax.text(0.48, 2.05, "Predicted Negative", ha="center", fontsize=9.5, fontweight="bold", color=theme["text"])
        ax.text(1.48, 2.05, "Predicted Impaired", ha="center", fontsize=9.5, fontweight="bold", color=theme["text"])
        
        # Summary footer pill
        ax.text(1.0, -0.15, f"Sensitivity: {m['sens']:.1f}%  |  Specificity: {m['spec']:.1f}%  |  NPV: {m['npv']:.1f}%",
                ha="center", fontsize=9, fontweight="bold", color=m["theme_accent"])

    add_figure_footer(fig, theme)
    return fig


def run():
    payload = {
        "model_with_mmse": {"tn": 38, "fp": 13, "fn": 2, "tp": 19, "sens": 0.9048, "spec": 0.7451, "threshold": 0.3203},
        "model_without_mmse": {"tn": 18, "fp": 33, "fn": 2, "tp": 19, "sens": 0.9048, "spec": 0.3529, "threshold": 0.3301}
    }
    return save_figure_pair(generate_confusion_matrices, "09_confusion_matrices", data_payload=payload)


if __name__ == "__main__":
    meta = run()
    print("Generated Confusion Matrices:", meta)
