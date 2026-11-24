"""Explainability module for cognitive risk screening.

Includes:
1. Lightweight, dependency-free runtime explanation (explain_one) using feature occlusion / coefficient contribution.
2. Offline SHAP tooling for global feature importance and waterfall plots.
3. Stable localization dictionary with English text and Odia placeholders.
"""
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd


# Localization lookup for feature explanation strings
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
    """Generate dependency-free, lightweight feature contributions for a single profile.

    Uses feature occlusion: replaces each feature with its reference training median/mode
    and observes the delta in predicted probability:
      delta = P(profile) - P(profile_with_feature_occluded)
    If delta > 0, the feature 'raises' the risk. If delta < 0, it 'lowers' the risk.
    Magnitude is |delta|.

    Returns items sorted by descending magnitude.
    """
    # Prepare single-row DataFrame containing all expected features
    row_dict = {feat: profile.get(feat, np.nan) for feat in feature_names}
    df_single = pd.DataFrame([row_dict])
    # Baseline probability
    prob_base = float(pipeline.predict_proba(df_single)[0, 1])

    explanations = []

    for feat in feature_names:
        if feat not in profile or feat not in reference_medians:
            continue

        original_val = profile[feat]
        ref_val = reference_medians[feat]

        # Occlude feature with reference median/mode
        df_occluded = df_single.copy()
        df_occluded[feat] = ref_val

        prob_occluded = float(pipeline.predict_proba(df_occluded)[0, 1])
        delta = prob_base - prob_occluded
        effect = "raises" if delta >= 0 else "lowers"
        magnitude = round(abs(delta), 4)

        text_meta = FEATURE_TEXTS.get(feat, {}).get(effect, {
            "key": f"risk.{feat.lower()}.{effect}",
            "en": f"{feat} {effect} estimated cognitive risk.",
            "or": f"{feat} ଆକଳିତ ବିପଦକୁ {effect} କରେ। (needs native review)"
        })

        explanations.append({
            "feature": feat,
            "value": original_val,
            "effect": effect,
            "magnitude": magnitude,
            "text_key": text_meta["key"],
            "text_en": text_meta["en"],
            "text_or": text_meta["or"]
        })

    # Sort by magnitude descending
    explanations.sort(key=lambda x: x["magnitude"], reverse=True)
    return explanations
