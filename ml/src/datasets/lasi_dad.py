"""LASI-DAD (Longitudinal Aging Study in India - Diagnostic Assessment of Dementia) Adapter.

Config-driven ingestion adapter that reads ml/config/lasi_dad_mapping.yaml to standardize
raw survey/harmonized files into CO CARE screening features.
Fails loudly if required variables are missing from the raw dataset.
"""
import os
from typing import Tuple, Optional, Dict, Any, List
import yaml
import numpy as np
import pandas as pd


def load_mapping(mapping_path: Optional[str] = None) -> Dict[str, Any]:
    """Load LASI-DAD YAML variable mapping configuration."""
    if mapping_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        mapping_path = os.path.join(base_dir, "config", "lasi_dad_mapping.yaml")
        
    if not os.path.exists(mapping_path):
        raise FileNotFoundError(f"Mapping configuration not found at '{mapping_path}'.")
        
    with open(mapping_path, "r", encoding="utf-8") as f:
        mapping = yaml.safe_load(f)
        
    return mapping


def validate_columns_against_mapping(df_columns: List[str], mapping: Dict[str, Any]):
    """Strict schema validator: Fails loudly if raw dataset is missing mapped variables."""
    missing_sources = []
    
    # Check participant identifier
    id_var = mapping.get("participant_id_variable", "TEMPLATE_PARTICIPANT_ID")
    if id_var not in df_columns:
        missing_sources.append(f"Participant ID '{id_var}'")
        
    # Check target variable
    target_var = mapping.get("target_definition", {}).get("source_variable", "TEMPLATE_DEMENTIA_STATUS")
    if target_var not in df_columns:
        missing_sources.append(f"Target '{target_var}'")
        
    # Check feature variables
    for var in mapping.get("variables", []):
        src = var["source_variable"]
        if src not in df_columns:
            missing_sources.append(f"Feature '{src}' (mapped to {var['standard_name']})")
            
    if missing_sources:
        raise ValueError(
            f"LASI-DAD Schema Validation Error: The provided dataset is missing {len(missing_sources)} "
            f"mapped variables specified in the mapping configuration:\n - " + "\n - ".join(missing_sources) +
            "\nPlease update ml/config/lasi_dad_mapping.yaml once the official codebook is available."
        )


def load_lasi_dad(
    csv_path: Optional[str] = None,
    mapping_path: Optional[str] = None,
    allow_placeholders: bool = False
) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Load, validate, and standardize LASI-DAD dataset using configuration mapping.

    Args:
        csv_path: Path to raw LASI-DAD csv or Stata file.
        mapping_path: Path to lasi_dad_mapping.yaml.
        allow_placeholders: If True, allows TEMPLATE_ column names (for synthetic testing).

    Returns:
        X: Standardized feature DataFrame.
        y: Standardized binary target Series.
        groups: Participant identifier Series for grouped cross-validation.
    """
    mapping = load_mapping(mapping_path)
    
    if csv_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        csv_path = os.path.join(base_dir, "data", "lasi_dad.csv")
        
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"LASI-DAD dataset not found at '{csv_path}'. "
            "To test the pipeline prior to receiving access-controlled data, "
            "run 'python -m ml.src.make_synthetic_lasi' to generate a synthetic test dataset."
        )
        
    df = pd.read_csv(csv_path)
    
    # Check if mapping still contains template placeholders when reading real data
    if not allow_placeholders:
        has_template_keys = any(
            v["source_variable"].startswith("TEMPLATE_") for v in mapping.get("variables", [])
        )
        if has_template_keys and not any(c.startswith("TEMPLATE_") for c in df.columns):
            raise ValueError(
                "LASI-DAD Mapping Incomplete: ml/config/lasi_dad_mapping.yaml currently contains "
                "placeholder variable names marked 'TEMPLATE_'. Please replace them with actual column names "
                "from the LASI-DAD codebook before ingesting non-synthetic participant data."
            )
            
    validate_columns_against_mapping(list(df.columns), mapping)
    
    # Standardize features
    standard_data = {}
    for var in mapping.get("variables", []):
        src = var["source_variable"]
        std_name = var["standard_name"]
        val_series = df[src].copy()
        
        # Recode missing codes
        missing_codes = var.get("missing_codes", [])
        val_series = val_series.replace(missing_codes, np.nan)
        
        # Apply categorical mappings if present
        if "value_mapping" in var:
            val_series = val_series.map(var["value_mapping"]).fillna(val_series)
            
        standard_data[std_name] = val_series
        
    X = pd.DataFrame(standard_data, index=df.index)
    
    # Standardize target
    target_def = mapping["target_definition"]
    t_src = target_def["source_variable"]
    t_series = df[t_src].copy()
    t_series = t_series.replace(target_def.get("missing_codes", []), np.nan)
    pos_vals = target_def.get("positive_values", [1, "1"])
    y = pd.Series(np.where(t_series.isin(pos_vals), 1, 0), index=df.index, name="target")
    
    # Participant groups
    id_src = mapping["participant_id_variable"]
    groups = df[id_src].copy()
    X.insert(0, "Subject ID", groups)
    
    return X, y, groups
