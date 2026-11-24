"""Tests for ML pipeline components, models, and predictions."""
import os
import sys
import json
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import numpy as np
import pandas as pd
import joblib

try:
    import pytest
except ImportError:
    pytest = None

from ml.src.datasets.oasis import load_oasis
from ml.src.datasets.lasi_dad import load_lasi_dad
from ml.src.preprocess import clean_raw_data, build_preprocessor
from ml.src.predict import predict_risk, load_model_and_metadata
from ml.src.explain import explain_one


class TestMLPipeline(unittest.TestCase):

    def test_lasi_dad_stub(self):
        """Verify LASI-DAD is a clearly marked stub and does not invent columns."""
        with self.assertRaises(NotImplementedError) as context:
            load_lasi_dad()
        self.assertIn("stub awaiting the official LASI-DAD codebook", str(context.exception))

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
        profile_with = {
            "Age": 75,
            "Sex": "M",
            "EDUC": 14,
            "SES": 2,
            "MMSE": 26
        }

        profile_without = {
            "Age": 75,
            "Sex": "F",
            "EDUC": 10,
            "SES": 3
        }

        # Test with MMSE
        res_with = predict_risk(profile_with, use_mmse=True, models_dir="ml/artifacts")
        self.assertIn("probability", res_with)
        self.assertTrue(0.0 <= res_with["probability"] <= 1.0)
        self.assertIn(res_with["band"], ["lower", "moderate", "higher"])
        self.assertEqual(res_with["model_variant"], "model_with_mmse")
        self.assertTrue(len(res_with["explanation"]) > 0)

        # Test without MMSE
        res_without = predict_risk(profile_without, use_mmse=False, models_dir="ml/artifacts")
        self.assertIn("probability", res_without)
        self.assertTrue(0.0 <= res_without["probability"] <= 1.0)
        self.assertIn(res_without["band"], ["lower", "moderate", "higher"])
        self.assertEqual(res_without["model_variant"], "model_without_mmse")
        self.assertTrue(len(res_without["explanation"]) > 0)
        # Confirm MMSE is not in explanation
        self.assertFalse(any(e["feature"] == "MMSE" for e in res_without["explanation"]))

    def test_explain_one_structure_and_localization(self):
        """Verify that explanations contain stable keys and Odia placeholders."""
        profile = {"Age": 82, "Sex": "M", "EDUC": 8, "SES": 4, "MMSE": 22}
        res = predict_risk(profile, use_mmse=True, models_dir="ml/artifacts")

        for item in res["explanation"]:
            self.assertIn("feature", item)
            self.assertIn(item["effect"], ["raises", "lowers"])
            self.assertIn("magnitude", item)
            self.assertIn("text_key", item)
            self.assertIn("text_en", item)
            self.assertIn("text_or", item)
            self.assertIn("needs native review", item["text_or"])

    def test_input_validation_and_imputation(self):
        """Verify that missing optional fields like SES are imputed gracefully."""
        profile = {"Age": 70, "Sex": "F", "EDUC": 12}  # SES omitted
        res = predict_risk(profile, use_mmse=False, models_dir="ml/artifacts")
        self.assertTrue(0.0 <= res["probability"] <= 1.0)


if __name__ == "__main__":
    unittest.main()
