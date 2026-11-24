"""OASIS Longitudinal Dementia Dataset Adapter.

Loads and standardizes the OASIS Longitudinal Dataset for dementia screening.
Performs honest participant-level grouping to prevent data leakage across visits.
"""
import os
from typing import Tuple, Optional
import pandas as pd
import numpy as np


def load_oasis(
    csv_path: Optional[str] = None,
    baseline_only: bool = False
) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Load OASIS longitudinal dataset and return standardized features, target, and participant groups.

    Args:
        csv_path: Path to oasis_longitudinal.csv. If None, uses default project location.
        baseline_only: If True, keep only Visit == 1 for each participant.

    Returns:
        X: DataFrame containing demographic and clinical features.
        y: Binary Series (1 = Demented / CDR > 0, 0 = Nondemented).
        groups: Series of participant IDs (Subject ID) for StratifiedGroupKFold splitting.
    """
    if csv_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        csv_path = os.path.join(base_dir, "data", "oasis_longitudinal.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"OASIS dataset not found at '{csv_path}'. "
            "Please ensure oasis_longitudinal.csv is placed in ml/data/."
        )

    df = pd.read_csv(csv_path)

    # Standardize column names
    df = df.rename(columns={"M/F": "Sex"})

    if baseline_only:
        df = df[df["Visit"] == 1].copy()

    # Define binary target:
    # In OASIS, CDR 0 = Nondemented, CDR > 0 = Demented/Impaired (0.5 very mild, 1.0 mild, 2.0 moderate)
    # Alternatively Group == 'Demented' (or Converted with CDR > 0)
    # We use CDR > 0 or Group == 'Demented' as clinical standard for cognitive risk screening
    target = np.where(df["CDR"] > 0, 1, 0)
    # Also handle any missing CDR using Group
    if df["CDR"].isna().any():
        group_target = np.where(df["Group"] == "Demented", 1, 0)
        target = np.where(df["CDR"].isna(), group_target, target)

    y = pd.Series(target, index=df.index, name="target")
    groups = df["Subject ID"].copy()

    # Features dataframe
    feature_cols = ["Subject ID", "Age", "Sex", "EDUC", "SES", "MMSE"]
    available_cols = [c for c in feature_cols if c in df.columns]
    X = df[available_cols].copy()

    return X, y, groups
