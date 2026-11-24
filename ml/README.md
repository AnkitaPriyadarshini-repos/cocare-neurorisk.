# Cognitive Risk Screening (ML Subsystem)

This folder contains the machine learning training pipeline, dataset adapters, explainability tooling, and artifacts for the CO CARE dementia risk screening model.

## Folder Layout
```
ml/
  config.yaml                  All paths, feature sets, seeds, and hyperparameters
  requirements.txt             Pinned training and evaluation dependencies
  Makefile                     Single-command targets for each workflow stage
  src/
    datasets/
      oasis.py                 OASIS dataset adapter with participant clustering
      lasi_dad.py              LASI-DAD stub adapter (awaiting official codebook & DUA)
    preprocess.py              Data cleaning and leakage-free ColumnTransformer
    train.py                   Stratified 5-fold CV comparison and model fitting
    evaluate.py                Bootstrap 95% CIs and threshold optimization
    explain.py                 Dependency-free runtime occlusion explainability
    fairness.py                Subgroup parity audits (Sex, Age, Education, SES)
    predict.py                 Runtime inference and risk band assignment
    export.py                  Artifact deployment to backend/models/
  artifacts/
    form_spec.json             Schema contract defining the profile input form
    model_with_mmse.joblib     Model trained with MMSE/HMSE score
    model_without_mmse.joblib  Model trained with self-report features only
    *_metadata.json            Thresholds, risk bands, metrics, CIs, and background summary
  reports/
    figures/                   Publication-quality evaluation plots
    model_comparison.csv       CV benchmark table across 5 classifier architectures
  tests/                       Unit and integration tests for ML pipeline
```

## Running the Pipeline

You can run individual stages using Make:
```bash
make eda        # Generate missingness, correlation, and distribution figures
make train      # Run 5-fold CV comparison across 5 models and train pipelines
make evaluate   # Evaluate held-out test set with bootstrap 95% CIs and fairness
make explain    # Run explainability checks and validate feature ranking
make export     # Copy trained joblib models and metadata to backend/models/
make test       # Execute test suite
make retrain DATASET=oasis       # One-command retrain on OASIS with quality gate enforcement
make retrain DATASET=lasi_dad   # Retrain pipeline against LASI-DAD mapping/synthetic cohort
```

Or run everything end-to-end:
```bash
make all
```

## Form Specification Schema Contract (`form_spec.json`)

The screening profile intake form for frontend teammate B3 is strictly defined by `ml/artifacts/form_spec.json` (and `backend/models/form_spec.json`). This schema is automatically derived from the active dataset mapping (`ml/config/oasis_mapping.yaml` or `ml/config/lasi_dad_mapping.yaml`):

```json
{
  "schema_version": "1.1.0",
  "dataset": "OASIS-demo",
  "model_status": "demo_oasis_not_validated_for_lasi_dad",
  "disclaimer": "This tool is a cognitive risk screening aid designed for preliminary assessment, NOT a clinical diagnosis.",
  "disclaimer_or": "ଏହି ଉପକରଣଟି କେବଳ ଏକ ପ୍ରାଥମିକ ଜ୍ଞାନଗତ ବିପଦ ଯାଞ୍ଚ ସହାୟକ, କୌଣସି ଡାକ୍ତରୀ ନିଦାନ ନୁହେଁ। [needs native review]",
  "fields": [
    {
      "name": "Age",
      "label": "Age (years)",
      "label_or": "ବୟସ (ବର୍ଷ) [needs native review]",
      "type": "number",
      "min": 40,
      "max": 120,
      "step": 1,
      "required": true,
      "help_text": "Participant age in complete years (40-120).",
      "help_text_or": "ଅଂଶଗ୍ରହଣକାରୀଙ୍କ ସମ୍ପୂର୍ଣ୍ଣ ବୟସ (୪୦-୧୨୦)। [needs native review]",
      "model_variant": "both"
    },
    {
      "name": "Sex",
      "label": "Biological Sex",
      "label_or": "ଲିଙ୍ଗ [needs native review]",
      "type": "select",
      "options": [
        {"value": "M", "label": "Male", "label_or": "ପୁରୁଷ [needs native review]"},
        {"value": "F", "label": "Female", "label_or": "ମହିଳା [needs native review]"}
      ],
      "required": true,
      "help_text": "Biological sex assigned at birth.",
      "help_text_or": "ଜନ୍ମ ସମୟର ଜୈବିକ ଲିଙ୍ଗ। [needs native review]",
      "model_variant": "both"
    },
    {
      "name": "EDUC",
      "label": "Education (years)",
      "label_or": "ଶିକ୍ଷା (ବର୍ଷ) [needs native review]",
      "type": "number",
      "min": 0,
      "max": 30,
      "step": 1,
      "required": true,
      "help_text": "Total years of completed formal schooling (0-30).",
      "help_text_or": "ସମ୍ପୂର୍ଣ୍ଣ ଶିକ୍ଷାର ମୋଟ ବର୍ଷ (୦-୩୦)। [needs native review]",
      "model_variant": "both"
    },
    {
      "name": "SES",
      "label": "Socioeconomic Status (1-5)",
      "label_or": "ସାମାଜିକ-ଅର୍ଥନୈତିକ ସ୍ଥିତି (୧-୫) [needs native review]",
      "type": "number",
      "min": 1,
      "max": 5,
      "step": 1,
      "required": false,
      "help_text": "Hollingshead socioeconomic status index (1=Highest, 5=Lowest). Optional.",
      "help_text_or": "ସାମାଜିକ-ଅର୍ଥନୈତିକ ସ୍ଥିତି ସୂଚକାଙ୍କ (୧ ରୁ ୫)। [needs native review]",
      "model_variant": "both"
    },
    {
      "name": "MMSE",
      "label": "MMSE / HMSE Total Score (0-30)",
      "label_or": "ଏମ୍.ଏମ୍.ଏସ୍.ଇ / ଏଚ୍.ଏମ୍.ଏସ୍.ଇ ମୋଟ ସ୍କୋର (୦-୩୦) [needs native review]",
      "type": "number",
      "min": 0,
      "max": 30,
      "step": 1,
      "required": true,
      "help_text": "Total score from Mini-Mental State Examination or Hindi/Odia Mental State Examination (0-30).",
      "help_text_or": "ଜ୍ଞାନଗତ ପରୀକ୍ଷଣର ମୋଟ ସ୍କୋର (୦-୩୦)। [needs native review]",
      "model_variant": "with_mmse"
    }
  ]
}
```

## Switching from OASIS to LASI-DAD
1. Obtain approved credentials from the Gateway to Global Aging Data and download the LASI-DAD wave 1 harmonized dataset (`.csv` or `.dta`).
2. Update the variable mappings in `ml/config/lasi_dad_mapping.yaml` to replace `TEMPLATE_` placeholders with the exact variable codes from the official codebook.
3. Test schema compliance using:
   ```bash
   python -m ml.src.make_synthetic_lasi   # generates synthetic testing cohort
   python -m ml.src.retrain --dataset lasi_dad
   ```
4. Place authorized non-synthetic data into `ml/data/lasi_dad.csv` (never commit real participant data; `.gitignore` will enforce exclusion).
5. Run `make retrain DATASET=lasi_dad`. The script enforces strict quality gates (zero participant overlap, label permutation AUC ~0.50, minimum CV AUC & sensitivity) before updating the production models in `backend/models/`.
