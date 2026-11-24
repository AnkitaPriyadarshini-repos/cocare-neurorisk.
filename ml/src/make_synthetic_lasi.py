"""Synthetic LASI-DAD Data Generator for Pre-Access Pipeline Verification.

Generates a fully synthetic, randomly generated tabular cohort matching the exact schema
defined in ml/config/lasi_dad_mapping.yaml.

CRITICAL DISCLAIMER:
THIS DATASET IS COMPLETELY SYNTHETIC AND RANDOMLY GENERATED FOR PIPELINE TESTING.
IT CONTAINS NO REAL PARTICIPANT DATA AND BEARS NO RELATION TO ACTUAL LASI-DAD SUBJECTS.
"""
import os
import argparse
import numpy as np
import pandas as pd
import yaml

from ml.src.datasets.lasi_dad import load_mapping


def generate_synthetic_lasi_dataset(
    n_participants: int = 200,
    n_records: int = 450,
    seed: int = 42,
    mapping_path: str = None
) -> pd.DataFrame:
    """Generate a realistic synthetic cohort matching the LASI-DAD schema."""
    rng = np.random.RandomState(seed)
    mapping = load_mapping(mapping_path)
    
    # 1. Generate participants and repeated visits
    participant_ids = [f"SYNTH_IND_{i:04d}" for i in range(1, n_participants + 1)]
    # Each participant has 1 to 4 visits
    records_sub = rng.choice(participant_ids, size=n_records, replace=True)
    records_sub = sorted(records_sub)
    
    data = {}
    id_var = mapping.get("participant_id_variable", "TEMPLATE_PARTICIPANT_ID")
    data[id_var] = records_sub
    
    # Participant baseline traits
    sub_sex = {pid: rng.choice([1, 2], p=[0.48, 0.52]) for pid in participant_ids}
    # Education distribution reflecting Indian elderly cohort (higher prevalence of 0-5 years)
    sub_educ = {pid: int(rng.choice([0, 2, 5, 8, 10, 12, 16], p=[0.30, 0.15, 0.20, 0.15, 0.10, 0.07, 0.03])) for pid in participant_ids}
    sub_ses = {pid: int(rng.choice([1, 2, 3, 4, 5], p=[0.15, 0.25, 0.30, 0.20, 0.10])) for pid in participant_ids}
    sub_base_age = {pid: int(rng.randint(45, 88)) for pid in participant_ids}
    sub_dementia_risk = {pid: rng.beta(2, 5) for pid in participant_ids}
    
    # Visit tracking
    sub_visit_count = {}
    
    ages, sexes, educs, ses_list, hmse_list, targets = [], [], [], [], [], []
    
    for pid in records_sub:
        v_idx = sub_visit_count.get(pid, 0)
        sub_visit_count[pid] = v_idx + 1
        
        age = sub_base_age[pid] + v_idx * 2
        sex = sub_sex[pid]
        educ = sub_educ[pid]
        ses = sub_ses[pid]
        
        # Risk latent variable influenced by age, education, and individual propensity
        risk_score = sub_dementia_risk[pid] + 0.02 * (age - 65) - 0.015 * educ + rng.normal(0, 0.1)
        prob = 1.0 / (1.0 + np.exp(-risk_score * 3))
        target = 1 if prob > 0.65 else 0
        
        # HMSE total score correlated with target, education, and age
        base_hmse = 27.0 - (7.0 if target == 1 else 0.0) + 0.2 * min(educ, 12) - 0.05 * (age - 60)
        hmse = int(np.clip(base_hmse + rng.normal(0, 2.5), 0, 30))
        
        ages.append(age)
        sexes.append(sex)
        educs.append(educ)
        ses_list.append(ses)
        hmse_list.append(hmse)
        targets.append(target)
        
    # Map into source variable names from mapping configuration
    for var in mapping.get("variables", []):
        std = var["standard_name"]
        src = var["source_variable"]
        if std == "Age":
            data[src] = ages
        elif std == "Sex":
            data[src] = sexes
        elif std == "EDUC":
            data[src] = educs
        elif std == "SES":
            # Introduce 5% realistic missingness
            ses_arr = np.array(ses_list, dtype=float)
            mask_miss = rng.rand(len(ses_arr)) < 0.05
            ses_arr[mask_miss] = -99  # sentinel missing code
            data[src] = ses_arr
        elif std == "MMSE":
            data[src] = hmse_list
            
    target_var = mapping.get("target_definition", {}).get("source_variable", "TEMPLATE_DEMENTIA_STATUS")
    data[target_var] = targets
    
    df = pd.DataFrame(data)
    return df


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic LASI-DAD validation cohort.")
    parser.add_argument("--output", type=str, default=None, help="Output CSV path.")
    parser.add_argument("--n_records", type=int, default=450, help="Number of records to generate.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    args = parser.parse_args()
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if args.output is None:
        args.output = os.path.join(base_dir, "ml", "data", "lasi_dad_synthetic.csv")
        
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df = generate_synthetic_lasi_dataset(n_records=args.n_records, seed=args.seed)
    
    df.to_csv(args.output, index=False)
    print(f"SUCCESS: Generated {len(df)} synthetic records written to '{args.output}'.")
    print(f"Target prevalence: {df.iloc[:, -1].mean():.2%}")
    print(f"Unique participants: {df.iloc[:, 0].nunique()}")


if __name__ == "__main__":
    main()
