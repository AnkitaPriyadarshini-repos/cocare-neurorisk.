"""Runtime explainability module for CO CARE serverless deployment.

Self-contained within backend/app so Vercel does not require ml/ to be deployed.
Uses lightweight feature occlusion with zero C++ or heavy dependencies (< 1.5 ms latency).
"""
from typing import Dict, List, Any
import numpy as np
import pandas as pd

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
