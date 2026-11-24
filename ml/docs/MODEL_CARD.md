# Model Card: Cognitive Risk Screening Models (`with_mmse` & `without_mmse`)

## 1. Model Details
- **Developer**: CO CARE Machine Learning Team (Part A: ML & Data Owner).
- **Model Date**: November 2026.
- **Model Version**: 1.0.0.
- **Model Type**: Regularized Logistic Regression with class-balanced weighting (`class_weight='balanced'`) wrapped in an end-to-end `scikit-learn` Pipeline with median/mode imputation, standard scaling, and one-hot encoding.
- **Artifacts**:
  - `model_with_mmse.joblib` + `model_with_mmse_metadata.json` (Includes Age, Sex, Education, SES, MMSE)
  - `model_without_mmse.joblib` + `model_without_mmse_metadata.json` (Includes Age, Sex, Education, SES strictly; no cognitive test items)
- **License**: MIT / Non-commercial academic research.

## 2. Intended Use
- **Primary Intended Use**: A rapid, community-accessible preliminary screening aid to identify elderly individuals who may be at elevated risk of cognitive impairment or dementia and would benefit from comprehensive clinical evaluation.
- **Primary Users**: Community health workers, caregivers, and older adults participating in elder-care programs.
- **Deployment**: Exposed via lightweight FastAPI endpoints (`/api/risk/predict`, `/api/risk/model-info`, `/api/risk/form-spec`) and deployed locally as well as on Vercel Serverless.

## 3. Out-of-Scope and Prohibited Uses
- **NOT A DIAGNOSIS**: This tool is **strictly a screening aid**, NOT a medical diagnostic instrument. It cannot establish a diagnosis of Alzheimer's disease, vascular dementia, Lewy body dementia, or any neurodegenerative condition.
- **Clinical Decision Making**: Must not be used as the sole basis for clinical treatment, pharmaceutical prescription, institutionalization, or legal competency determinations.
- **Autonomous Action**: Predictions must always be presented alongside appropriate disclaimers and recommend follow-up with qualified geriatricians or neurologists.

## 4. Training and Test Data
- **Practice Dataset**: OASIS-2 Longitudinal Dementia Cohort (373 sessions across 150 unique subjects aged 60–98).
- **Target Definition**: Binary cognitive risk status ($Y=1$ for Clinical Dementia Rating $\text{CDR} > 0$ or Demented group; $Y=0$ for $\text{CDR} = 0$ / Nondemented).
- **Data Splitting**: Stratified Group 5-fold split by participant ID (`Subject ID`). Zero participant overlap between train ($N=301$, 121 subjects) and held-out test ($N=72$, 29 subjects) ensures complete isolation and no longitudinal leakage.

## 5. Performance Metrics (Held-Out Test Set, N=72)

### Variant A: `model_with_mmse`
*Optimized for clinical sensitivity ($\ge 0.85$ target threshold = 0.316)*

| Metric | Point Estimate | Bootstrap 95% CI |
|---|---|---|
| **Sensitivity (Recall)** | **90.5%** (19/21) | [76.2%, 100.0%] |
| **Specificity** | **74.5%** (38/51) | [62.3%, 86.5%] |
| **Precision** | **59.4%** (19/32) | [41.2%, 76.7%] |
| **F1 Score** | **0.717** | [0.560, 0.849] |
| **ROC-AUC** | **0.929** | [0.858, 0.985] |
| **PR-AUC** | **0.891** | [0.770, 0.971] |
| **Accuracy** | **79.2%** | [69.4%, 88.9%] |
| **Brier Score** | **0.102** | - |
| **Confusion Matrix** | TP=19, FP=13, TN=38, FN=2 | False Negatives = 2 |

### Variant B: `model_without_mmse`
*Self-reportable demographic features only (Age, Sex, Education, SES; threshold = 0.330)*

| Metric | Point Estimate | Bootstrap 95% CI |
|---|---|---|
| **Sensitivity (Recall)** | **90.5%** (19/21) | [75.0%, 100.0%] |
| **Specificity** | **35.3%** (18/51) | [22.9%, 48.2%] |
| **Precision** | **36.5%** (19/52) | [24.0%, 50.0%] |
| **F1 Score** | **0.521** | [0.373, 0.652] |
| **ROC-AUC** | **0.679** | [0.526, 0.809] |
| **PR-AUC** | **0.549** | [0.350, 0.728] |
| **Accuracy** | **51.4%** | [38.9%, 62.5%] |
| **Brier Score** | **0.210** | - |
| **Confusion Matrix** | TP=19, FP=33, TN=18, FN=2 | False Negatives = 2 |

## 6. Subgroup Fairness & Disparity Analysis
Subgroup parity was audited across Sex ($M$ vs $F$), Age bands ($<75$ vs $\ge 75$), and Education levels ($\le 12$ years vs $>12$ years).
- For `model_with_mmse`, sensitivity across sexes was $90.9\%$ (Male) vs $90.0\%$ (Female), a gap of $<1\%$, well within the 5% parity bound.
- In `model_without_mmse`, lower education ($\le 12$ years) had slightly elevated baseline false positive rates, reflecting that education is a proxy for cognitive reserve and socioeconomic protection.

## 7. Contextual Differences in Odia / Rural Elderly Populations
When transitioning from the Western OASIS cohort to rural/semi-urban Indian cohorts (LASI-DAD):
1. **Educational Distribution**: Western cohorts skew towards higher formal education ($>12$ years). In Odisha and rural India, many elderly individuals have $\le 5$ years or informal schooling. Standard MMSE cutoffs unfairly penalize illiterate or low-literacy elders.
2. **Harmonized Cognitive Tests**: The Hindi Mental State Examination (HMSE) or adapted Odia cognitive batteries replace literacy-dependent tasks (spelling 'WORLD' backward, writing sentences) with culturally relevant serial operations (number counting, market transactions).
3. **Socioeconomic Stratification**: Joint family living arrangements and caregiver proxy reporting play a more substantial role in India than self-reporting alone.

## 8. Explainability Mechanism
- **Runtime Explanations**: Uses dependency-free feature occlusion against training reference medians:
  $$\Delta = P(\text{profile}) - P(\text{profile with feature occluded})$$
- Returns human-interpretable cards with English and native Odia placeholders (flagged for native speaker review) indicating whether each factor raises or lowers estimated risk.
