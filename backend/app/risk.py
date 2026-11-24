"""FastAPI router for cognitive risk screening (Additive ML Module).

Endpoints:
- GET  /api/risk/form-spec   -> Form definition schema for frontend intake form
- POST /api/risk/predict     -> Stateless risk assessment and lightweight explanation
- GET  /api/risk/model-info  -> Model metadata, thresholds, and performance metrics
"""
import os
import json
import logging
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/risk", tags=["Risk Screening"])

# Models directory path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND_MODELS_DIR = os.path.join(BASE_DIR, "backend", "models")
ML_ARTIFACTS_DIR = os.path.join(BASE_DIR, "ml", "artifacts")

_LOADED_MODELS: Dict[str, Any] = {}
_LOADED_METADATA: Dict[str, Any] = {}
_LOADED_FORM_SPEC: Optional[Dict[str, Any]] = None


def get_models_dir() -> str:
    if os.path.exists(os.path.join(BACKEND_MODELS_DIR, "model_with_mmse.joblib")):
        return BACKEND_MODELS_DIR
    return ML_ARTIFACTS_DIR


def get_form_spec() -> Dict[str, Any]:
    global _LOADED_FORM_SPEC
    if _LOADED_FORM_SPEC is not None:
        return _LOADED_FORM_SPEC

    models_dir = get_models_dir()
    spec_path = os.path.join(models_dir, "form_spec.json")
    if not os.path.exists(spec_path):
        spec_path = os.path.join(ML_ARTIFACTS_DIR, "form_spec.json")

    if not os.path.exists(spec_path):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model form specification not available"
        )

    with open(spec_path, "r", encoding="utf-8") as f:
        _LOADED_FORM_SPEC = json.load(f)
    return _LOADED_FORM_SPEC


def get_model(variant: str):
    """Lazily load model and metadata once into memory."""
    global _LOADED_MODELS, _LOADED_METADATA

    if variant in _LOADED_MODELS and variant in _LOADED_METADATA:
        return _LOADED_MODELS[variant], _LOADED_METADATA[variant]

    models_dir = get_models_dir()
    model_path = os.path.join(models_dir, f"{variant}.joblib")
    meta_path = os.path.join(models_dir, f"{variant}_metadata.json")

    if not os.path.exists(model_path) or not os.path.exists(meta_path):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Risk screening model '{variant}' is not available."
        )

    try:
        import joblib
        model = joblib.load(model_path)
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        _LOADED_MODELS[variant] = model
        _LOADED_METADATA[variant] = metadata
        return model, metadata
    except Exception as e:
        logger.error(f"Failed to load model {variant}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error initializing risk screening model: {str(e)}"
        )


class PredictIn(BaseModel):
    profile: Dict[str, Any]
    use_mmse: bool = False


def validate_profile(profile: Dict[str, Any], use_mmse: bool):
    """Validate user profile against metadata rules. Returns 422 on violations."""
    allowed_fields = {"Age", "Sex", "EDUC", "SES"}
    if use_mmse:
        allowed_fields.add("MMSE")

    # Reject unknown fields
    unknown = set(profile.keys()) - allowed_fields
    if unknown:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown fields rejected: {sorted(list(unknown))}. Allowed fields: {sorted(list(allowed_fields))}"
        )

    # Required field checks
    for req in ["Age", "Sex", "EDUC"]:
        if req not in profile or profile[req] is None:
            raise HTTPException(
                status_code=422,
                detail=f"Field '{req}' is required."
            )

    if use_mmse and ("MMSE" not in profile or profile["MMSE"] is None):
        raise HTTPException(
            status_code=422,
            detail="Field 'MMSE' is required when use_mmse is True."
        )

    # Range and type validation
    try:
        age = float(profile["Age"])
        if not (40 <= age <= 120):
            raise ValueError()
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=422,
            detail="Field 'Age' must be a number between 40 and 120."
        )

    sex = str(profile["Sex"]).strip().upper()
    if sex not in ["M", "F"]:
        raise HTTPException(
            status_code=422,
            detail="Field 'Sex' must be either 'M' or 'F'."
        )
    profile["Sex"] = sex

    try:
        educ = float(profile["EDUC"])
        if not (0 <= educ <= 30):
            raise ValueError()
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=422,
            detail="Field 'EDUC' must be a number between 0 and 30."
        )

    if "SES" in profile and profile["SES"] is not None:
        try:
            ses = float(profile["SES"])
            if not (1 <= ses <= 5):
                raise ValueError()
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=422,
                detail="Field 'SES' must be an integer between 1 and 5."
            )

    if use_mmse:
        try:
            mmse = float(profile["MMSE"])
            if not (0 <= mmse <= 30):
                raise ValueError()
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=422,
                detail="Field 'MMSE' must be a score between 0 and 30."
            )


@router.get("/form-spec")
def get_form_specification():
    """Retrieve the JSON schema specifying fields, bounds, and Odia labels for the screening form."""
    return get_form_spec()


@router.get("/model-info")
def get_model_information():
    """Retrieve metadata, decision thresholds, and performance metrics for active models."""
    info = {}
    for variant in ["model_with_mmse", "model_without_mmse"]:
        _, meta = get_model(variant)
        clean_meta = meta.copy()
        # Do not expose raw background participant summaries in API
        clean_meta.pop("background_summary", None)
        info[variant] = clean_meta
    return info


@router.post("/predict")
def predict_cognitive_risk(body: PredictIn):
    """Perform stateless risk assessment and generate transparent explainability breakdown."""
    validate_profile(body.profile, body.use_mmse)

    variant = "model_with_mmse" if body.use_mmse else "model_without_mmse"
    pipeline, metadata = get_model(variant)

    expected_features = metadata["features"]["all_ordered"]
    row_data = {f: body.profile.get(f, np.nan) for f in expected_features}
    df_in = pd.DataFrame([row_data])

    prob = float(pipeline.predict_proba(df_in)[0, 1])
    threshold = float(metadata["threshold"])

    # Determine risk band
    band = "moderate"
    for b_name, (low, high) in metadata["risk_bands"].items():
        if low <= prob <= high:
            band = b_name
            break

    # Explainability (runtime occlusion)
    # Import explain_one
    from ml.src.explain import explain_one
    explanations = explain_one(
        profile=body.profile,
        pipeline=pipeline,
        reference_medians=metadata.get("reference_medians", {}),
        feature_names=expected_features
    )

    return {
        "probability": round(prob, 4),
        "band": band,
        "threshold": round(threshold, 4),
        "model_variant": variant,
        "explanation": explanations,
        "disclaimer": metadata["disclaimer"],
        "model_version": metadata.get("version", "1.0.0")
    }
