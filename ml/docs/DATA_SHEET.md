# Data Sheet: Cognitive Risk Screening Cohorts

## 1. Motivation
- **Purpose**: To train, validate, and benchmark screening models for early cognitive risk detection that can be administered in web interfaces and community elderly-care environments.
- **Creator**: Washington University Alzheimer's Disease Research Center (OASIS Project) & Gateway to Global Aging Data / IIPS (LASI-DAD).

## 2. Composition
- **Cohort Instances**:
  - **OASIS-2**: 373 MRI sessions from 150 participants aged 60–98 (mean 2.49 visits per subject, range 2–5). 72 participants remained nondemented, 64 were demented at initial visit, and 14 converted during longitudinal follow-up.
  - **LASI-DAD Roadmap**: In-depth diagnostic assessment of dementia sub-study nested within the Longitudinal Aging Study in India (harmonized with Health and Retirement Study).
- **Target Label Definition & Ground Truth**:
  - Binary target is derived from the Clinical Dementia Rating (`CDR`):
    - `0` (Cognitively Normal / Nondemented): `CDR == 0.0`.
    - `1` (Cognitively Impaired / At Risk): `CDR > 0.0` (0.5 = very mild impairment, 1.0 = mild dementia, 2.0 = moderate dementia).
    - If `CDR` is missing, fallback uses `Group == 'Demented'`.
  - **Handling of Converted Participants**: Participants who convert from normal to impaired over successive visits have their baseline visits (`CDR == 0`) labeled 0 and conversion visits (`CDR > 0`) labeled 1. Under `StratifiedGroupKFold(groups=Subject ID)`, all visits for any given participant are assigned to either the train split or the test split, completely preventing temporal leakage.
  - **Label Independence Guarantee**: `CDR` is strictly excluded from all model feature spaces. No model feature is derived from the diagnostic label.
- **Features Captured**:
  - Demographics: Age, Biological Sex, Years of Education (EDUC), Socioeconomic Status (SES).
  - Cognitive Assessments: Mini-Mental State Examination (MMSE) / Hindi Mental State Examination (HMSE).
  - Diagnostic Anchor: Clinical Dementia Rating (CDR 0.0, 0.5, 1.0, 2.0; excluded from inputs).

## 3. Collection Process
- **OASIS**: Recruited via the Washington University ADRC; each participant completed clinical dementia rating interviews, psychometric evaluations, and MRI scans under informed consent.
- **Data Hygiene**:
  - Missingness: SES has 5.1% missing records; MMSE has 0.5% missing records.
  - Imputation: Imputed strictly within `scikit-learn` ColumnTransformer using training fold medians/modes.
  - Participant Isolation: Longitudinal records clustered by `Subject ID` to prevent data leakage.

## 4. Preprocessing & Quality Checks
1. Sentinel codes (`-1`, `999`, `None`, `Unknown`) recoded to standard `NaN`.
2. Outlier boundaries clipped to biological reality: Age $\in [40, 120]$, EDUC $\in [0, 30]$, SES $\in [1, 5]$, MMSE $\in [0, 30]$.
3. De-duplication and dtype standardization applied.

## 5. Uses and Distribution
- **Raw Data Privacy**: Raw participant-level data is strictly excluded from version control via `.gitignore`.
- **Committed Artifacts**: Only aggregate distributions, synthetic background profiles, and pre-fitted `.joblib` estimators are checked into version control.
