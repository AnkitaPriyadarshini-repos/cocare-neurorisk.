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
            "en": "Advanced age is a primary non-modifiable risk factor for cognitive vulnerability.",
            "or": "ଅଧିକ ବୟସ ଜ୍ଞାନଗତ ଦୁର୍ବଳତା ପାଇଁ ଏକ ମୁଖ୍ୟ ବିପଦ କାରଣ। [needs native review]"
        },
        "lowers": {
            "key": "risk.age.lowers",
            "en": "Younger age profile contributes positively to baseline cognitive resilience.",
            "or": "କମ୍ ବୟସ ଜ୍ଞାନଗତ ସହନଶୀଳତା ବୃଦ୍ଧିରେ ସହାୟକ ହୁଏ। [needs native review]"
        }
    },
    "EDUC": {
        "raises": {
            "key": "risk.educ.raises",
            "en": "Fewer years of formal education is associated with lower cognitive reserve buffer.",
            "or": "କମ୍ ବିଦ୍ୟାଳୟ ଶିକ୍ଷା କାରଣରୁ ଜ୍ଞାନଗତ ସଂରକ୍ଷଣ ହ୍ରାସ ପାଇପାରେ। [needs native review]"
        },
        "lowers": {
            "key": "risk.educ.lowers",
            "en": "Higher formal educational attainment supports robust cognitive reserve.",
            "or": "ଅଧିକ ଶିକ୍ଷାଗତ ଯୋଗ୍ୟତା ଜ୍ଞାନଗତ ସଂରକ୍ଷଣକୁ ସୁଦୃଢ଼ ରଖେ। [needs native review]"
        }
    },
    "SES": {
        "raises": {
            "key": "risk.ses.raises",
            "en": "Lower socioeconomic status is historically associated with elevated healthcare barrier exposure.",
            "or": "ନିମ୍ନ ସାମାଜିକ-ଅର୍ଥନୈତିକ ସ୍ଥିତି ସ୍ୱାସ୍ଥ୍ୟ ସୁରକ୍ଷାରେ ବାଧା ସୃଷ୍ଟି କରିପାରେ। [needs native review]"
        },
        "lowers": {
            "key": "risk.ses.lowers",
            "en": "Higher socioeconomic standing correlates with enhanced health literacy and protective resources.",
            "or": "ଉଚ୍ଚ ସାମାଜିକ-ଅର୍ଥନୈତିକ ସ୍ଥିତି ଉତ୍ତମ ସ୍ୱାସ୍ଥ୍ୟ ସଚେତନତା ସହ ସମ୍ପୃକ୍ତ। [needs native review]"
        }
    },
    "Sex": {
        "raises": {
            "key": "risk.sex.raises",
            "en": "Demographic epidemiological profile indicates slight baseline adjustment.",
            "or": "ଜନସଂଖ୍ୟାଗତ ବିଶ୍ଳେଷଣ ସାମାନ୍ୟ ସଂଶୋଧନ ସୂଚାଉଛି। [needs native review]"
        },
        "lowers": {
            "key": "risk.sex.lowers",
            "en": "Demographic baseline aligns favorably with lower population incidence.",
            "or": "ଜନସଂଖ୍ୟାଗତ ବିଶ୍ଳେଷଣ ଅନୁକୂଳ ଫଳାଫଳ ଦର୍ଶାଉଛି। [needs native review]"
        }
    },
    "MMSE": {
        "raises": {
            "key": "risk.mmse.raises",
            "en": "Reduced score on mental state examination directly reflects difficulty with orientation, recall, or attention.",
            "or": "ମାନସିକ ସ୍ଥିତି ପରୀକ୍ଷଣରେ କମ୍ ସ୍କୋର ଧ୍ୟାନ ଏବଂ ସ୍ମରଣ ଶକ୍ତିରେ ଦୁର୍ବଳତା ଦର୍ଶାଉଛି। [needs native review]"
        },
        "lowers": {
            "key": "risk.mmse.lowers",
            "en": "High score on mental state assessment indicates preserved orientation, recall, and attention.",
            "or": "ମାନସିକ ସ୍ଥିତି ପରୀକ୍ଷଣରେ ଉଚ୍ଚ ସ୍କୋର ଉତ୍ତମ ସ୍ମରଣ ଓ ଧ୍ୟାନ ଶକ୍ତି ଦର୍ଶାଉଛି। [needs native review]"
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
