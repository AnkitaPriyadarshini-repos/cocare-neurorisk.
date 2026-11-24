# Feature Inventory: Cognitive Risk Screening

This inventory defines the feature catalog for both OASIS and LASI-DAD harmonization, distinguishing between self-reportable demographic/lifestyle variables and objective cognitive performance metrics (MMSE / HMSE).

## Screening Principles
1. **Self-Reportable vs Test-Based**:
   - The **"without MMSE"** screening model relies exclusively on self-reportable, non-test variables (Age, Sex, Education, Socioeconomic Status) that an older adult or caregiver can provide in a quick web profile without requiring clinical test administration.
   - The **"with MMSE"** screening model augments these with the total score from the Mini-Mental State Examination (MMSE) / Hindi Mental State Examination (HMSE).
2. **Clinical Exclusions**:
   - High-cost MRI volumetrics (`eTIV`, `nWBV`, `ASF`) are excluded from community screening tools because they require clinical neuroimaging and cannot be gathered in a community screening form.
   - Clinical Dementia Rating (`CDR`) is the ground-truth clinical diagnostic anchor and is never used as an input feature.

| Variable | Description | Type | Allowed Values / Units | % Missing (OASIS) | Self-Reportable? | Cognitive Test Item? | Include / Exclude & Reason |
|---|---|---|---|---|---|---|---|
| `Age` | Participant chronological age | Numeric | 40 - 120 years | 0.0% | Yes (Caregiver/Self) | No | **Include (Both)**: Major demographic risk factor for neurodegeneration. |
| `Sex` | Biological sex (`M`/`F`) | Categorical | `M`, `F` | 0.0% | Yes (Caregiver/Self) | No | **Include (Both)**: Key demographic stratification feature. |
| `EDUC` | Years of formal education | Numeric | 0 - 30 years | 0.0% | Yes (Caregiver/Self) | No | **Include (Both)**: Major proxy for cognitive reserve; vital in rural/suburban contexts. |
| `SES` | Socioeconomic Status scale | Numeric / Ordinal | 1 (highest) to 5 (lowest) | ~5.1% | Yes (Caregiver/Self) | No | **Include (Both)**: Social determinant of health, imputed via median/mode. |
| `MMSE` | Mini-Mental State Exam score | Numeric | 0 - 30 points | ~0.5% | No (requires test protocol) | Yes (Total Score) | **Include (With MMSE only)**: Highly predictive cognitive screening test item; excluded from "without" model. |
| `CDR` | Clinical Dementia Rating | Numeric | 0.0, 0.5, 1.0, 2.0 | 0.0% | No | Clinical rating | **Exclude**: Ground-truth target label; inclusion would constitute direct target leakage. |
| `eTIV` | Estimated Total Intracranial Volume | Numeric | 1000 - 2500 cm³ | 0.0% | No | No (MRI imaging) | **Exclude**: Requires hospital MRI scanner; unusable for web screening. |
| `nWBV` | Normalized Whole Brain Volume | Numeric | 0.6 - 0.9 ratio | 0.0% | No | No (MRI imaging) | **Exclude**: Requires hospital MRI scanner; unusable for web screening. |
| `ASF` | Atlas Scaling Factor | Numeric | 0.8 - 1.6 unitless | 0.0% | No | No (MRI imaging) | **Exclude**: Requires hospital MRI scanner; unusable for web screening. |
| `Visit` | Longitudinal visit number | Integer | 1, 2, 3... | 0.0% | No | No (Study metadata) | **Exclude**: Study artifact, not a clinical risk factor. |
| `MR Delay`| Time elapsed between visits | Integer | Days | 0.0% | No | No (Study metadata) | **Exclude**: Study artifact, not a clinical risk factor. |
| `Hand` | Handedness | Categorical | `R` (Right) | 0.0% | Yes | No | **Exclude**: Invariant in dataset (100% Right-handed), zero predictive power. |
