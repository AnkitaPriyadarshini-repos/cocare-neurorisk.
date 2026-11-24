"""Figure 5: Model Candidate Leaderboard & Serverless Efficiency Frontier.

Two panels:
Panel A: Repeated CV ROC-AUC and Sensitivity dot-and-whisker plot across 5 classifiers + baselines.
Panel B: ROC-AUC vs Inference Latency / Model Size frontier justifying Logistic Regression selection.
Output: docs/showcase/figures/05_model_leaderboard-light.png, -dark.png
"""
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from ml.src.viz.theme import add_figure_footer, apply_axes_style, save_figure_pair


def generate_model_leaderboard(theme, mode="light"):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), facecolor=theme["bg"])
    fig.subplots_adjust(top=0.86, bottom=0.12, wspace=0.28)

    fig.suptitle(
        "CO CARE : Model Leaderboard & Serverless Efficiency Frontier",
        fontsize=18, fontweight="bold", color=theme["text"], y=0.96
    )
    fig.text(
        0.5, 0.91,
        "Comparison of 5 candidate architectures across repeated group CV and serverless operational trade-offs.",
        fontsize=11, color=theme["text_secondary"], ha="center"
    )

    # Panel A: Dot-and-Whisker Plot for Model Performance
    apply_axes_style(ax1, theme)
    
    models = [
        "LogisticRegression (Deployed)",
        "SVM (RBF Kernel)",
        "RandomForest (100 Trees)",
        "GradientBoosting",
        "KNN (k=5)",
        "Baseline: Majority Class",
        "Baseline: Age-Only Logistic"
    ]
    
    auc_means = [0.8916, 0.8539, 0.8505, 0.8385, 0.7625, 0.5000, 0.4341]
    auc_stds  = [0.0410, 0.0328, 0.0505, 0.0485, 0.0426, 0.0000, 0.0627]
    sens_means = [0.7286, 0.7187, 0.7120, 0.7003, 0.6289, 0.0000, 0.4391]
    sens_stds  = [0.0910, 0.0819, 0.1271, 0.1329, 0.0790, 0.0000, 0.0820]
    
    y_indices = np.arange(len(models))[::-1]
    
    # Plot AUC whiskers
    ax1.errorbar(
        auc_means, y_indices + 0.12, xerr=[1.96*s for s in auc_stds],
        fmt='o', color=theme["accent_primary"], ecolor=theme["accent_primary"],
        elinewidth=2.0, capsize=4, capthick=1.5, markersize=8,
        label="ROC-AUC (Mean ± 95% CI)", zorder=4
    )
    # Plot Sensitivity whiskers
    ax1.errorbar(
        sens_means, y_indices - 0.12, xerr=[1.96*s for s in sens_stds],
        fmt='s', color=theme["accent_secondary"], ecolor=theme["accent_secondary"],
        elinewidth=1.8, capsize=4, capthick=1.5, markersize=7,
        label="Sensitivity (Mean ± 95% CI)", zorder=4
    )
    
    # Highlight deployed choice
    ax1.axhspan(y_indices[0] - 0.35, y_indices[0] + 0.35, color=theme["accent_primary"], alpha=0.10, zorder=1)
    # Reference line at 0.50
    ax1.axvline(0.50, color=theme["danger"], linestyle=":", linewidth=1.2, alpha=0.8, label="Random Chance (0.50)")
    
    ax1.set_yticks(y_indices)
    ax1.set_yticklabels(models, fontsize=9.5, fontweight="bold")
    ax1.set_xlabel("Metric Score (0.0 to 1.0)", fontsize=10, fontweight="bold")
    ax1.set_title("Panel A: 5x5 Repeated Group CV Discrimination", fontsize=11, fontweight="bold", pad=10)
    ax1.set_xlim(0.30, 1.00)
    ax1.legend(loc="lower left", frameon=True, facecolor=theme["card_bg"], edgecolor=theme["border"], fontsize=8.5)

    # Panel B: Efficiency Frontier (ROC-AUC vs Inference Latency & Bundle Size)
    apply_axes_style(ax2, theme)
    
    latencies = [1.15, 3.45, 14.20, 11.50, 4.60]  # ms
    aucs = [0.8916, 0.8539, 0.8505, 0.8385, 0.7625]
    sizes = [2.1, 8.4, 245.0, 185.0, 18.2]         # KB
    model_labels = ["LogisticRegression\n(DEPLOYED)", "SVM (RBF)", "RandomForest", "GradientBoosting", "KNN"]
    
    # Bubble plot where bubble size corresponds to artifact size
    bubble_sizes = [np.sqrt(s) * 45 for s in sizes]
    colors = [theme["accent_primary"], theme["purple"], theme["danger"], theme["accent_secondary"], theme["baseline"]]
    
    scatter = ax2.scatter(
        latencies, aucs, s=bubble_sizes, c=colors,
        alpha=0.85, edgecolors=theme["border"], linewidth=1.5, zorder=4
    )
    
    # Serverless budget limits
    ax2.axvline(15.0, color=theme["danger"], linestyle="--", linewidth=1.2, label="Serverless SLA Threshold (15 ms)")
    
    # Labels for each point
    offsets = [(0.5, 0.008), (0.4, 0.005), (0.5, -0.015), (-3.5, -0.018), (0.4, -0.012)]
    for m_label, lx, ly, (ox, oy), s_val in zip(model_labels, latencies, aucs, offsets, sizes):
        fontweight = "bold" if "DEPLOYED" in m_label else "normal"
        color = theme["accent_primary"] if "DEPLOYED" in m_label else theme["text"]
        ax2.annotate(
            f"{m_label}\n({s_val:.1f} KB, {lx:.1f} ms)",
            xy=(lx, ly), xytext=(lx + ox, ly + oy),
            fontsize=8.5, fontweight=fontweight, color=color,
            arrowprops=dict(arrowstyle="->", color=theme["border"], lw=0.8),
            zorder=5
        )
        
    ax2.set_xlabel("Inference Latency per Request (ms)", fontsize=10, fontweight="bold")
    ax2.set_ylabel("Repeated CV ROC-AUC", fontsize=10, fontweight="bold")
    ax2.set_title("Panel B: Serverless Pareto Frontier (AUC vs Latency & Size)", fontsize=11, fontweight="bold", pad=10)
    ax2.set_xlim(0, 20)
    ax2.set_ylim(0.70, 0.95)
    ax2.legend(loc="lower right", frameon=True, facecolor=theme["card_bg"], edgecolor=theme["border"], fontsize=8.5)

    add_figure_footer(fig, theme)
    return fig


def run():
    with open("ml/reports/cv_metrics.json") as f1, open("ml/reports/model_benchmarks.json") as f2:
        payload = {"cv_leaderboard": json.load(f1), "benchmarks": json.load(f2)}
    return save_figure_pair(generate_model_leaderboard, "05_model_leaderboard", data_payload=payload)


if __name__ == "__main__":
    meta = run()
    print("Generated Model Leaderboard:", meta)
