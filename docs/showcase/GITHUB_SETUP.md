# GitHub Repository Showcase Configuration

Guidelines and recommended metadata for presenting the **CO CARE** machine learning showcase to an engineering, research, and technical recruiter audience.

---

## 1. Suggested Repository Topics (Tags)
Add these topics in the GitHub repository settings (under the **About** gear icon on the main repo page):

```
dementia-screening, cognitive-health, machine-learning, scikit-learn, fastapi, shap, responsible-ai, stateless-privacy, healthcare-ai, oasis-dataset, serverless, lasi-dad-planned
```

---

## 2. Recommended Repository Description
Enter this concise, impact-oriented summary in the repository's **Description** field:

> **AI-assisted cognitive risk screening pipeline and culturally adapted cognitive games for elderly populations. Features subject-grouped cross-validation, stateless serverless inference, and Odia-ready (translations pending native review) feature attribution.**

---

## 3. Recommended Website URL
Set the repository **Website** URL to either the live Vercel application or the interactive showcase page:
```
https://cocare-zeta.vercel.app
```

---

## 4. Key Architectural Highlights for Technical Reviewers
When discussing this repository with engineers and hiring teams, highlight these core engineering decisions:
1. **Zero Data Leakage by Design**: Longitudinal cohorts with repeated measures (OASIS has ~2.5 visits/subject) are strictly partitioned using `GroupShuffleSplit` and `StratifiedGroupKFold`. Naive random splitting falsely inflated AUC by `+0.052`.
2. **Permutation Test Sanity Check**: Shuffled labels collapsed CV AUC to `0.496 ± 0.078` for `model_with_mmse` and `0.470 ± 0.064` for `model_without_mmse`, proving that preprocessing and imputation did not leak target structure.
3. **Stateless Privacy Guarantee**: No participant profile vector is ever written to disk, SQLite, or application logs. Inference runs in-memory and data is discarded upon HTTP response delivery.
4. **Serverless Footprint Optimization**: Heavy scientific packages (`shap`, `seaborn`) are isolated to training; serverless inference uses lightweight linear weights and exact feature occlusion sensitivity (model inference ~1 ms (local, warm), zero C++ binary dependencies in Lambda).
5. **LASI-DAD Adapter & Retrain Quality Gates**: The pipeline is dataset-agnostic; changing from OASIS demo to Indian LASI-DAD requires only editing `ml/config/lasi_dad_mapping.yaml` and running `make retrain DATASET=lasi_dad` which enforces 3 automated quality gates before artifact deployment.
