# Machine Learning Audit: Leakage, Labels, and Validation

## 1. Repeated Measures & Participant Grouping Audit
- **Dataset**: OASIS Longitudinal Dataset (373 records across 150 unique participants, mean 2.49 visits per subject, range 2–5).
- **Leakage Risk**: Because each participant contributes multiple visits over time, naive random splitting (e.g. `KFold` or `train_test_split`) allows different visits of the same participant to appear simultaneously in both training and test sets. Since cognitive status is autocorrelated, this causes severe data leakage and artificially inflates performance.
- **Enforcement**:
  - The split is executed using `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` grouped strictly on `Subject ID`.
  - **Verification**: `set(train_subjects).intersection(set(test_subjects)) == 0` (0 participant overlap verified).
- **Impact of Grouping**:
  - **With MMSE variant**:
    - Ungrouped 5-Fold CV ROC-AUC: **0.8972** (std: 0.0298)
    - Grouped 5-Fold CV ROC-AUC: **0.8841** (std: 0.0372)
    - AUC Delta: **+0.0132**
  - **Without MMSE variant**:
    - Ungrouped 5-Fold CV ROC-AUC: **0.6980** (std: 0.0482)
    - Grouped 5-Fold CV ROC-AUC: **0.6456** (std: 0.0656)
    - AUC Delta: **+0.0524**
  - *Finding*: Ungrouped evaluation artificially overestimates discriminative ability. Grouped validation provides honest generalization metrics for unseen participants.

## 2. Target Label Definition & Leakage Prevention
- **Source Attribute**: Clinical Dementia Rating (`CDR`).
- **Classification Criterion**:
  - Positive Class (`target = 1`): `CDR > 0` (CDR 0.5 = very mild impairment, CDR 1.0 = mild dementia, CDR 2.0 = moderate dementia).
  - Negative Class (`target = 0`): `CDR == 0` (Cognitively normal / nondemented).
- **Handling of Converted Participants**:
  - In OASIS, participants who convert from normal to impaired over successive visits have their baseline visits (`CDR == 0`) labeled 0 and conversion visits (`CDR > 0`) labeled 1. Because splits are grouped by subject, all visits for a converted subject reside in either the train set or test set, preventing temporal leakage.
- **Feature Independence Verification**:
  - `CDR` is strictly excluded from all model feature spaces.
  - The feature space for `model_without_mmse` contains solely self-reportable attributes: `Age`, `Sex`, `EDUC`, `SES`.
  - The feature space for `model_with_mmse` adds only the administered cognitive score `MMSE`. No diagnostic or clinical classification features are used as inputs.

## 3. Threshold Selection Path
- The decision threshold is **never tuned on the test set**.
- **Code Path**: In `ml/src/train.py` (lines 164–181) and `ml/src/evaluate.py`:
  1. Out-of-fold cross-validated probability predictions (`oof_probs`) are computed using `StratifiedGroupKFold(groups=groups_train)` across training folds only.
  2. `find_optimal_threshold()` evaluates candidate thresholds on `y_train` vs. `oof_probs` to select the threshold meeting the target sensitivity (e.g. >= 0.85) or maximizing Youden's $J$.
  3. The held-out test set is evaluated exactly once at this pre-fixed threshold.

## 4. Preprocessing Fit-on-Train Verification
- All median imputers, standardizers (`StandardScaler`), and categorical encoders are contained inside a scikit-learn `Pipeline` and fitted exclusively on `X_train`.
- Imputer statistics match training medians (`Age`=77.0, `EDUC`=15.0, `SES`=2.0, `MMSE`=29.0) and scaler means match training means (`Age`=76.52, `EDUC`=14.60, `SES`=2.44, `MMSE`=27.27).

## 5. Label Permutation Sanity Check
- When training and evaluating with randomly shuffled labels over 10 seeds, model discrimination drops to random chance:
  - `model_with_mmse` Permutation CV ROC-AUC: **0.4956 ± 0.0785**
  - `model_without_mmse` Permutation CV ROC-AUC: **0.4700 ± 0.0640**
- This confirms that genuine signal rather than structural artifacts or data leakage drives model performance.

## 6. Baseline Models Comparison
- **Majority Class Baseline** (`DummyClassifier(strategy='most_frequent')`):
  - Accuracy: **55.4%** | ROC-AUC: **0.5000**
- **Age-Only Logistic Regression**:
  - CV ROC-AUC: **0.4341 ± 0.0627**
  - CV Accuracy: **43.9%**
