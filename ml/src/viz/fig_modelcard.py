"""Figure 14: Model Card at a Glance Infographic.

Executive one-page infographic combining:
- Model Details & Intended Use
- Out-of-Scope Uses
- Quantitative Performance (Repeated CV and Held-Out Test with CIs)
- Training Cohort & Population Shift Limitations
- Responsible AI & Stateless Privacy Guarantees
- Mandatory Clinical Disclaimer
Output: docs/showcase/figures/14_model_card_glance-light.png, -dark.png
"""
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from ml.src.viz.theme import add_figure_footer, save_figure_pair


def generate_model_card_glance(theme, mode="light"):
    fig = plt.figure(figsize=(16, 9.5), facecolor=theme["bg"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(theme["bg"])
    ax.axis("off")

    # Header Title
    ax.text(
        0.05, 0.94,
        "CO CARE : Model Card at a Glance (v1.0.0)",
        fontsize=24, fontweight="bold", color=theme["text"],
        transform=ax.transAxes
    )
    ax.text(
        0.05, 0.90,
        "Standardized specification adhering to Mitchell et al. (2019) model reporting guidelines.",
        fontsize=12, color=theme["text_secondary"],
        transform=ax.transAxes
    )

    # 4 Quadrants Layout
    card_w = 0.435
    card_h = 0.355

    # Card 1: Intended Use & Clinical Scope (Top-Left)
    c1 = patches.FancyBboxPatch(
        (0.05, 0.51), card_w, card_h,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor=theme["card_bg"], edgecolor=theme["border"], lw=1.2, transform=ax.transAxes
    )
    ax.add_patch(c1)
    ax.text(0.07, 0.83, "1. INTENDED USE & SCOPE", fontsize=12, fontweight="bold", color=theme["accent_primary"], transform=ax.transAxes)
    ax.text(0.07, 0.77, "Target Setting:", fontsize=9.5, fontweight="bold", color=theme["text"], transform=ax.transAxes)
    ax.text(0.18, 0.77, "Community intake, primary care triage, and mobile screening.", fontsize=9.5, color=theme["text_secondary"], transform=ax.transAxes)
    ax.text(0.07, 0.72, "Two Variants:", fontsize=9.5, fontweight="bold", color=theme["text"], transform=ax.transAxes)
    ax.text(0.07, 0.67, "• model_without_mmse: Purely self-reportable (Age, Sex, EDUC, SES).\n• model_with_mmse: Augments demographics with MMSE/HMSE total score.", fontsize=9, color=theme["text_secondary"], transform=ax.transAxes)
    ax.text(0.07, 0.60, "Out-of-Scope (Strict Exclusions):", fontsize=9.5, fontweight="bold", color=theme["danger"], transform=ax.transAxes)
    ax.text(0.07, 0.54, "• NOT a diagnostic tool for clinical dementia, Alzheimer's, or MCI.\n• Must never automate prescription, institutionalization, or clinical denial.", fontsize=8.5, color=theme["text_secondary"], transform=ax.transAxes)

    # Card 2: Quantitative Verification (Top-Right)
    c2 = patches.FancyBboxPatch(
        (0.515, 0.51), card_w, card_h,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor=theme["card_bg"], edgecolor=theme["border"], lw=1.2, transform=ax.transAxes
    )
    ax.add_patch(c2)
    ax.text(0.535, 0.83, "2. QUANTITATIVE PERFORMANCE (HONEST REPORTING)", fontsize=12, fontweight="bold", color=theme["success"], transform=ax.transAxes)
    
    # Mini table inside card
    headers = ["Metric", "Primary 5x5 Group CV", "Held-Out Test (N=72) [95% CI]"]
    ax.text(0.535, 0.77, f"{headers[0]:<14} | {headers[1]:<22} | {headers[2]}", fontsize=8.5, fontweight="bold", color=theme["text"], transform=ax.transAxes)
    ax.plot([0.535, 0.93], [0.755, 0.755], color=theme["border"], lw=1.0, transform=ax.transAxes)
    
    rows = [
        ("ROC-AUC (With)", "0.892 ± 0.041", "0.929 [0.847, 0.986]"),
        ("ROC-AUC (Without)", "0.654 ± 0.062", "0.679 [0.538, 0.811]"),
        ("Sensitivity", "72.9% ± 9.1%", "90.5% [75.0%, 100.0%]"),
        ("Specificity", "85.9% ± 7.8%", "74.5% [62.3%, 86.5%]"),
        ("Brier Score", "0.134 ± 0.026", "0.102 [0.063, 0.149]")
    ]
    y_row = 0.72
    for r in rows:
        col = theme["accent_primary"] if "With" in r[0] else theme["text"]
        ax.text(0.535, y_row, f"{r[0]:<17} | {r[1]:<22} | {r[2]}", fontsize=8, color=col, transform=ax.transAxes)
        y_row -= 0.038

    # Card 3: Training Cohort & Population Shift (Bottom-Left)
    c3 = patches.FancyBboxPatch(
        (0.05, 0.11), card_w, card_h,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor=theme["card_bg"], edgecolor=theme["border"], lw=1.2, transform=ax.transAxes
    )
    ax.add_patch(c3)
    ax.text(0.07, 0.43, "3. COHORT & POPULATION SHIFT LIMITATIONS", fontsize=12, fontweight="bold", color=theme["accent_secondary"], transform=ax.transAxes)
    ax.text(0.07, 0.38, "Training Data Source:", fontsize=9.5, fontweight="bold", color=theme["text"], transform=ax.transAxes)
    ax.text(0.24, 0.38, "OASIS-1/2 Longitudinal (Washington Univ., St. Louis, USA).", fontsize=9, color=theme["text_secondary"], transform=ax.transAxes)
    ax.text(0.07, 0.33, "Population Shift Warnings:", fontsize=9.5, fontweight="bold", color=theme["danger"], transform=ax.transAxes)
    ax.text(0.07, 0.28, "• OASIS cohort skews towards high education (>12 yrs) and Western demographics.\n• NOT validated on LASI-DAD, Indian rural populations, or Odia speakers.\n• Cultural/linguistic bias: MMSE is heavily language/literacy dependent.", fontsize=8.5, color=theme["text_secondary"], transform=ax.transAxes)
    ax.text(0.07, 0.17, "Target Scale Target:", fontsize=9.5, fontweight="bold", color=theme["success"], transform=ax.transAxes)
    ax.text(0.07, 0.13, "LASI-DAD transition planned (N~3,000+ nationally representative Indian cohort).", fontsize=8.5, color=theme["text_secondary"], transform=ax.transAxes)

    # Card 4: Responsible AI & Stateless Privacy (Bottom-Right)
    c4 = patches.FancyBboxPatch(
        (0.515, 0.11), card_w, card_h,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor=theme["card_bg"], edgecolor=theme["border"], lw=1.2, transform=ax.transAxes
    )
    ax.add_patch(c4)
    ax.text(0.535, 0.43, "4. RESPONSIBLE AI & PRIVACY GUARANTEES", fontsize=12, fontweight="bold", color=theme["purple"], transform=ax.transAxes)
    ax.text(0.535, 0.38, "Stateless Privacy Architecture:", fontsize=9.5, fontweight="bold", color=theme["text"], transform=ax.transAxes)
    ax.text(0.535, 0.33, "• Patient profile vectors are NEVER written to database tables or logs.\n• Fully stateless execution; predictions discarded after HTTP response.", fontsize=8.5, color=theme["text_secondary"], transform=ax.transAxes)
    ax.text(0.535, 0.26, "Transparency & Parity:", fontsize=9.5, fontweight="bold", color=theme["text"], transform=ax.transAxes)
    ax.text(0.535, 0.21, "• Bilingual feature attribution (English + Odia [needs native review]).\n• Zero-dependency occlusion sensitivity matches SHAP with rs = 0.985.", fontsize=8.5, color=theme["text_secondary"], transform=ax.transAxes)
    ax.text(0.535, 0.14, "Model Status Header:", fontsize=9.5, fontweight="bold", color=theme["accent_primary"], transform=ax.transAxes)
    ax.text(0.70, 0.14, "demo_oasis_not_validated_for_lasi_dad", fontsize=8.5, fontweight="bold", color=theme["text"], transform=ax.transAxes)

    add_figure_footer(fig, theme)
    return fig


def run():
    payload = {
        "model_card_version": "1.0.0",
        "intended_use": "Preliminary cognitive risk screening demonstration",
        "out_of_scope": "Clinical diagnosis or treatment denial",
        "cohort": "OASIS Longitudinal (US)",
        "population_shift": "Not validated on Indian/Odia populations",
        "stateless_privacy": True
    }
    return save_figure_pair(generate_model_card_glance, "14_model_card_glance", data_payload=payload)


if __name__ == "__main__":
    meta = run()
    print("Generated Model Card Infographic:", meta)
