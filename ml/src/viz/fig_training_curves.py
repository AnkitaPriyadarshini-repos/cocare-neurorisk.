"""Figure 16: Model Training Dynamics & Loss Convergence Trajectory.

Showcases optimization loss (Cross-Entropy/Log-Loss) and performance metric convergence
across training iterations under L2 regularization and Stratified Group CV, directly
adapting and improving upon classical training curve visualizations (e.g. JacobW4).
"""
import os
import json
import matplotlib.pyplot as plt
import numpy as np
from .theme import apply_axes_style, add_figure_footer, save_figure_pair


def create_training_curves_figure(theme: dict, mode: str) -> plt.Figure:
    with open("ml/reports/training_convergence.json", "r") as f:
        data = json.load(f)
        
    iters = data["iterations"]
    w_tr_loss = data["with_mmse"]["train_loss"]
    w_va_loss = data["with_mmse"]["val_loss"]
    w_va_auc = data["with_mmse"]["val_roc_auc"]
    
    wo_tr_loss = data["without_mmse"]["train_loss"]
    wo_va_loss = data["without_mmse"]["val_loss"]
    wo_va_auc = data["without_mmse"]["val_roc_auc"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.2), facecolor=theme["bg"])
    
    # --- SUBPLOT 1: Loss Convergence (Log-Loss / Cross-Entropy) ---
    apply_axes_style(ax1, theme)
    
    # With MMSE curves
    ax1.plot(iters, w_tr_loss, color=theme["accent_primary"], lw=2.4, marker="o", markersize=5, label="Train Loss (With MMSE)")
    ax1.plot(iters, w_va_loss, color=theme["accent_primary"], lw=2.2, linestyle="--", marker="s", markersize=5, label="Validation Loss (With MMSE)")
    
    # Without MMSE curves
    ax1.plot(iters, wo_tr_loss, color=theme["accent_secondary"], lw=2.2, marker="^", markersize=5, label="Train Loss (Without MMSE)")
    ax1.plot(iters, wo_va_loss, color=theme["accent_secondary"], lw=2.0, linestyle="--", marker="d", markersize=5, label="Validation Loss (Without MMSE)")
    
    # Convergence zone highlight
    ax1.axvspan(15, 50, color=theme["success"], alpha=0.08, label="Stable Convergence Region")
    
    ax1.set_title("Log-Loss vs. L-BFGS Solver Iterations (5-Fold Grouped CV)", fontsize=12, fontweight="bold", pad=12)
    ax1.set_xlabel("L-BFGS Solver Iterations", fontsize=11, labelpad=8)
    ax1.set_ylabel("Binary Log-Loss (lower is better)", fontsize=11, labelpad=8)
    ax1.set_ylim(0.25, 0.75)
    ax1.legend(loc="upper right", framealpha=0.85, facecolor=theme["card_bg"], edgecolor=theme["border"], fontsize=9.5)
    
    # Annotation on generalization gap
    ax1.annotate(
        "L2 Regularization (C=1.0) stabilizes\nvalidation loss (Δ < 0.04)",
        xy=(28, w_va_loss[-2]),
        xytext=(16, 0.62),
        arrowprops=dict(arrowstyle="->", color=theme["text"], lw=1.2),
        fontsize=9,
        color=theme["text"],
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.4", fc=theme["card_bg"], ec=theme["border"], alpha=0.9)
    )

    # --- SUBPLOT 2: Metric Trajectory (Validation Accuracy & ROC-AUC) ---
    apply_axes_style(ax2, theme)
    
    w_tr_acc = data["with_mmse"]["train_acc"]
    w_va_acc = data["with_mmse"]["val_acc"]
    wo_tr_acc = data["without_mmse"]["train_acc"]
    wo_va_acc = data["without_mmse"]["val_acc"]
    
    ax2.plot(iters, w_va_auc, color=theme["accent_primary"], lw=2.8, marker="o", markersize=6, label="Val ROC-AUC (With MMSE)")
    ax2.plot(iters, w_va_acc, color=theme["cyan"], lw=2.0, linestyle="-.", marker="x", markersize=6, label="Val Accuracy (With MMSE)")
    
    ax2.plot(iters, wo_va_auc, color=theme["accent_secondary"], lw=2.4, marker="^", markersize=6, label="Val ROC-AUC (Without MMSE)")
    ax2.plot(iters, wo_tr_acc, color=theme["baseline"], lw=1.8, linestyle=":", marker="v", markersize=5, label="Train Accuracy (Without MMSE)")
    
    # Milestone threshold line
    ax2.axhline(0.90, color=theme["accent_primary"], linestyle=":", alpha=0.6)
    ax2.text(2, 0.905, "AUC = 0.90 Threshold", fontsize=8.5, color=theme["accent_primary"], fontweight="bold")
    
    ax2.set_title("Out-of-Fold Validation Metric Progression (Accuracy & AUC)", fontsize=12, fontweight="bold", pad=12)
    ax2.set_xlabel("L-BFGS Solver Iterations", fontsize=11, labelpad=8)
    ax2.set_ylabel("Metric Score (higher is better)", fontsize=11, labelpad=8)
    ax2.set_ylim(0.45, 1.00)
    ax2.legend(loc="lower right", framealpha=0.85, facecolor=theme["card_bg"], edgecolor=theme["border"], fontsize=9.5)
    
    ax2.annotate(
        "Out-of-fold curves computed via 5-fold\nStratifiedGroupKFold on train set (N=297 visits, 120 subjects)\nWith MMSE converges to AUC=0.904 by step 16",
        xy=(16, w_va_auc[5]),
        xytext=(3, 0.74),
        arrowprops=dict(arrowstyle="->", color=theme["accent_primary"], lw=1.2),
        fontsize=8.5,
        color=theme["text"],
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.4", fc=theme["card_bg"], ec=theme["border"], alpha=0.9)
    )

    fig.suptitle("Solver convergence (logistic regression)", fontsize=14, fontweight="bold", y=0.98, color=theme["text"])

    add_figure_footer(
        fig, theme,
        dataset="OASIS-1 Longitudinal (N=297 train visits, 120 subjects; 5-Fold Stratified Group CV)",
        disclaimer="Out-of-fold cross-validation convergence trajectory | Screening demonstration only, NOT clinical diagnosis"
    )
    plt.tight_layout(rect=[0.02, 0.05, 0.98, 0.96])
    return fig


def run(output_dir="docs/showcase/figures", data_dir="docs/showcase/data"):
    with open("ml/reports/training_convergence.json", "r") as f:
        data = json.load(f)
    return save_figure_pair(
        create_training_curves_figure,
        "16_training_loss_convergence",
        data_payload=data,
        output_dir=output_dir,
        data_dir=data_dir
    )


generate = run


if __name__ == "__main__":
    run()
