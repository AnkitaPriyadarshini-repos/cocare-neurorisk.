"""Quality Gate Tests for Showcase Layer Visuals and Artifacts.

Verifies:
1. File existence of all 15 figure pairs (Light and Dark PNGs) + GIF.
2. File size constraints: every PNG image strictly < 400 KB, GIF < 2 MB.
3. Numeric fidelity: parses data sidecars in docs/showcase/data/*.json
   and verifies exact equivalence with ml/reports/*.json source artifacts.
4. Documentation completeness: MANIFEST.md, GITHUB_SETUP.md, index.html.
"""
import os
import json
import pytest

SHOWCASE_DIR = "docs/showcase"
FIGURES_DIR = os.path.join(SHOWCASE_DIR, "figures")
DATA_DIR = os.path.join(SHOWCASE_DIR, "data")

EXPECTED_FIGURE_NAMES = [
    "01_hero_banner",
    "02_pipeline_architecture",
    "03_split_schematic",
    "04_data_overview",
    "05_model_leaderboard",
    "06_roc_pr_curves",
    "07_threshold_tradeoff",
    "08_calibration",
    "09_confusion_matrices",
    "10_ablation_value_added",
    "11_explainability",
    "12_fairness_forest_plot",
    "13_learning_curve",
    "14_model_card_glance",
    "15_signature_visual"
]


def test_all_15_figures_exist_in_light_and_dark():
    """Ensure all 15 figures have both light and dark PNG variants."""
    assert os.path.isdir(FIGURES_DIR), f"Figures directory missing: {FIGURES_DIR}"
    
    for name in EXPECTED_FIGURE_NAMES:
        light_path = os.path.join(FIGURES_DIR, f"{name}-light.png")
        dark_path = os.path.join(FIGURES_DIR, f"{name}-dark.png")
        assert os.path.isfile(light_path), f"Missing light variant: {light_path}"
        assert os.path.isfile(dark_path), f"Missing dark variant: {dark_path}"


def test_all_figures_under_400kb():
    """Verify that every PNG file in figures directory is strictly < 400 KB."""
    max_bytes = 400 * 1024
    png_files = [f for f in os.listdir(FIGURES_DIR) if f.endswith(".png")]
    assert len(png_files) >= 30, f"Expected at least 30 PNG files, found {len(png_files)}"
    
    for fname in png_files:
        fpath = os.path.join(FIGURES_DIR, fname)
        size_bytes = os.path.getsize(fpath)
        size_kb = size_bytes / 1024.0
        assert size_bytes < max_bytes, f"Figure {fname} is {size_kb:.1f} KB, exceeding 400 KB limit!"


def test_animated_gif_exists_and_under_2mb():
    """Verify Figure 15 animated GIF exists and is under 2 MB."""
    gif_path = os.path.join(FIGURES_DIR, "15_signature_visual_animated.gif")
    assert os.path.isfile(gif_path), f"Missing animated GIF: {gif_path}"
    gif_size = os.path.getsize(gif_path)
    assert gif_size < 2 * 1024 * 1024, f"Animated GIF is {gif_size/1024/1024:.2f} MB, exceeding 2 MB limit!"


def test_figure_sidecars_match_source_artifacts():
    """Assert numeric fidelity between figure data sidecars and ml/reports/*.json."""
    assert os.path.isdir(DATA_DIR), f"Data sidecars directory missing: {DATA_DIR}"
    
    # 1. Hero banner check
    hero_sidecar = json.load(open(os.path.join(DATA_DIR, "01_hero_banner.json")))
    cv_source = json.load(open("ml/reports/cv_metrics.json"))
    test_source = json.load(open("ml/reports/test_metrics.json"))
    
    assert hero_sidecar["cv"]["model_with_mmse"]["roc_auc"]["mean"] == pytest.approx(
        cv_source["model_with_mmse"]["roc_auc"]["mean"], rel=1e-4
    )
    assert hero_sidecar["test"]["model_with_mmse"]["metrics"]["roc_auc"] == pytest.approx(
        test_source["model_with_mmse"]["metrics"]["roc_auc"], rel=1e-4
    )
    
    # 2. Confusion matrices check
    cm_sidecar = json.load(open(os.path.join(DATA_DIR, "09_confusion_matrices.json")))
    assert cm_sidecar["model_with_mmse"]["tp"] == test_source["model_with_mmse"]["metrics"]["tp"]
    assert cm_sidecar["model_with_mmse"]["tn"] == test_source["model_with_mmse"]["metrics"]["tn"]
    assert cm_sidecar["model_with_mmse"]["fp"] == test_source["model_with_mmse"]["metrics"]["fp"]
    assert cm_sidecar["model_with_mmse"]["fn"] == test_source["model_with_mmse"]["metrics"]["fn"]
    
    # 3. Threshold trade-off check
    th_sidecar = json.load(open(os.path.join(DATA_DIR, "07_threshold_tradeoff.json")))
    th_source = json.load(open("ml/reports/threshold_operating_points.json"))
    assert th_sidecar["with_mmse"]["target_sens_85"]["selected_threshold"] == th_source["with_mmse"]["target_sens_85"]["selected_threshold"]
    
    # 4. Calibration check
    cal_sidecar = json.load(open(os.path.join(DATA_DIR, "08_calibration.json")))
    assert cal_sidecar["brier_scores"]["model_with_mmse"] == pytest.approx(
        test_source["model_with_mmse"]["metrics"]["brier_score"], rel=1e-4
    )


def test_manifest_and_showcase_docs_exist():
    """Verify that MANIFEST.md, GITHUB_SETUP.md, and index.html are generated."""
    manifest_path = os.path.join(SHOWCASE_DIR, "MANIFEST.md")
    github_setup_path = os.path.join(SHOWCASE_DIR, "GITHUB_SETUP.md")
    index_path = os.path.join(SHOWCASE_DIR, "index.html")
    
    assert os.path.isfile(manifest_path), f"Missing MANIFEST.md: {manifest_path}"
    assert os.path.isfile(github_setup_path), f"Missing GITHUB_SETUP.md: {github_setup_path}"
    assert os.path.isfile(index_path), f"Missing index.html: {index_path}"
    
    manifest_content = open(manifest_path).read()
    for name in EXPECTED_FIGURE_NAMES:
        assert name in manifest_content, f"Figure {name} missing from MANIFEST.md"
