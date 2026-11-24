"""Preprocessing and data quality pipelines for cognitive risk screening.

Ensures strict no-leakage by encapsulating all imputations and transformations
inside scikit-learn transformers fitted strictly on training data.
"""
from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer


def clean_raw_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean and validate raw tabular data.

    - Recodes invalid/refused codes (-1, 99, 999, 'Unknown', 'None') to NaN.
    - Fixes data types.
    - Clips physically/biologically impossible values (e.g. Age < 40 or > 120).
    - Produces a data quality summary.
    """
    df_clean = df.copy()
    dq_issues = []

    # Recode common missing/refused sentinel values
    sentinels = [-1, 99, 999, "-1", "99", "999", "Unknown", "unknown", "None", "NULL", ""]
    df_clean = df_clean.replace(sentinels, np.nan)

    # Validate and clean Age
    if "Age" in df_clean.columns:
        df_clean["Age"] = pd.to_numeric(df_clean["Age"], errors="coerce")
        invalid_age = (df_clean["Age"] < 40) | (df_clean["Age"] > 120)
        if invalid_age.any():
            count = int(invalid_age.sum())
            dq_issues.append(f"Clipped {count} Age records outside valid bounds [40, 120].")
            df_clean["Age"] = df_clean["Age"].clip(40, 120)

    # Validate and clean EDUC
    if "EDUC" in df_clean.columns:
        df_clean["EDUC"] = pd.to_numeric(df_clean["EDUC"], errors="coerce")
        invalid_educ = (df_clean["EDUC"] < 0) | (df_clean["EDUC"] > 30)
        if invalid_educ.any():
            count = int(invalid_educ.sum())
            dq_issues.append(f"Clipped {count} EDUC records outside valid bounds [0, 30].")
            df_clean["EDUC"] = df_clean["EDUC"].clip(0, 30)

    # Validate and clean SES
    if "SES" in df_clean.columns:
        df_clean["SES"] = pd.to_numeric(df_clean["SES"], errors="coerce")
        invalid_ses = (df_clean["SES"] < 1) | (df_clean["SES"] > 5)
        if invalid_ses.any():
            count = int(invalid_ses.sum())
            dq_issues.append(f"Clipped {count} SES records outside valid bounds [1, 5].")
            df_clean["SES"] = df_clean["SES"].clip(1, 5)

    # Validate and clean MMSE
    if "MMSE" in df_clean.columns:
        df_clean["MMSE"] = pd.to_numeric(df_clean["MMSE"], errors="coerce")
        invalid_mmse = (df_clean["MMSE"] < 0) | (df_clean["MMSE"] > 30)
        if invalid_mmse.any():
            count = int(invalid_mmse.sum())
            dq_issues.append(f"Clipped {count} MMSE records outside valid bounds [0, 30].")
            df_clean["MMSE"] = df_clean["MMSE"].clip(0, 30)

    # Standardize Sex
    if "Sex" in df_clean.columns:
        df_clean["Sex"] = df_clean["Sex"].astype(str).str.strip().str.upper()
        # Standardize M/F
        valid_sex = df_clean["Sex"].isin(["M", "F"])
        if not valid_sex.all():
            dq_issues.append(f"Found {(~valid_sex).sum()} unrecognized Sex values; set to NaN.")
            df_clean.loc[~valid_sex, "Sex"] = np.nan

    quality_report = {
        "initial_rows": len(df),
        "cleaned_rows": len(df_clean),
        "missing_counts": df_clean.isna().sum().to_dict(),
        "missing_pcts": (df_clean.isna().mean() * 100).round(2).to_dict(),
        "issues_addressed": dq_issues
    }

    return df_clean, quality_report


def build_preprocessor(
    numeric_features: List[str],
    categorical_features: List[str]
) -> ColumnTransformer:
    """Build a leakage-free ColumnTransformer pipeline.

    - Numeric: Median imputation + StandardScaler.
    - Categorical: Most-frequent / constant imputation + OneHotEncoder(handle_unknown='ignore').
    """
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features)
        ],
        remainder="drop"
    )

    return preprocessor
