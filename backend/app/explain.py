"""Runtime explainability module for CO CARE serverless deployment.

Self-contained within backend/app so Vercel does not require ml/ to be deployed.
Uses lightweight feature occlusion with zero C++ or heavy dependencies (model inference ~1 ms (local, warm)).
"""
from typing import Dict, List, Any
import numpy as np
import pandas as pd

FEATURE_TEXTS = {
    "Age": {
        "raises": {
            "key": "risk.age.raises",
            "en": "In this demo model, age raises predicted score relative to typical training-data values.",
            "or": "ଏହି ଡେମୋ ମଡେଲରେ, ସାଧାରଣ ତାଲିମ ମୂଲ୍ୟ ତୁଳନାରେ ବୟସ ଆକଳିତ ସ୍କୋରକୁ ବୃଦ୍ଧି କରେ। [needs native review]"
        },
        "lowers": {
            "key": "risk.age.lowers",
            "en": "In this demo model, age lowers predicted score relative to typical training-data values.",
            "or": "ଏହି ଡେମୋ ମଡେଲରେ, ସାଧାରଣ ତାଲିମ ମୂଲ୍ୟ ତୁଳନାରେ ବୟସ ଆକଳିତ ସ୍କୋରକୁ ହ୍ରାସ କରେ। [needs native review]"
        }
    },
    "EDUC": {
        "raises": {
            "key": "risk.educ.raises",
            "en": "In this demo model, education raises predicted score relative to typical training-data values.",
            "or": "ଏହି ଡେମୋ ମଡେଲରେ, ସାଧାରଣ ତାଲିମ ମୂଲ୍ୟ ତୁଳନାରେ ଶିକ୍ଷା ଆକଳିତ ସ୍କୋରକୁ ବୃଦ୍ଧି କରେ। [needs native review]"
        },
        "lowers": {
            "key": "risk.educ.lowers",
            "en": "In this demo model, education lowers predicted score relative to typical training-data values.",
            "or": "ଏହି ଡେମୋ ମଡେଲରେ, ସାଧାରଣ ତାଲିମ ମୂଲ୍ୟ ତୁଳନାରେ ଶିକ୍ଷା ଆକଳିତ ସ୍କୋରକୁ ହ୍ରାସ କରେ। [needs native review]"
        }
    },
    "SES": {
        "raises": {
            "key": "risk.ses.raises",
            "en": "In this demo model, socioeconomic status raises predicted score relative to typical training-data values.",
            "or": "ଏହି ଡେମୋ ମଡେଲରେ, ସାଧାରଣ ତାଲିମ ମୂଲ୍ୟ ତୁଳନାରେ ସାମାଜିକ-ଅର୍ଥନୈତିକ ସ୍ଥିତି ଆକଳିତ ସ୍କୋରକୁ ବୃଦ୍ଧି କରେ। [needs native review]"
        },
        "lowers": {
            "key": "risk.ses.lowers",
            "en": "In this demo model, socioeconomic status lowers predicted score relative to typical training-data values.",
            "or": "ଏହି ଡେମୋ ମଡେଲରେ, ସାଧାରଣ ତାଲିମ ମୂଲ୍ୟ ତୁଳନାରେ ସାମାଜିକ-ଅର୍ଥନୈତିକ ସ୍ଥିତି ଆକଳିତ ସ୍କୋରକୁ ହ୍ରାସ କରେ। [needs native review]"
        }
    },
    "Sex": {
        "raises": {
            "key": "risk.sex.raises",
            "en": "In this demo model, sex demographic baseline raises predicted score relative to typical training-data values.",
            "or": "ଏହି ଡେମୋ ମଡେଲରେ, ଲିଙ୍ଗ ଜନସଂଖ୍ୟାଗତ ଆଧାର ଆକଳିତ ସ୍କୋରକୁ ବୃଦ୍ଧି କରେ। [needs native review]"
        },
        "lowers": {
            "key": "risk.sex.lowers",
            "en": "In this demo model, sex demographic baseline lowers predicted score relative to typical training-data values.",
            "or": "ଏହି ଡେମୋ ମଡେଲରେ, ଲିଙ୍ଗ ଜନସଂଖ୍ୟାଗତ ଆଧାର ଆକଳିତ ସ୍କୋରକୁ ହ୍ରାସ କରେ। [needs native review]"
        }
    },
    "MMSE": {
        "raises": {
            "key": "risk.mmse.raises",
            "en": "In this demo model, mental examination score raises predicted score relative to typical training-data values.",
            "or": "ଏହି ଡେମୋ ମଡେଲରେ, ମାନସିକ ପରୀକ୍ଷା ସ୍କୋର ଆକଳିତ ସ୍କୋରକୁ ବୃଦ୍ଧି କରେ। [needs native review]"
        },
        "lowers": {
            "key": "risk.mmse.lowers",
            "en": "In this demo model, mental examination score lowers predicted score relative to typical training-data values.",
            "or": "ଏହି ଡେମୋ ମଡେଲରେ, ମାନସିକ ପରୀକ୍ଷା ସ୍କୋର ଆକଳିତ ସ୍କୋରକୁ ହ୍ରାସ କରେ। [needs native review]"
        }
    }
}


def explain_one(
    profile: Dict[str, Any],
    pipeline,
    reference_medians: Dict[str, Any],
    feature_names: List[str]
) -> List[Dict[str, Any]]:
    """Generate dependency-free, lightweight feature contributions for a single profile."""
    row_df = pd.DataFrame([profile])
    baseline_p = float(pipeline.predict_proba(row_df)[0, 1])

    explanations = []
    for feat in feature_names:
        if feat not in profile:
            continue

        ref_val = reference_medians.get(feat, None)
        if ref_val is None:
            continue

        occluded_profile = profile.copy()
        occluded_profile[feat] = ref_val
        occluded_df = pd.DataFrame([occluded_profile])
        occluded_p = float(pipeline.predict_proba(occluded_df)[0, 1])

        delta = baseline_p - occluded_p
        effect = "raises" if delta > 0.001 else ("lowers" if delta < -0.001 else "neutral")
        magnitude = round(float(abs(delta)), 4)

        text_entry = FEATURE_TEXTS.get(feat, {}).get(effect, {})
        text_key = text_entry.get("key", f"risk.{feat.lower()}.{effect}")
        text_en = text_entry.get("en", f"{feat} has a {effect} effect on estimated risk.")
        text_or = text_entry.get("or", f"{feat} ପ୍ରଭାବ [needs native review]")

        explanations.append({
            "feature": feat,
            "value": profile[feat],
            "effect": effect,
            "magnitude": magnitude,
            "text_key": text_key,
            "text_en": text_en,
            "text_or": text_or
        })

    explanations.sort(key=lambda x: x["magnitude"], reverse=True)
    return explanations
