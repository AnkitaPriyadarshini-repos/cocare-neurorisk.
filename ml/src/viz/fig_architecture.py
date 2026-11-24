"""Figure 2: End-to-End Pipeline Architecture Diagram.

Vector-quality diagram illustrating offline training vs online serverless inference,
highlighting leakage-protection boundaries and stateless guarantees.
Output: docs/showcase/figures/02_pipeline_architecture-light.png, -dark.png, .svg
"""
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from ml.src.viz.theme import add_figure_footer, save_figure_pair


def generate_pipeline_architecture(theme, mode="light"):
    fig = plt.figure(figsize=(16, 8.5), facecolor=theme["bg"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(theme["bg"])
    ax.axis("off")

    # Title
    ax.text(
        0.05, 0.94,
        "CO CARE : Machine Learning Pipeline & Serverless Architecture",
        fontsize=22, fontweight="bold", color=theme["text"],
        transform=ax.transAxes
    )
    ax.text(
        0.05, 0.90,
        "Separation of concerns: Leakage-free offline training pipeline decoupled from lightweight serverless inference.",
        fontsize=12, color=theme["text_secondary"],
        transform=ax.transAxes
    )

    # 1. Swimlane: Offline Training Pipeline (Top)
    lane_offline = patches.FancyBboxPatch(
        (0.04, 0.49), 0.92, 0.38,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor=theme["card_bg"],
        edgecolor=theme["border"],
        linewidth=1.2,
        transform=ax.transAxes
    )
    ax.add_patch(lane_offline)
    ax.text(0.06, 0.835, "OFFLINE TRAINING & VALIDATION PIPELINE (REPRODUCIBLE & LEAKAGE-FREE)", fontsize=11, fontweight="bold", color=theme["accent_primary"], transform=ax.transAxes)

    # Offline Steps
    offline_steps = [
        ("Raw Cohorts", "OASIS Longitudinal\nLASI-DAD (Config Adapter)", theme["text_secondary"]),
        ("Leakage Protection", "Participant Grouped Split\n(Zero subject overlap)", theme["danger"]),
        ("Preprocessing", "Imputer + Scaler + OHE\n(Fit on Train ONLY)", theme["purple"]),
        ("Model Selection", "5 Candidates (LR, SVM,\nRF, GB, KNN) in Pipeline", theme["cyan"]),
        ("Validation", "5x5 Repeated Group CV\n(25 Evaluations)", theme["accent_primary"]),
        ("Calibration", "Threshold Opt (Sens>=0.85)\n+ Brier Calibration", theme["accent_secondary"]),
        ("Export Artifacts", "joblib models + metadata\n+ form_spec.json", theme["success"]),
    ]

    x_step = 0.06
    step_w = 0.115
    for i, (title, desc, accent) in enumerate(offline_steps):
        box = patches.FancyBboxPatch(
            (x_step, 0.54), step_w, 0.26,
            boxstyle="round,pad=0.01,rounding_size=0.015",
            facecolor=theme["bg"],
            edgecolor=accent,
            linewidth=1.5 if accent == theme["danger"] else 1.0,
            transform=ax.transAxes
        )
        ax.add_patch(box)
        
        # Step number badge
        ax.text(x_step + 0.01, 0.765, f"STEP {i+1}", fontsize=7.5, fontweight="bold", color=accent, transform=ax.transAxes)
        ax.text(x_step + 0.01, 0.715, title, fontsize=10, fontweight="bold", color=theme["text"], transform=ax.transAxes)
        ax.text(x_step + 0.01, 0.615, desc, fontsize=8.5, color=theme["text_secondary"], transform=ax.transAxes)
        
        # Arrow
        if i < len(offline_steps) - 1:
            ax.annotate(
                "", xy=(x_step + step_w + 0.015, 0.67), xytext=(x_step + step_w, 0.67),
                arrowprops=dict(arrowstyle="->", color=theme["text_muted"], lw=1.5),
                xycoords="axes fraction"
            )
        x_step += step_w + 0.017

    # 2. Swimlane: Online Runtime Inference (Bottom)
    lane_online = patches.FancyBboxPatch(
        (0.04, 0.08), 0.92, 0.37,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor=theme["card_bg"],
        edgecolor=theme["border"],
        linewidth=1.2,
        transform=ax.transAxes
    )
    ax.add_patch(lane_online)
    ax.text(0.06, 0.415, "ONLINE SERVERLESS RUNTIME INFERENCE (FASTAPI / VERCEL LAMBDA)", fontsize=11, fontweight="bold", color=theme["accent_secondary"], transform=ax.transAxes)

    online_steps = [
        ("Client Form", "Dynamic rendering from\nform_spec.json (EN / Odia)", theme["cyan"]),
        ("HTTP API Route", "POST /api/risk/predict\nPayload validation (Pydantic)", theme["accent_primary"]),
        ("Stateless Predict", "In-memory LR model\nmodel inference time\n(local, warm) < 1.5 ms", theme["success"]),
        ("Runtime Explainer", "Occlusion sensitivity\nZero C++ dependencies", theme["purple"]),
        ("Localized Insights", "Bilingual risk band &\ntransparent factors", theme["accent_secondary"]),
        ("Stateless Privacy", "Zero participant data\npersisted to DB or logs", theme["danger"])
    ]

    x_step_on = 0.06
    step_w_on = 0.138
    for j, (title, desc, accent) in enumerate(online_steps):
        box = patches.FancyBboxPatch(
            (x_step_on, 0.13), step_w_on, 0.25,
            boxstyle="round,pad=0.01,rounding_size=0.015",
            facecolor=theme["bg"],
            edgecolor=accent,
            linewidth=1.5 if accent == theme["danger"] else 1.0,
            transform=ax.transAxes
        )
        ax.add_patch(box)
        
        ax.text(x_step_on + 0.01, 0.345, f"PHASE {j+1}", fontsize=7.5, fontweight="bold", color=accent, transform=ax.transAxes)
        ax.text(x_step_on + 0.01, 0.295, title, fontsize=10, fontweight="bold", color=theme["text"], transform=ax.transAxes)
        ax.text(x_step_on + 0.01, 0.205, desc, fontsize=8.5, color=theme["text_secondary"], transform=ax.transAxes)
        
        if j < len(online_steps) - 1:
            ax.annotate(
                "", xy=(x_step_on + step_w_on + 0.015, 0.25), xytext=(x_step_on + step_w_on, 0.25),
                arrowprops=dict(arrowstyle="->", color=theme["text_muted"], lw=1.5),
                xycoords="axes fraction"
            )
        x_step_on += step_w_on + 0.017

    # Connector arrow from Export to API
    ax.annotate(
        "Deploy models & form_spec\n(<250MB bundle ceiling)",
        xy=(0.28, 0.46), xytext=(0.88, 0.53),
        arrowprops=dict(arrowstyle="->", color=theme["success"], lw=2.0, connectionstyle="angle,angleA=0,angleB=90,rad=10"),
        fontsize=8.5, fontweight="bold", color=theme["success"],
        xycoords="axes fraction"
    )

    add_figure_footer(fig, theme)
    return fig


def run():
    payload = {
        "architecture": "Two-stage decoupled ML pipeline (Offline Training & Serverless Runtime)",
        "offline_stages": 7,
        "online_phases": 6,
        "leakage_safeguards": ["Participant Grouped Split", "Fit-on-train preprocessors", "StratifiedGroupKFold"],
        "serverless_guarantees": ["Stateless privacy", "Latency < 1.5ms", "No C++ compilation in Lambda"]
    }
    return save_figure_pair(generate_pipeline_architecture, "02_pipeline_architecture", data_payload=payload)


if __name__ == "__main__":
    meta = run()
    print("Generated Pipeline Architecture:", meta)
