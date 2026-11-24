"""
Generate high-fidelity UI showcase diagrams for CO CARE's Risk Check and My Progress screens.
Saves PNG and SVG visuals under docs/showcase/ui/.
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

def setup_dirs():
    os.makedirs("docs/showcase/ui", exist_ok=True)

def generate_wizard_mockup():
    fig, ax = plt.subplots(figsize=(8, 10), dpi=150)
    fig.patch.set_facecolor('#fdf8f0') # CO CARE background
    ax.set_facecolor('#fdf8f0')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Header / Top bar
    ax.text(8, 94, "← ପଛକୁ (Back)", fontsize=12, fontweight='bold', color='#5a5650')
    # Font size buttons
    box_font = patches.FancyBboxPatch((65, 92), 27, 4.5, boxstyle="round,pad=0.5", fc='#ece6dc', ec='#d8cfc2')
    ax.add_patch(box_font)
    ax.text(70, 93.5, "A", fontsize=11, fontweight='bold', color='#1d1d1b')
    ax.text(78, 93.5, "A+", fontsize=13, fontweight='bold', color='#b4471b')
    ax.text(86, 93.5, "A++", fontsize=15, fontweight='bold', color='#1d1d1b')

    # Wizard title and step indicator
    ax.text(8, 86, "🩺 ସ୍ୱାସ୍ଥ୍ୟ ଯାଞ୍ଚ (Risk Check)", fontsize=18, fontweight='bold', color='#1d1d1b')
    ax.text(92, 86, "ପଦକ୍ଷେପ ୧ / ୫ (Step 1 of 5)", fontsize=11, fontweight='bold', color='#5a5650', ha='right')

    # Progress bar
    bg_bar = patches.FancyBboxPatch((8, 81.5), 84, 2.0, boxstyle="round,pad=0.2", fc='#e6ded3', ec='none')
    ax.add_patch(bg_bar)
    fill_bar = patches.FancyBboxPatch((8, 81.5), 84 * 0.2, 2.0, boxstyle="round,pad=0.2", fc='#b4471b', ec='none')
    ax.add_patch(fill_bar)

    # Main Card
    card = patches.FancyBboxPatch((8, 25), 84, 52, boxstyle="round,pad=1.5", fc='#ffffff', ec='#d8cfc2', lw=2)
    ax.add_patch(card)

    # Question Title & Audio button
    ax.text(12, 70, "ବୟସ (ବର୍ଷ) · Age (years)", fontsize=16, fontweight='bold', color='#1d1d1b')
    audio_btn = patches.FancyBboxPatch((70, 68), 18, 4.5, boxstyle="round,pad=0.5", fc='#fdf8f0', ec='#d8cfc2')
    ax.add_patch(audio_btn)
    ax.text(79, 69.5, "🔊 ଶୁଣନ୍ତୁ (Listen)", fontsize=10, fontweight='bold', color='#1d1d1b', ha='center')

    # Help text
    ax.text(12, 63, "ଅଂଶଗ୍ରହଣକାରୀଙ୍କ ସମ୍ପୂର୍ଣ୍ଣ ବୟସ (୪୦-୧୨୦) [needs native review]", fontsize=11, color='#5a5650')
    ax.text(12, 59.5, "Participant age in complete years (40-120).", fontsize=10.5, color='#777777', style='italic')

    # Stepper widget
    # Minus button
    minus_btn = patches.FancyBboxPatch((18, 41), 14, 12, boxstyle="round,pad=0.6", fc='#ffffff', ec='#d8cfc2', lw=2)
    ax.add_patch(minus_btn)
    ax.text(25, 45, "−", fontsize=24, fontweight='bold', color='#1d1d1b', ha='center')

    # Display box
    val_box = patches.FancyBboxPatch((36, 41), 28, 12, boxstyle="round,pad=0.6", fc='#fdf8f0', ec='#b4471b', lw=2.5)
    ax.add_patch(val_box)
    ax.text(50, 45.5, "65", fontsize=28, fontweight='bold', color='#1d1d1b', ha='center')
    ax.text(50, 36.5, "ବର୍ଷ (years)", fontsize=10, color='#777777', ha='center')

    # Plus button
    plus_btn = patches.FancyBboxPatch((68, 41), 14, 12, boxstyle="round,pad=0.6", fc='#ffffff', ec='#d8cfc2', lw=2)
    ax.add_patch(plus_btn)
    ax.text(75, 45, "+", fontsize=24, fontweight='bold', color='#1d1d1b', ha='center')

    # Primary Next button
    next_btn = patches.FancyBboxPatch((8, 10), 84, 10, boxstyle="round,pad=0.8", fc='#b4471b', ec='#b4471b')
    ax.add_patch(next_btn)
    ax.text(50, 14, "ଆଗକୁ (Next) →", fontsize=16, fontweight='bold', color='#ffffff', ha='center')

    plt.tight_layout()
    out_png = "docs/showcase/ui/01_risk_wizard_screen.png"
    plt.savefig(out_png, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Generated {out_png}")

def generate_result_mockup():
    fig, ax = plt.subplots(figsize=(8, 11), dpi=150)
    fig.patch.set_facecolor('#fdf8f0')
    ax.set_facecolor('#fdf8f0')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Header
    ax.text(8, 94, "🩺 ଆପଣଙ୍କ ସ୍କ୍ରିନିଂ ସାରାଂଶ (Screening Summary)", fontsize=17, fontweight='bold', color='#1d1d1b')

    # Main Result Card
    card = patches.FancyBboxPatch((8, 38), 84, 52, boxstyle="round,pad=1.5", fc='#ffffff', ec='#d8cfc2', lw=2.5)
    ax.add_patch(card)

    # Score and Badge
    ax.text(12, 83, "ମଡେଲ ସ୍କୋର (Model Score)", fontsize=11, color='#5a5650')
    ax.text(12, 75, "0.2854", fontsize=32, fontweight='800', color='#1d1d1b')

    # Badge (Lower Risk)
    badge = patches.FancyBboxPatch((56, 74), 32, 9, boxstyle="round,pad=0.6", fc='#e8f5e9', ec='#a5d6a7', lw=2)
    ax.add_patch(badge)
    ax.text(72, 77.5, "🛡️ ନିମ୍ନ ସତର୍କତା (Lower Risk)", fontsize=11, fontweight='bold', color='#1b5e20', ha='center')

    # Score Note
    note_box = patches.FancyBboxPatch((12, 65), 76, 5.5, boxstyle="round,pad=0.4", fc='#f9f6f0', ec='#e0d7cb')
    ax.add_patch(note_box)
    ax.text(14, 67, "ℹ️ Model score calibrated to OASIS sample prevalence of 48.5%", fontsize=9.5, color='#5a5650')

    # What to do next
    ax.text(12, 59, "🧭 ପରବର୍ତ୍ତୀ ପଦକ୍ଷେପ (What to do next)", fontsize=13, fontweight='bold', color='#1d1d1b')
    ax.text(12, 53.5, "ନିୟମିତ ମନୋରଞ୍ଜକ ଖେଳ ଖେଳନ୍ତୁ, ସାଙ୍ଗସାଥୀଙ୍କ ସହ ସମୟ ବିତାନ୍ତୁ।", fontsize=10.5, color='#1d1d1b')
    ax.text(12, 49.5, "Keep engaging in regular social activities, walking, and brain games.", fontsize=10, color='#5a5650', style='italic')

    # Factors list
    ax.text(12, 43, "🔍 ସ୍କୋର ଉପରେ କାରକଗୁଡ଼ିକର ପ୍ରଭାବ (Factors with |impact| ≥ 0.01):", fontsize=10.5, fontweight='bold', color='#5a5650')
    ax.text(14, 39, "• 📉 EDUC (14 yrs): Lowered score by 0.032 relative to median training-data values", fontsize=9.5, color='#1d1d1b')

    # Clinical Disclaimer
    disc_box = patches.FancyBboxPatch((8, 25), 84, 10, boxstyle="round,pad=0.8", fc='#fff3e0', ec='#ffe082', lw=1.5)
    ax.add_patch(disc_box)
    ax.text(11, 31, "⚠️ ଏହା କୌଣସି ଡାକ୍ତରୀ ରୋଗ ନିର୍ଣ୍ଣୟ ନୁହେଁ। (Not a clinical diagnosis)", fontsize=11, fontweight='bold', color='#b4471b')
    ax.text(11, 27, "OASIS research demo · Not validated on Indian populations (LASI-DAD). Consult a physician.", fontsize=9, color='#795548')

    # Action buttons: Doctor summary & My progress
    doc_btn = patches.FancyBboxPatch((8, 14), 84, 8, boxstyle="round,pad=0.6", fc='#ffffff', ec='#b4471b', lw=2)
    ax.add_patch(doc_btn)
    ax.text(50, 17, "📄 ଡାକ୍ତରଙ୍କ ପାଇଁ ସାରାଂଶ (Print Doctor Summary)", fontsize=13, fontweight='bold', color='#b4471b', ha='center')

    prog_btn = patches.FancyBboxPatch((8, 4), 84, 8, boxstyle="round,pad=0.6", fc='#b4471b', ec='#b4471b')
    ax.add_patch(prog_btn)
    ax.text(50, 7, "📈 ମୋର ପ୍ରଗତି ଦେଖନ୍ତୁ (View My Progress)", fontsize=14, fontweight='bold', color='#ffffff', ha='center')

    plt.tight_layout()
    out_png = "docs/showcase/ui/02_risk_result_screen.png"
    plt.savefig(out_png, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Generated {out_png}")

def generate_progress_mockup():
    fig, ax = plt.subplots(figsize=(8, 11), dpi=150)
    fig.patch.set_facecolor('#fdf8f0')
    ax.set_facecolor('#fdf8f0')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Header
    ax.text(8, 94, "📈 ମୋର ପ୍ରଗତି (My Progress)", fontsize=18, fontweight='bold', color='#1d1d1b')

    # Caregiver Summary Card
    cg_card = patches.FancyBboxPatch((8, 71), 84, 19, boxstyle="round,pad=1.0", fc='#ffffff', ec='#d8cfc2', lw=2)
    ax.add_patch(cg_card)
    ax.text(12, 85, "👨‍👩‍👦 ଯତ୍ନକାରୀ ଓ ପରିବାର ସାରାଂଶ (Caregiver Overview)", fontsize=13, fontweight='bold', color='#b4471b')

    # Mini stat boxes
    b1 = patches.FancyBboxPatch((12, 73), 23, 10, boxstyle="round,pad=0.4", fc='#faf8f5', ec='#d8cfc2')
    ax.add_patch(b1)
    ax.text(23.5, 79.5, "ସମୁଦାୟ ଖେଳ", fontsize=9, color='#5a5650', ha='center')
    ax.text(23.5, 75, "18", fontsize=18, fontweight='800', color='#1d1d1b', ha='center')

    b2 = patches.FancyBboxPatch((38, 73), 24, 10, boxstyle="round,pad=0.4", fc='#faf8f5', ec='#d8cfc2')
    ax.add_patch(b2)
    ax.text(50, 79.5, "ହାରାହାରି ସଠିକତା", fontsize=9, color='#5a5650', ha='center')
    ax.text(50, 75, "84%", fontsize=18, fontweight='800', color='#1d1d1b', ha='center')

    b3 = patches.FancyBboxPatch((65, 73), 24, 10, boxstyle="round,pad=0.4", fc='#faf8f5', ec='#d8cfc2')
    ax.add_patch(b3)
    ax.text(77, 79.5, "ଶେଷ ଯାଞ୍ଚ ସ୍ତର", fontsize=9, color='#5a5650', ha='center')
    ax.text(77, 75, "🛡️ Lower", fontsize=13, fontweight='bold', color='#1b5e20', ha='center')

    # Cognitive Trend SVG Mockup
    chart_card = patches.FancyBboxPatch((8, 38), 84, 29, boxstyle="round,pad=1.0", fc='#ffffff', ec='#d8cfc2', lw=2)
    ax.add_patch(chart_card)
    ax.text(12, 62, "📈 ଖେଳର ସଠିକତା ଧାରା (Game Accuracy Trend)", fontsize=13, fontweight='bold', color='#1d1d1b')

    # Grid lines inside chart
    for y_val in [43, 48, 53, 58]:
        ax.plot([16, 86], [y_val, y_val], color='#e0d7cb', linestyle='--', lw=0.8)

    # Plot sample data points and spline
    xs = [18, 28, 38, 48, 58, 68, 78, 84]
    ys = [45, 47, 51, 49, 54, 56, 55, 57]
    ax.plot(xs, ys, color='#b4471b', lw=3, marker='o', markersize=6, markerfacecolor='#ffffff', markeredgewidth=2)
    for x, y, val in zip(xs, ys, [65, 70, 85, 78, 90, 95, 92, 96]):
        ax.text(x, y + 1.2, f"{val}%", fontsize=8, fontweight='bold', color='#1d1d1b', ha='center')

    # Saved Local Screening Assessments
    rec_card = patches.FancyBboxPatch((8, 14), 84, 20, boxstyle="round,pad=1.0", fc='#ffffff', ec='#d8cfc2', lw=2)
    ax.add_patch(rec_card)
    ax.text(12, 29, "📋 ସଞ୍ଚିତ ସ୍ୱାସ୍ଥ୍ୟ ଯାଞ୍ଚ ରେକର୍ଡ (Opt-in Local History)", fontsize=12, fontweight='bold', color='#1d1d1b')
    ax.text(14, 24, "Date          Score    Band              Model", fontsize=9, fontweight='bold', color='#5a5650')
    ax.plot([12, 88], [22.5, 22.5], color='#d8cfc2', lw=1)
    ax.text(14, 18.5, "2026-11-24    0.285    🛡️ Lower Risk     Demographics Only", fontsize=9, color='#1d1d1b')

    # Bottom Home button
    home_btn = patches.FancyBboxPatch((8, 3), 84, 8, boxstyle="round,pad=0.6", fc='#b4471b', ec='#b4471b')
    ax.add_patch(home_btn)
    ax.text(50, 6, "🏠 ମୂଳ ପୃଷ୍ଠା (Home)", fontsize=14, fontweight='bold', color='#ffffff', ha='center')

    plt.tight_layout()
    out_png = "docs/showcase/ui/03_my_progress_screen.png"
    plt.savefig(out_png, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Generated {out_png}")

if __name__ == '__main__':
    setup_dirs()
    generate_wizard_mockup()
    generate_result_mockup()
    generate_progress_mockup()
