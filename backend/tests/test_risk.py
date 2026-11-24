"""Unit and integration tests for the /api/risk screening endpoints."""
import os
import sys
import unittest
from fastapi.testclient import TestClient

# Ensure backend and repo root are in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.main import app
from app.db import connect, init_db


class TestRiskAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_form_spec_endpoint(self):
        """GET /api/risk/form-spec returns the form specification schema."""
        res = self.client.get("/api/risk/form-spec")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("fields", data)
        self.assertIn("disclaimer", data)
        self.assertTrue(any(f["name"] == "Age" for f in data["fields"]))
        self.assertTrue(any(f["name"] == "MMSE" for f in data["fields"]))

    def test_model_info_endpoint(self):
        """GET /api/risk/model-info returns metadata for both models without background data."""
        res = self.client.get("/api/risk/model-info")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("model_with_mmse", data)
        self.assertIn("model_without_mmse", data)

        for variant in ["model_with_mmse", "model_without_mmse"]:
            info = data[variant]
            self.assertIn("threshold", info)
            self.assertIn("test_metrics", info)
            self.assertIn("risk_bands", info)
            # Ensure background raw data is not leaked
            self.assertNotIn("background_summary", info)

    def test_predict_happy_path_with_mmse(self):
        """POST /api/risk/predict happy path for with_mmse variant."""
        payload = {
            "profile": {
                "Age": 76,
                "Sex": "M",
                "EDUC": 14,
                "SES": 2,
                "MMSE": 26
            },
            "use_mmse": True
        }
        res = self.client.post("/api/risk/predict", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("probability", data)
        self.assertTrue(0.0 <= data["probability"] <= 1.0)
        self.assertIn(data["band"], ["lower", "moderate", "higher"])
        self.assertEqual(data["model_variant"], "model_with_mmse")
        self.assertIn("disclaimer", data)
        self.assertTrue(len(data["explanation"]) > 0)

    def test_predict_happy_path_without_mmse(self):
        """POST /api/risk/predict happy path for without_mmse variant."""
        payload = {
            "profile": {
                "Age": 72,
                "Sex": "F",
                "EDUC": 10,
                "SES": 3
            },
            "use_mmse": False
        }
        res = self.client.post("/api/risk/predict", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("probability", data)
        self.assertTrue(0.0 <= data["probability"] <= 1.0)
        self.assertIn(data["band"], ["lower", "moderate", "higher"])
        self.assertEqual(data["model_variant"], "model_without_mmse")
        self.assertIn("disclaimer", data)
        # Ensure MMSE is NOT in explanations for without_mmse
        self.assertFalse(any(e["feature"] == "MMSE" for e in data["explanation"]))

    def test_predict_bad_input_unknown_field(self):
        """Unknown fields in profile must be strictly rejected with 422."""
        payload = {
            "profile": {
                "Age": 70,
                "Sex": "F",
                "EDUC": 12,
                "unauthorized_field": "hack"
            },
            "use_mmse": False
        }
        res = self.client.post("/api/risk/predict", json=payload)
        self.assertEqual(res.status_code, 422)

    def test_predict_bad_input_out_of_range(self):
        """Out of range values must trigger 422 error."""
        # Age too low (<40)
        res = self.client.post("/api/risk/predict", json={
            "profile": {"Age": 25, "Sex": "M", "EDUC": 12},
            "use_mmse": False
        })
        self.assertEqual(res.status_code, 422)

        # MMSE out of bounds (>30)
        res2 = self.client.post("/api/risk/predict", json={
            "profile": {"Age": 70, "Sex": "M", "EDUC": 12, "MMSE": 35},
            "use_mmse": True
        })
        self.assertEqual(res2.status_code, 422)

    def test_predict_missing_required_field(self):
        """Missing required fields (e.g. Sex or Age) must trigger 422."""
        res = self.client.post("/api/risk/predict", json={
            "profile": {"Age": 70, "EDUC": 12},  # Sex missing
            "use_mmse": False
        })
        self.assertEqual(res.status_code, 422)

    def test_stateless_no_persistence(self):
        """Predictions must be strictly stateless and never persist health profile data in the database."""
        with connect() as con:
            initial_users = con.execute("SELECT count(*) as c FROM users").fetchone()["c"]
            initial_sessions = con.execute("SELECT count(*) as c FROM sessions").fetchone()["c"]
            initial_attempts = con.execute("SELECT count(*) as c FROM attempts").fetchone()["c"]

        # Run several predictions
        self.client.post("/api/risk/predict", json={
            "profile": {"Age": 80, "Sex": "M", "EDUC": 8, "SES": 4},
            "use_mmse": False
        })
        self.client.post("/api/risk/predict", json={
            "profile": {"Age": 78, "Sex": "F", "EDUC": 16, "SES": 1, "MMSE": 29},
            "use_mmse": True
        })

        with connect() as con:
            final_users = con.execute("SELECT count(*) as c FROM users").fetchone()["c"]
            final_sessions = con.execute("SELECT count(*) as c FROM sessions").fetchone()["c"]
            final_attempts = con.execute("SELECT count(*) as c FROM attempts").fetchone()["c"]

        self.assertEqual(initial_users, final_users, "Violation: Users table modified by risk prediction endpoint!")
        self.assertEqual(initial_sessions, final_sessions, "Violation: Sessions table modified by risk prediction endpoint!")
        self.assertEqual(initial_attempts, final_attempts, "Violation: Attempts table modified by risk prediction endpoint!")


if __name__ == "__main__":
    unittest.main()
