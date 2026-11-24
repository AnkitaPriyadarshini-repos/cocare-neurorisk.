"""One-Command Retrain Orchestrator with Rigorous Quality Gates.

Executes end-to-end retraining for OASIS or LASI-DAD:
1. Validates participant grouping (zero subject overlap).
2. Performs label-shuffle permutation check (must be ~0.50).
3. Benchmarks cross-validation against quality gates (min AUC & sensitivity).
4. Refuses to overwrite deployed models unless all gates pass.
5. On success: exports models, regenerates form_spec.json and metadata.
"""
import os
import sys
import argparse
import logging
from typing import Dict, Any
import numpy as np
import pandas as pd
import yaml

from sklearn.model_selection import StratifiedGroupKFold, cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score

from ml.src.datasets.oasis import load_oasis
from ml.src.datasets.lasi_dad import load_lasi_dad
from ml.src.preprocess import clean_raw_data, build_preprocessor
from ml.src.train import train_single_variant
from ml.src.export import export_model_artifacts
from ml.src.generate_form_spec import generate_form_spec_from_mapping

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def retrain_pipeline(
    dataset_name: str = "oasis",
    config_path: str = "ml/config.yaml",
    allow_synthetic: bool = True,
    seed: int = 42
) -> Dict[str, Any]:
    """Run full retrain pipeline with quality gate enforcement."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if not os.path.isabs(config_path):
        config_path = os.path.join(base_dir, config_path)
        
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
        
    logging.info(f"Initiating retrain for dataset: '{dataset_name}' with seed {seed}")
    
    # 1. Load data via designated adapter
    if dataset_name.lower() == "oasis":
        data_path = os.path.join(base_dir, "ml", "data", "oasis_longitudinal.csv")
        mapping_path = os.path.join(base_dir, "ml", "config", "oasis_mapping.yaml")
        X_raw, y_raw, groups = load_oasis(data_path)
    elif dataset_name.lower() in ["lasi_dad", "lasi"]:
        data_path = os.path.join(base_dir, "ml", "data", "lasi_dad_synthetic.csv")
        mapping_path = os.path.join(base_dir, "ml", "config", "lasi_dad_mapping.yaml")
        if not os.path.exists(data_path):
            from ml.src.make_synthetic_lasi import generate_synthetic_lasi_dataset
            logging.info("Generating synthetic LASI-DAD dataset for verification...")
            df_synth = generate_synthetic_lasi_dataset(seed=seed)
            os.makedirs(os.path.dirname(data_path), exist_ok=True)
            df_synth.to_csv(data_path, index=False)
        X_raw, y_raw, groups = load_lasi_dad(data_path, allow_placeholders=allow_synthetic)
    else:
        raise ValueError(f"Unknown dataset '{dataset_name}'. Supported: 'oasis', 'lasi_dad'.")
        
    X_clean, _ = clean_raw_data(X_raw)
    
    # 2. Split with strict participant grouping
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    train_idx, test_idx = next(sgkf.split(X_clean, y_raw, groups=groups))
    
    X_train, X_test = X_clean.iloc[train_idx].copy(), X_clean.iloc[test_idx].copy()
    y_train, y_test = y_raw.iloc[train_idx].copy(), y_raw.iloc[test_idx].copy()
    groups_train = groups.iloc[train_idx]
    
    # Quality Gate 1: Participant Isolation
    train_subjects = set(groups.iloc[train_idx])
    test_subjects = set(groups.iloc[test_idx])
    overlap = train_subjects.intersection(test_subjects)
    if len(overlap) > 0:
        raise RuntimeError(f"QUALITY GATE FAILED: Found {len(overlap)} overlapping participants between train and test!")
    logging.info(f"[GATE PASSED] Participant isolation verified: 0 subject overlap.")
    
    # Quality Gate 2: Label Permutation Check (~0.50 AUC)
    logging.info("Checking label permutation sanity gate...")
    rng = np.random.RandomState(seed)
    y_shuffled = pd.Series(rng.permutation(y_train.values), index=y_train.index)
    
    prep_check = build_preprocessor(["Age", "EDUC", "SES"], ["Sex"])
    pipe_check = Pipeline([
        ("preprocessor", prep_check),
        ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=seed))
    ])
    perm_cv = cross_validate(pipe_check, X_train, y_shuffled, groups=groups_train, cv=sgkf, scoring=["roc_auc"])
    mean_perm_auc = float(np.mean(perm_cv["test_roc_auc"]))
    logging.info(f"Label-shuffled CV ROC-AUC: {mean_perm_auc:.4f}")
    if mean_perm_auc > 0.60:
        raise RuntimeError(f"QUALITY GATE FAILED: Label-shuffled AUC is too high ({mean_perm_auc:.4f} > 0.60). Leakage suspected!")
    logging.info("[GATE PASSED] Label permutation check confirmed near chance (~0.50).")
    
    # Quality Gate 3: Minimum CV Performance Gates
    cv_with = cross_validate(
        Pipeline([
            ("preprocessor", build_preprocessor(["Age", "EDUC", "SES", "MMSE"], ["Sex"])),
            ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=seed))
        ]),
        X_train, y_train, groups=groups_train, cv=sgkf, scoring=["roc_auc", "recall"]
    )
    cv_with_auc = float(np.mean(cv_with["test_roc_auc"]))
    cv_with_recall = float(np.mean(cv_with["test_recall"]))
    
    logging.info(f"'model_with_mmse' CV ROC-AUC: {cv_with_auc:.4f}, Sensitivity: {cv_with_recall:.4f}")
    if cv_with_auc < 0.75 or cv_with_recall < 0.70:
        raise RuntimeError(f"QUALITY GATE FAILED: 'model_with_mmse' failed performance thresholds (AUC={cv_with_auc:.4f}, Rec={cv_with_recall:.4f}).")
    logging.info("[GATE PASSED] Minimum cross-validation performance gates satisfied.")
    
    # 3. Train and tune both variants
    artifacts_dir = os.path.join(base_dir, "ml", "artifacts")
    backend_models_dir = os.path.join(base_dir, "backend", "models")
    
    logging.info("Retraining 'model_with_mmse'...")
    pipe_w, meta_w, _ = train_single_variant(
        variant_name="model_with_mmse",
        X_train=X_train,
        y_train=y_train,
        groups_train=groups_train,
        X_test=X_test,
        y_test=y_test,
        numeric_features=["Age", "EDUC", "SES", "MMSE"],
        categorical_features=["Sex"],
        seed=seed,
        target_sensitivity=0.85
    )
    meta_w["model_status"] = "demo_oasis_not_validated_for_lasi_dad" if dataset_name == "oasis" else "synthetic_lasi_dad_pipeline_test"
    
    logging.info("Retraining 'model_without_mmse'...")
    pipe_wo, meta_wo, _ = train_single_variant(
        variant_name="model_without_mmse",
        X_train=X_train,
        y_train=y_train,
        groups_train=groups_train,
        X_test=X_test,
        y_test=y_test,
        numeric_features=["Age", "EDUC", "SES"],
        categorical_features=["Sex"],
        seed=seed,
        target_sensitivity=0.85
    )
    meta_wo["model_status"] = "demo_oasis_not_validated_for_lasi_dad" if dataset_name == "oasis" else "synthetic_lasi_dad_pipeline_test"
    
    # 4. Overwrite deployed models and artifacts ONLY after all quality gates pass
    export_model_artifacts("model_with_mmse", pipe_w, meta_w, artifacts_dir, backend_models_dir)
    export_model_artifacts("model_without_mmse", pipe_wo, meta_wo, artifacts_dir, backend_models_dir)
    
    # 5. Regenerate form_spec.json from dataset mapping
    form_spec_paths = [
        os.path.join(artifacts_dir, "form_spec.json"),
        os.path.join(backend_models_dir, "form_spec.json")
    ]
    generate_form_spec_from_mapping(mapping_path, form_spec_paths)
    
    logging.info(f"SUCCESS: Retraining complete. Deployed models and form_spec updated for dataset '{dataset_name}'.")
    return {"status": "success", "dataset": dataset_name, "cv_with_auc": cv_with_auc}


def main():
    parser = argparse.ArgumentParser(description="One-command retrain with quality gate validation.")
    parser.add_argument("--dataset", type=str, default="oasis", help="Dataset to train on (oasis or lasi_dad).")
    parser.add_argument("--config", type=str, default="ml/config.yaml", help="Path to config.yaml.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    args = parser.parse_args()
    
    retrain_pipeline(dataset_name=args.dataset, config_path=args.config, seed=args.seed)


if __name__ == "__main__":
    main()
