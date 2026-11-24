"""Runtime risk prediction and band classification."""
import os
import json
import joblib
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from .explain import explain_one

_CACHED_MODELS: Dict[str, Any] = {}
_CACHED_METADATA: Dict[str, Any] = {}


def load_model_and_metadata(variant: str, models_dir: Optional[str] = None):
    """Lazily load and cache model pipeline and metadata in memory."""
    global _CACHED_MODELS, _CACHED_METADATA

    if variant in _CACHED_MODELS and variant in _CACHED_METADATA:
        return _CACHED_MODELS[variant], _CACHED_METADATA[variant]

    if models_dir is None:
        # Check backend/models first, fallback to ml/artifacts
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        backend_models = os.path.join(base_dir, "backend", "models")
        ml_artifacts = os.path.join(base_dir, "ml", "artifacts")
        models_dir = backend_models if os.path.exists(os.path.join(backend_models, f"{variant}.joblib")) else ml_artifacts

    model_file = os.path.join(models_dir, f"{variant}.joblib")
    meta_file = os.path.join(models_dir, f"{variant}_metadata.json")

    if not os.path.exists(model_file) or not os.path.exists(meta_file):
        raise FileNotFoundError(f"Model or metadata for '{variant}' not found in '{models_dir}'.")

    model = joblib.load(model_file)
    with open(meta_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    _CACHED_MODELS[variant] = model
    _CACHED_METADATA[variant] = metadata
    return model, metadata


def determine_risk_band(prob: float, threshold: float, risk_bands: Dict[str, list]) -> str:
    """Categorize probability into lower, moderate, or higher risk band."""
    for band_name, (low, high) in risk_bands.items():
        if low <= prob <= high:
            return band_name
    if prob < threshold:
        return "lower"
    return "higher"


def predict_risk(
    profile: Dict[str, Any],
    use_mmse: bool = False,
    models_dir: Optional[str] = None
) -> Dict[str, Any]:
    """Execute risk prediction and explainability for a user profile.

    Args:
        profile: Dictionary of participant features (e.g. Age, Sex, EDUC, SES, MMSE).
        use_mmse: True to use 'model_with_mmse', False for 'model_without_mmse'.
        models_dir: Directory containing .joblib and metadata files.

    Returns:
        Structured prediction dictionary with probability, band, threshold, explanations, and disclaimer.
    """
    variant = "model_with_mmse" if use_mmse else "model_without_mmse"
    pipeline, metadata = load_model_and_metadata(variant, models_dir=models_dir)

    expected_features = metadata["features"]["all_ordered"]

    # Verify 'without_mmse' model never references MMSE
    if not use_mmse and "MMSE" in expected_features:
        raise ValueError("Invalid configuration: 'without_mmse' model contains MMSE feature.")

    # Prepare single-row DataFrame
    row_data = {}
    for f in expected_features:
        row_data[f] = profile.get(f, np.nan)

    df_in = pd.DataFrame([row_data])

    # Predict risk probability
    probability = float(pipeline.predict_proba(df_in)[0, 1])
    threshold = float(metadata["threshold"])
    band = determine_risk_band(probability, threshold, metadata["risk_bands"])

    # Compute lightweight explanations
    reference_medians = metadata.get("reference_medians", {})
    explanations = explain_one(
        profile=profile,
        pipeline=pipeline,
        reference_medians=reference_medians,
        feature_names=expected_features
    )

    return {
        "probability": round(probability, 4),
        "band": band,
        "threshold": round(threshold, 4),
        "model_variant": variant,
        "explanation": explanations,
        "disclaimer": metadata["disclaimer"],
        "model_version": metadata.get("version", "1.0.0")
    }
