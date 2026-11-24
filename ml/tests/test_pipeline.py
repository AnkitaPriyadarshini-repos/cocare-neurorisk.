"""Unit and validation tests for ML pipeline components, models, and explainability."""
import os
import sys
import json
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import StratifiedGroupKFold, cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from ml.src.datasets.oasis import load_oasis
from ml.src.datasets.lasi_dad import load_lasi_dad
from ml.src.preprocess import clean_raw_data, build_preprocessor
from ml.src.predict import predict_risk, load_model_and_metadata
from ml.src.explain import explain_one, FEATURE_TEXTS


class TestMLPipeline(unittest.TestCase):

    def test_lasi_dad_adapter_validation(self):
        """Verify LASI-DAD adapter schema validation and loud failures on mismatch."""
        # Test nonexistent file
        with self.assertRaises(FileNotFoundError):
            load_lasi_dad("ml/data/nonexistent_file.csv")

        # Test loud failure on column mismatch
        oasis_path = "ml/data/oasis_longitudinal.csv"
        if os.path.exists(oasis_path):
            with self.assertRaises(ValueError) as context:
                load_lasi_dad(oasis_path, allow_placeholders=True)
            self.assertIn("LASI-DAD Schema Validation Error", str(context.exception))

        # Test synthetic dataset ingestion
        synthetic_path = os.path.join("ml", "data", "lasi_dad_synthetic.csv")
        if not os.path.exists(synthetic_path):
            from ml.src.make_synthetic_lasi import generate_synthetic_lasi_dataset
            df_synth = generate_synthetic_lasi_dataset(seed=42)
            os.makedirs(os.path.dirname(synthetic_path), exist_ok=True)
            df_synth.to_csv(synthetic_path, index=False)

        X, y, groups = load_lasi_dad(synthetic_path, allow_placeholders=True)
        self.assertEqual(len(X), len(y))
        self.assertIn("Age", X.columns)
        self.assertIn("Sex", X.columns)
        self.assertIn("EDUC", X.columns)
        self.assertIn("MMSE", X.columns)
        self.assertTrue(groups.nunique() > 50)

    def test_without_mmse_has_no_mmse(self):
        """Verify that model_without_mmse contains zero references to MMSE in features or pipeline."""
        meta_path = os.path.join("ml", "artifacts", "model_without_mmse_metadata.json")
        if not os.path.exists(meta_path):
            self.skipTest("Model metadata not generated yet")

        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        # Check all feature lists
        self.assertNotIn("MMSE", meta["features"]["numeric"])
        self.assertNotIn("MMSE", meta["features"]["all_ordered"])

        # Check joblib pipeline transformers
        model_path = os.path.join("ml", "artifacts", "model_without_mmse.joblib")
        pipeline = joblib.load(model_path)
        preprocessor = pipeline.named_steps["preprocessor"]
        for name, trans, cols in preprocessor.transformers:
            if cols != "drop":
                self.assertNotIn("MMSE", cols)

    def test_predict_risk_both_variants(self):
        """Verify predict_risk works for both with_mmse and without_mmse variants."""
        profile_with = {"Age": 75, "Sex": "M", "EDUC": 14, "SES": 2, "MMSE": 26}
        profile_without = {"Age": 75, "Sex": "F", "EDUC": 10, "SES": 3}

        # Test with MMSE
        res_with = predict_risk(profile_with, use_mmse=True, models_dir="ml/artifacts")
        self.assertIn("probability", res_with)
        self.assertTrue(0.0 <= res_with["probability"] <= 1.0)
        self.assertIn(res_with["band"], ["lower", "moderate", "higher"])
        self.assertEqual(res_with["model_variant"], "model_with_mmse")
        self.assertEqual(res_with["model_status"], "demo_oasis_not_validated_for_lasi_dad")
        self.assertTrue(len(res_with["explanation"]) > 0)

        # Test without MMSE
        res_without = predict_risk(profile_without, use_mmse=False, models_dir="ml/artifacts")
        self.assertIn("probability", res_without)
        self.assertTrue(0.0 <= res_without["probability"] <= 1.0)
        self.assertIn(res_without["band"], ["lower", "moderate", "higher"])
        self.assertEqual(res_without["model_variant"], "model_without_mmse")
        self.assertEqual(res_without["model_status"], "demo_oasis_not_validated_for_lasi_dad")
        self.assertTrue(len(res_without["explanation"]) > 0)
        self.assertFalse(any(e["feature"] == "MMSE" for e in res_without["explanation"]))

    def test_participant_grouping_zero_overlap(self):
        """Audit test: Verify zero participant ID overlap between train and test splits."""
        data_path = os.path.join("ml", "data", "oasis_longitudinal.csv")
        if not os.path.exists(data_path):
            self.skipTest("Raw participant-level OASIS dataset omitted from repo for data privacy.")
        X_raw, y_raw, groups = load_oasis(data_path)
        X_clean, _ = clean_raw_data(X_raw)

        sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
        train_idx, test_idx = next(sgkf.split(X_clean, y_raw, groups=groups))

        train_subjects = set(groups.iloc[train_idx])
        test_subjects = set(groups.iloc[test_idx])
        overlap = train_subjects.intersection(test_subjects)
        self.assertEqual(len(overlap), 0, f"DATA LEAKAGE: {len(overlap)} subjects overlap between train and test!")

    def test_preprocessing_fit_on_train_only(self):
        """Audit test: Prove imputer and scaler statistics equal train split alone."""
        data_path = os.path.join("ml", "data", "oasis_longitudinal.csv")
        if not os.path.exists(data_path):
            self.skipTest("Raw participant-level OASIS dataset omitted from repo for data privacy.")
        X_raw, y_raw, groups = load_oasis(data_path)
        X_clean, _ = clean_raw_data(X_raw)

        sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
        train_idx, test_idx = next(sgkf.split(X_clean, y_raw, groups=groups))

        X_train = X_clean.iloc[train_idx]
        prep = build_preprocessor(["Age", "EDUC", "SES", "MMSE"], ["Sex"])
        pipe = Pipeline([
            ("preprocessor", prep),
            ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42))
        ])
        pipe.fit(X_train, y_raw.iloc[train_idx])

        fitted_prep = pipe.named_steps["preprocessor"]
        imputer = fitted_prep.named_transformers_["num"].named_steps["imputer"]
        scaler = fitted_prep.named_transformers_["num"].named_steps["scaler"]

        expected_medians = [float(X_train[c].median()) for c in ["Age", "EDUC", "SES", "MMSE"]]
        expected_means = [float(X_train[c].fillna(X_train[c].median()).mean()) for c in ["Age", "EDUC", "SES", "MMSE"]]

        np.testing.assert_allclose(list(imputer.statistics_), expected_medians)
        np.testing.assert_allclose(list(scaler.mean_), expected_means)

    def test_label_permutation_sanity_check(self):
        """Sanity check: Label-shuffled CV ROC-AUC must collapse to near random chance (~0.50)."""
        data_path = os.path.join("ml", "data", "oasis_longitudinal.csv")
        if not os.path.exists(data_path):
            self.skipTest("Raw participant-level OASIS dataset omitted from repo for data privacy.")
        X_raw, y_raw, groups = load_oasis(data_path)
        X_clean, _ = clean_raw_data(X_raw)

        rng = np.random.RandomState(42)
        y_shuffled = pd.Series(rng.permutation(y_raw.values), index=y_raw.index)

        prep = build_preprocessor(["Age", "EDUC", "SES", "MMSE"], ["Sex"])
        pipe = Pipeline([
            ("preprocessor", prep),
            ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42))
        ])
        cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
        scores = cross_validate(pipe, X_clean, y_shuffled, groups=groups, cv=cv, scoring=["roc_auc"])
        mean_auc = float(np.mean(scores["test_roc_auc"]))
        self.assertTrue(0.40 <= mean_auc <= 0.60, f"Permutation AUC unexpected: {mean_auc}")

    def test_mmse_monotonicity(self):
        """Monotonicity test: For fixed Age, Sex, EDUC, SES, predicted risk must be non-increasing as MMSE rises 10 to 30."""
        reference_profiles = [
            {"Age": 75, "Sex": "F", "EDUC": 14, "SES": 2.0},
            {"Age": 68, "Sex": "M", "EDUC": 16, "SES": 1.0},
            {"Age": 82, "Sex": "F", "EDUC": 8, "SES": 4.0},
        ]
        for ref in reference_profiles:
            risks = []
            for mmse in range(10, 31):
                p = ref.copy()
                p["MMSE"] = float(mmse)
                res = predict_risk(p, use_mmse=True, models_dir="backend/models" if os.path.exists("backend/models/model_with_mmse.joblib") else "ml/artifacts")
                risks.append(res["probability"])
            for i in range(len(risks) - 1):
                self.assertGreaterEqual(
                    risks[i],
                    risks[i + 1],
                    f"Monotonicity violation for profile {ref} at MMSE={10+i} ({risks[i]}) -> MMSE={11+i} ({risks[i+1]})"
                )

    def test_all_features_have_localization_texts(self):
        """Verify that every feature has stable text_keys in English and Odia with review flags."""
        features = ["Age", "Sex", "EDUC", "SES", "MMSE"]
        for feat in features:
            self.assertIn(feat, FEATURE_TEXTS)
            for eff in ["raises", "lowers"]:
                entry = FEATURE_TEXTS[feat][eff]
                self.assertIn("key", entry)
                self.assertTrue(entry["key"].startswith(f"risk.{feat.lower()}."))
                self.assertIn("en", entry)
                self.assertTrue(len(entry["en"]) > 5)
                self.assertIn("or", entry)
                self.assertTrue(len(entry["or"]) > 5)
                self.assertIn("[needs native review]", entry["or"])

    def test_input_validation_and_imputation(self):
        """Verify that missing optional fields like SES are imputed gracefully."""
        profile = {"Age": 70, "Sex": "F", "EDUC": 12}
        res = predict_risk(profile, use_mmse=False, models_dir="ml/artifacts")
        self.assertTrue(0.0 <= res["probability"] <= 1.0)


if __name__ == "__main__":
    unittest.main()
