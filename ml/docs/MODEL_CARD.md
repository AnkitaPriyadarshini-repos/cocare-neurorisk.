# Model Card: Cognitive Risk Screening Models (`with_mmse` & `without_mmse`)

## 1. Model Details
- **Developer**: CO CARE Machine Learning Team (Part A: ML & Data Owner).
- **Model Date**: November 2026.
- **Model Version**: 1.1.0-validation.
- **Model Status**: `demo_oasis_not_validated_for_lasi_dad` (DEMO ONLY: Practised on OASIS; NOT validated for Indian/Odia populations).
- **Model Type**: Regularized Logistic Regression with class-balanced weighting (`class_weight='balanced'`) wrapped in an end-to-end `scikit-learn` Pipeline with median/mode imputation, standard scaling, and one-hot encoding.
- **Artifacts**:
  - `model_with_mmse.joblib` + `model_with_mmse_metadata.json` (Features: Age, Sex, Education, SES, MMSE)
  - `model_without_mmse.joblib` + `model_without_mmse_metadata.json` (Features: Age, Sex, Education, SES strictly; zero cognitive test items)
- **License**: MIT / Academic research demo.

## 2. Intended Use
- **Demonstration Architecture**: Designed to prototype and validate the end-to-end integration of machine learning cognitive screening pipelines, form schemas, localized feature explanations, and serverless deployment in CO CARE.
- **Screening Aid Only**: When validated on appropriate population data (LASI-DAD), intended as a preliminary triage aid for community health workers and caregivers to identify individuals who should receive thorough neurological and neuropsychological assessment.

## 3. Out-of-Scope, Prohibited Uses, and Critical Limitations
- **NOT A DIAGNOSIS**: This tool is **strictly a screening aid**, NOT a medical diagnostic instrument. It cannot diagnose Alzheimer's disease, vascular dementia, Lewy body dementia, or any specific neurological condition.
- **NOT VALIDATED ON INDIAN / ODIA POPULATIONS**: These demo models were trained solely on the OASIS cohort (a US clinical cohort). They have **NOT** been calibrated or validated on LASI-DAD or rural/semi-urban Indian elders. **DO NOT USE FOR CLINICAL OR REAL-WORLD SCREENING OF PATIENTS.**
- **Population Shift**: Educational attainment, language, and cultural background differ radically between US cohorts and elderly Odia speakers. Applying US-derived thresholds directly to Indian cohorts introduces severe diagnostic bias.
- **Small Sample Size**: The OASIS longitudinal cohort contains only 373 total sessions across 150 individuals. Held-out test performance is based on 72 records (21 positives, 51 negatives).
- **Cognitive Score Dependence**: In `model_with_mmse`, model discrimination is overwhelmingly driven by the MMSE score. In `model_without_mmse`, relying purely on 4 demographic features achieves high sensitivity (90.5%) only at the cost of very low specificity (35.3%, 33 false positives out of 51 negatives).

## 4. Training and Test Data
- **Practice Dataset**: OASIS-2 Longitudinal Dementia Cohort (373 sessions across 150 unique subjects aged 60–98).
- **Target Definition**: Binary cognitive risk status ($Y=1$ for Clinical Dementia Rating $\text{CDR} > 0$ or Demented group; $Y=0$ for $\text{CDR} = 0$ / Nondemented).
- **Data Splitting**: Stratified Group 5-fold split by participant ID (`Subject ID`). Zero participant overlap between train ($N=301$, 121 subjects) and held-out test ($N=72$, 29 subjects) ensures complete isolation and no longitudinal leakage.

## 5. Performance Metrics and Validation

Because the single held-out test set is small ($N=72$), **repeated cross-validation across all participants (5 repeats of 5-fold Stratified Group K-Fold = 25 evaluations)** provides the **primary performance estimate**, while the single held-out split ($N=72$, 29 participants strictly isolated) serves as a secondary out-of-sample check.

### Primary Estimate: 5x Repeated 5-Fold Stratified Group CV (25 Evaluations)

| Metric | `model_with_mmse` (Mean ± Std) | `model_without_mmse` (Mean ± Std) | Baseline: Age-Only LR | Baseline: Majority Class |
|---|---|---|---|---|
| **ROC-AUC** | **0.892 ± 0.041** | **0.654 ± 0.062** | 0.434 ± 0.063 | 0.500 |
| **PR-AUC** | **0.890 ± 0.044** | **0.551 ± 0.082** | 0.448 ± 0.065 | 0.448 |
| **Sensitivity** | **72.9% ± 9.1%** | **61.2% ± 13.3%** | 43.9% ± 8.2% | 0.0% |
| **Specificity** | **85.9% ± 7.8%** | **63.2% ± 13.3%** | 43.9% ± 8.2% | 100.0% |
| **Precision** | **81.0% ± 9.8%** | **58.1% ± 9.9%** | 44.8% ± 6.5% | 0.0% |
| **NPV** | **79.7% ± 7.0%** | **66.4% ± 10.1%** | 55.2% ± 5.0% | 55.2% |
| **F1 Score** | **0.761 ± 0.068** | **0.582 ± 0.095** | 0.440 ± 0.068 | 0.000 |
| **Accuracy** | **80.0% ± 5.3%** | **62.3% ± 8.7%** | 43.9% ± 6.3% | 55.4% |
| **Brier Score** | **0.134 ± 0.026** | **0.219 ± 0.021** | 0.252 ± 0.015 | 0.248 |

### Secondary Estimate: Single Held-Out Test Set (N=72, 21 Positives, 51 Negatives, Bootstrap 2,000 Resamples)

| Metric | `model_with_mmse` Point Estimate [95% CI] | `model_without_mmse` Point Estimate [95% CI] |
|---|---|---|
| **Sensitivity (Recall)** | **90.5%** (19/21) [75.0%, 100.0%] | **90.5%** (19/21) [75.0%, 100.0%] |
| **Specificity** | **74.5%** (38/51) [62.3%, 86.5%] | **35.3%** (18/51) [22.7%, 47.9%] |
| **Precision (PPV)** | **59.4%** (19/32) [41.4%, 76.5%] | **36.5%** (19/52) [24.0%, 50.0%] |
| **NPV** | **95.0%** (38/40) [87.0%, 100.0%] | **90.0%** (18/20) [75.0%, 100.0%] |
| **F1 Score** | **0.717** [0.558, 0.844] | **0.521** [0.373, 0.651] |
| **Accuracy** | **79.2%** [69.4%, 88.9%] | **51.4%** [38.9%, 62.5%] |
| **ROC-AUC** | **0.929** [0.847, 0.986] | **0.679** [0.538, 0.811] |
| **PR-AUC** | **0.891** [0.765, 0.972] | **0.549** [0.347, 0.728] |
| **Brier Score** | **0.102** [0.063, 0.149] | **0.210** [0.173, 0.250] |
| **Confusion Matrix** | TP=19, FP=13, TN=38, FN=2 | TP=19, FP=33, TN=18, FN=2 |

### Operating Points and Clinical Trade-offs

| Target Sensitivity | Variant | Threshold | Sensitivity | Specificity | Precision | NPV | Clinical Trade-off (False Negatives vs False Positives) |
|---|---|---|---|---|---|---|---|
| **Sens $\ge 0.80$** | With MMSE | 0.3439 | 80.1% | 68.4% | 70.5% | 78.5% | Misses 29/146 impaired cases; 49 false alarms. |
| **Sens $\ge 0.85$** | With MMSE | 0.3203 | 85.6% | 63.2% | 68.7% | 82.4% | Primary screening threshold: misses 21 cases; 57 false alarms. |
| **Sens $\ge 0.90$** | With MMSE | 0.2861 | 90.4% | 56.1% | 65.7% | 86.8% | High sensitivity: misses only 14 cases; 68 false alarms. |
| **Sens $\ge 0.80$** | Without MMSE | 0.3753 | 80.1% | 37.4% | 54.7% | 66.7% | Demographics only: misses 29/146 cases; 97 false alarms. |
| **Sens $\ge 0.85$** | Without MMSE | 0.3301 | 85.6% | 33.5% | 54.8% | 71.2% | High community recall: misses 21 cases; 103 false alarms. |
| **Sens $\ge 0.90$** | Without MMSE | 0.3105 | 91.1% | 31.0% | 55.4% | 78.7% | Misses only 13 cases; 107 false alarms (low specificity). |

## 6. Subgroup Fairness & Disparity Analysis
Subgroup parity was audited on the held-out test set across Sex, Age bands, and Education levels:

| Subgroup | Category | $N$ | Positives | Prevalence | Sensitivity (With MMSE) | Sensitivity (Without MMSE) | Parity Notes |
|---|---|---|---|---|---|---|---|
| **Sex** | Male | 21 | 11 | 52.4% | 90.9% | 100.0% | Sensitivity gap between sexes is <1% with MMSE. |
| **Sex** | Female | 51 | 10 | 19.6% | 90.0% | 80.0% | Female cohort has lower prevalence in test split. |
| **Age** | $<75$ years | 26 | 9 | 34.6% | 88.9% | 88.9% | Sensitivity gap is <3% across age bands. |
| **Age** | $\ge 75$ years | 46 | 12 | 26.1% | 91.7% | 91.7% | Well-calibrated across age boundaries. |
| **Education** | $\le 12$ years | 19 | 10 | 52.6% | 100.0% | 100.0% | **Underpowered subgroup** ($N=19$); higher false positive rate. |
| **Education** | $>12$ years | 53 | 11 | 20.8% | 81.8% | 81.8% | Disparity flag (gap > 5 points): educational cognitive reserve effect. |

> **Underpowered Group Warning**: Subgroups with $N < 30$ (e.g. Male $N=21$, $\le 12$ years education $N=19$) must not be over-interpreted. True population parity must be assessed on LASI-DAD once access is granted.

## 7. Contextual Differences in Odia / Rural Elderly Populations
When transitioning from the Western OASIS cohort to rural/semi-urban Indian cohorts (LASI-DAD):
1. **Educational Distribution**: Western cohorts skew towards higher formal education ($>12$ years). In Odisha and rural India, many elderly individuals have $\le 5$ years or informal schooling. Standard MMSE cutoffs unfairly penalize illiterate or low-literacy elders.
2. **Harmonized Cognitive Tests**: The Hindi Mental State Examination (HMSE) or adapted Odia cognitive batteries replace literacy-dependent tasks (spelling 'WORLD' backward, writing sentences) with culturally relevant serial operations (number counting, market transactions).
3. **Socioeconomic Stratification**: Joint family living arrangements and caregiver proxy reporting play a more substantial role in India than self-reporting alone.

## 8. Explainability Mechanism
- **Runtime Explanations**: Uses dependency-free feature occlusion against training reference medians:
  $$\Delta = P(\text{profile}) - P(\text{profile with feature occluded})$$
- Returns human-interpretable cards with English and native Odia placeholders (flagged for native speaker review) indicating whether each factor raises or lowers estimated risk.
