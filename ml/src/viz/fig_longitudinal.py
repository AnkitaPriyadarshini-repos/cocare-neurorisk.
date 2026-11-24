"""Figure 19: Longitudinal Cognitive Risk Trajectory & Early Conversion Dynamics.

Directly adapts and extends Memora Health's longitudinal monitoring paradigm,
illustrating predicted risk progression across patient visits (Visits 1, 2, and 3)
for Stable Non-Demented, Converted (MCI -> Impairment), and Stable Demented cohorts.
"""
import os
import json
import matplotlib.pyplot as plt
import numpy as np
from .theme import apply_axes_style, add_figure_footer, save_figure_pair


def create_longitudinal_figure(theme: dict, mode: str) -> plt.Figure:
    with open("ml/reports/longitudinal_trajectories.json", "r") as f:
        data = json.load(f)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.2), facecolor=theme["bg"])
    
    thresh = data["screening_threshold"]
    trajs = data["trajectories"]
    
    # --- SUBPLOT 1: Mean Risk Probability Across Visits ---
    apply_axes_style(ax1, theme)
    
    visits = [1, 2, 3]
    
    # Stable Nondemented
    nd_mean = [trajs["Nondemented"][f"visit_{v}"]["mean_risk_oof"] for v in visits]
    nd_q25 = [trajs["Nondemented"][f"visit_{v}"]["q25_risk_oof"] for v in visits]
    nd_q75 = [trajs["Nondemented"][f"visit_{v}"]["q75_risk_oof"] for v in visits]
    nd_n = trajs["Nondemented"]["total_participants"]
    nd_v = trajs["Nondemented"]["total_visits"]
    
    # Converted
    conv_mean = [trajs["Converted"][f"visit_{v}"]["mean_risk_oof"] for v in visits]
    conv_q25 = [trajs["Converted"][f"visit_{v}"]["q25_risk_oof"] for v in visits]
    conv_q75 = [trajs["Converted"][f"visit_{v}"]["q75_risk_oof"] for v in visits]
    conv_n = trajs["Converted"]["total_participants"]
    conv_v = trajs["Converted"]["total_visits"]
    
    # Demented
    dem_mean = [trajs["Demented"][f"visit_{v}"]["mean_risk_oof"] for v in visits]
    dem_q25 = [trajs["Demented"][f"visit_{v}"]["q25_risk_oof"] for v in visits]
    dem_q75 = [trajs["Demented"][f"visit_{v}"]["q75_risk_oof"] for v in visits]
    dem_n = trajs["Demented"]["total_participants"]
    dem_v = trajs["Demented"]["total_visits"]
    
    # Plot trajectories with confidence ribbons
    ax1.plot(visits, nd_mean, color=theme["success"], lw=2.6, marker="o", markersize=7, label=f"Stable Non-Demented (n={nd_n} participants, {nd_v} visits)")
    ax1.fill_between(visits, nd_q25, nd_q75, color=theme["success"], alpha=0.15)
    
    ax1.plot(visits, conv_mean, color=theme["accent_secondary"], lw=2.8, linestyle="--", marker="s", markersize=8, label=f"Converted (n={conv_n} participants, {conv_v} visits; exploratory)")
    ax1.fill_between(visits, conv_q25, conv_q75, color=theme["accent_secondary"], alpha=0.18)
    
    ax1.plot(visits, dem_mean, color=theme["danger"], lw=2.6, marker="^", markersize=7, label=f"Stable Demented (n={dem_n} participants, {dem_v} visits)")
    ax1.fill_between(visits, dem_q25, dem_q75, color=theme["danger"], alpha=0.15)
    
    # Screening threshold line
    ax1.axhline(thresh, color=theme["accent_primary"], linestyle=":", lw=1.8, label=f"Screening Threshold ({thresh:.3f})")
    ax1.axhspan(0.0, 0.221, color=theme["success"], alpha=0.06)
    ax1.axhspan(0.411, 1.0, color=theme["danger"], alpha=0.06)
    
    ax1.set_title("Out-of-Fold Risk Trajectories Across Clinical Visits", fontsize=12, fontweight="bold", pad=12)
    ax1.set_xlabel("Clinical Assessment Visit Number", fontsize=11, labelpad=8)
    ax1.set_ylabel("Out-of-Fold Predicted Risk Probability", fontsize=11, labelpad=8)
    ax1.set_xticks(visits)
    ax1.set_xticklabels(["Visit 1 (Baseline)", "Visit 2 (~1.5 yrs)", "Visit 3 (~3.0 yrs)"], fontsize=10, fontweight="bold")
    ax1.set_ylim(0.0, 1.05)
    ax1.legend(loc="upper left", framealpha=0.85, facecolor=theme["card_bg"], edgecolor=theme["border"], fontsize=8.5)
    
    # Conversion inflection arrow
    ax1.annotate(
        "Exploratory (n=14 participants):\nMean OOF risk rises from 0.24 to 0.42,\ncrossing screening threshold",
        xy=(2, conv_mean[1]),
        xytext=(1.35, 0.60),
        arrowprops=dict(arrowstyle="->", color=theme["accent_secondary"], lw=1.5),
        fontsize=8.5,
        color=theme["text"],
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.4", fc=theme["card_bg"], ec=theme["border"], alpha=0.9)
    )

    # --- SUBPLOT 2: Risk Trajectory vs CDR Progression ---
    apply_axes_style(ax2, theme)
    
    conv_cdr = [trajs["Converted"][f"visit_{v}"]["mean_cdr"] for v in visits]
    dem_cdr = [trajs["Demented"][f"visit_{v}"]["mean_cdr"] for v in visits]
    
    ax2.plot(visits, conv_mean, color=theme["accent_secondary"], lw=2.6, marker="s", markersize=7, label=f"Converted: OOF Risk (n={conv_n})")
    ax2.plot(visits, conv_cdr, color=theme["purple"], lw=2.4, linestyle="-.", marker="d", markersize=7, label=f"Converted: Mean CDR (n={conv_n})")
    
    ax2.plot(visits, dem_mean, color=theme["danger"], lw=2.0, linestyle=":", marker="^", markersize=6, alpha=0.6, label=f"Demented: OOF Risk (n={dem_n})")
    ax2.plot(visits, dem_cdr, color=theme["text_muted"], lw=1.8, linestyle=":", marker="x", markersize=6, alpha=0.6, label=f"Demented: Mean CDR (n={dem_n})")
    
    ax2.set_title("OOF Risk Progression vs. Clinical CDR Score", fontsize=12, fontweight="bold", pad=12)
    ax2.set_xlabel("Clinical Assessment Visit Number", fontsize=11, labelpad=8)
    ax2.set_ylabel("OOF Risk Score / Clinical CDR Rating", fontsize=11, labelpad=8)
    ax2.set_xticks(visits)
    ax2.set_xticklabels(["Visit 1 (Baseline)", "Visit 2 (~1.5 yrs)", "Visit 3 (~3.0 yrs)"], fontsize=10, fontweight="bold")
    ax2.set_ylim(0.0, 1.05)
    ax2.legend(loc="lower right", framealpha=0.85, facecolor=theme["card_bg"], edgecolor=theme["border"], fontsize=8.5)
    
    ax2.annotate(
        "Exploratory (n=14):\nOOF risk elevation (0.42) corresponds\nwith emerging CDR impairment (0.33)",
        xy=(2, conv_mean[1]),
        xytext=(1.10, 0.82),
        arrowprops=dict(arrowstyle="->", color=theme["accent_primary"], lw=1.4),
        fontsize=8.5,
        color=theme["text"],
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.4", fc=theme["card_bg"], ec=theme["border"], alpha=0.9)
    )

    add_figure_footer(
        fig, theme,
        dataset="OASIS-1 Longitudinal Cohort (150 participants; 5-Fold StratifiedGroupKFold OOF Predictions)",
        disclaimer="Out-of-fold predictions only | Converted cohort (n=14) is exploratory due to small sample size"
    )
    plt.tight_layout(rect=[0.02, 0.05, 0.98, 0.96])
    return fig


def run(output_dir="docs/showcase/figures", data_dir="docs/showcase/data"):
    with open("ml/reports/longitudinal_trajectories.json", "r") as f:
        data = json.load(f)
    return save_figure_pair(
        create_longitudinal_figure,
        "19_longitudinal_trajectory",
        data_payload=data,
        output_dir=output_dir,
        data_dir=data_dir
    )


generate = run


if __name__ == "__main__":
    run()
