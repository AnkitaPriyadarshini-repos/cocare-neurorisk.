"""Export and artifact deployment utility."""
import os
import shutil
import json
import joblib
from typing import Dict, Any


def export_model_artifacts(
    variant_name: str,
    pipeline,
    metadata: Dict[str, Any],
    artifacts_dir: str = "ml/artifacts",
    backend_models_dir: str = "backend/models"
):
    """Save trained pipeline and metadata to artifacts and copy to backend/models."""
    os.makedirs(artifacts_dir, exist_ok=True)
    os.makedirs(backend_models_dir, exist_ok=True)

    joblib_name = f"{variant_name}.joblib"
    meta_name = f"{variant_name}_metadata.json"

    art_joblib = os.path.join(artifacts_dir, joblib_name)
    art_meta = os.path.join(artifacts_dir, meta_name)

    # Save to artifacts
    joblib.dump(pipeline, art_joblib)
    with open(art_meta, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    # Copy to backend/models for runtime serving
    shutil.copy2(art_joblib, os.path.join(backend_models_dir, joblib_name))
    shutil.copy2(art_meta, os.path.join(backend_models_dir, meta_name))

    # Also ensure form_spec.json is in backend/models
    form_spec_art = os.path.join(artifacts_dir, "form_spec.json")
    if os.path.exists(form_spec_art):
        shutil.copy2(form_spec_art, os.path.join(backend_models_dir, "form_spec.json"))
