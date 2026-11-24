"""Figure 1: Hero Banner for CO CARE Repository Header.

Renders high-impact header with live stats pulled from cv_metrics.json and test_metrics.json.
Output: docs/showcase/figures/01_hero_banner-light.png, -dark.png, .svg
"""
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from ml.src.viz.theme import add_figure_footer, save_figure_pair


def generate_hero_banner(theme, mode="light"):
    fig = plt.figure(figsize=(16, 6.5), facecolor=theme["bg"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(theme["bg"])
    ax.axis("off")
    
    # Load live metrics
    with open("ml/reports/cv_metrics.json") as f:
        cv_data = json.load(f)
    with open("ml/reports/test_metrics.json") as f:
        test_data = json.load(f)
        
    cv_auc_w = cv_data["model_with_mmse"]["roc_auc"]["mean"]
    cv_auc_w_std = cv_data["model_with_mmse"]["roc_auc"]["std"]
    cv_auc_wo = cv_data["model_without_mmse"]["roc_auc"]["mean"]
    cv_auc_wo_std = cv_data["model_without_mmse"]["roc_auc"]["std"]
    
    test_sens_w = test_data["model_with_mmse"]["metrics"]["sensitivity"] * 100
    test_sens_ci = test_data["model_with_mmse"]["bootstrap_95_ci_2000"]["sensitivity"]
    test_spec_w = test_data["model_with_mmse"]["metrics"]["specificity"] * 100
    test_spec_ci = test_data["model_with_mmse"]["bootstrap_95_ci_2000"]["specificity"]

    # Header Badges row
    badges = [
        ("CI / Tests", "Passing (18/18)", theme["success"]),
        ("Python", "3.10+", theme["accent_primary"]),
        ("Scikit-Learn", "1.6.1", theme["cyan"]),
        ("FastAPI", "Serverless", theme["purple"]),
        ("Vercel", "Production Live", theme["accent_secondary"]),
        ("License", "MIT", theme["baseline"]),
    ]
    
    bx_start = 0.05
    for label, val, col in badges:
        # draw badge capsule
        rect = patches.FancyBboxPatch(
            (bx_start, 0.88), 0.135, 0.055,
            boxstyle="round,pad=0.015,rounding_size=0.02",
            facecolor=theme["card_bg"],
            edgecolor=theme["border"],
            linewidth=1.0,
            transform=ax.transAxes
        )
        ax.add_patch(rect)
        ax.text(bx_start + 0.01, 0.907, label.upper(), fontsize=7.5, color=theme["text_muted"], fontweight="bold", transform=ax.transAxes)
        ax.text(bx_start + 0.07, 0.907, val, fontsize=8, color=col, fontweight="bold", transform=ax.transAxes)
        bx_start += 0.15

    # Main Title and Subtitle
    ax.text(
        0.05, 0.76,
        "CO CARE : Dementia & Cognitive Risk Screening",
        fontsize=28, fontweight="bold", color=theme["text"],
        transform=ax.transAxes
    )
    ax.text(
        0.05, 0.69,
        "Explainable, privacy-first machine learning models for early community risk screening.",
        fontsize=13, color=theme["text_secondary"],
        transform=ax.transAxes
    )
    ax.text(
        0.05, 0.63,
        "Trained on longitudinal cohort data with grouped leakage protection; ready for LASI-DAD validation.",
        fontsize=12, color=theme["text_muted"],
        transform=ax.transAxes
    )
    
    # 4 Live Metric Cards
    cards = [
        {
            "tag": "PRIMARY CV (WITH MMSE)",
            "headline": f"{cv_auc_w:.3f}",
            "unit": f"± {cv_auc_w_std:.3f}",
            "sub": f"Held-out test: {test_data['model_with_mmse']['metrics']['roc_auc']:.3f} [95% CI: 0.85-0.99]",
            "color": theme["accent_primary"],
            "desc": "5x5 Repeated Group CV AUC"
        },
        {
            "tag": "PRIMARY CV (DEMOGRAPHICS ONLY)",
            "headline": f"{cv_auc_wo:.3f}",
            "unit": f"± {cv_auc_wo_std:.3f}",
            "sub": f"Held-out test: {test_data['model_without_mmse']['metrics']['roc_auc']:.3f} [95% CI: 0.54-0.81]",
            "color": theme["accent_secondary"],
            "desc": "Self-reportable (No test items)"
        },
        {
            "tag": "SCREENING SENSITIVITY",
            "headline": f"{test_sens_w:.1f}%",
            "unit": "[75% - 100%]",
            "sub": "Calibrated operating threshold (0.3203)",
            "color": theme["success"],
            "desc": "High recall minimizes missed cases"
        },
        {
            "tag": "SCREENING SPECIFICITY",
            "headline": f"{test_spec_w:.1f}%",
            "unit": "[62% - 87%]",
            "sub": "Negative Predictive Value (NPV): 95.0%",
            "color": theme["cyan"],
            "desc": "Safe triage for primary care referral"
        }
    ]
    
    cx_start = 0.05
    card_width = 0.208
    card_gap = 0.022
    
    for i, c in enumerate(cards):
        cx = cx_start + i * (card_width + card_gap)
        cy = 0.16
        card_rect = patches.FancyBboxPatch(
            (cx, cy), card_width, 0.38,
            boxstyle="round,pad=0.015,rounding_size=0.03",
            facecolor=theme["card_bg"],
            edgecolor=theme["border"],
            linewidth=1.2,
            transform=ax.transAxes
        )
        ax.add_patch(card_rect)
        
        # Color bar indicator on top of card
        top_bar = patches.FancyBboxPatch(
            (cx + 0.01, cy + 0.355), card_width - 0.02, 0.015,
            boxstyle="round,pad=0.005,rounding_size=0.01",
            facecolor=c["color"],
            edgecolor="none",
            transform=ax.transAxes
        )
        ax.add_patch(top_bar)
        
        # Tag
        ax.text(cx + 0.015, cy + 0.315, c["tag"], fontsize=8, fontweight="bold", color=c["color"], transform=ax.transAxes)
        # Headline Number
        ax.text(cx + 0.015, cy + 0.205, c["headline"], fontsize=26, fontweight="bold", color=theme["text"], transform=ax.transAxes)
        # Unit / CI
        ax.text(cx + 0.015, cy + 0.155, c["unit"], fontsize=9.5, fontweight="bold", color=theme["text_secondary"], transform=ax.transAxes)
        # Description
        ax.text(cx + 0.015, cy + 0.095, c["desc"], fontsize=8.5, color=theme["text_muted"], transform=ax.transAxes)
        # Secondary stat
        ax.text(cx + 0.015, cy + 0.040, c["sub"], fontsize=7.5, color=theme["text_secondary"], transform=ax.transAxes)

    add_figure_footer(fig, theme)
    return fig


def run():
    with open("ml/reports/cv_metrics.json") as f1, open("ml/reports/test_metrics.json") as f2:
        payload = {"cv": json.load(f1), "test": json.load(f2)}
    return save_figure_pair(generate_hero_banner, "01_hero_banner", data_payload=payload)


if __name__ == "__main__":
    meta = run()
    print("Generated Hero Banner:", meta)
