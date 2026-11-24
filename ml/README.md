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
```

Or run everything end-to-end:
```bash
make all
```

## Switching from OASIS to LASI-DAD
1. Acquire access to LASI-DAD data via Gateway to Global Aging Data and adhere to the Data Use Agreement (DUA).
2. Place the verified LASI-DAD CSV in `ml/data/lasi_dad.csv` and the official codebook in `ml/docs/`.
3. In `ml/config.yaml`, change `dataset.active` to `lasi_dad`.
4. Update `ml/src/datasets/lasi_dad.py` to map the exact verified column names for demographics, HMSE items, and clinical dementia status.
5. Re-run `make all` to train and export the updated models.
