"""Unit and integration tests for the /api/risk screening endpoints, health checks, and hardening."""
import os
import sys
import unittest
import logging
from unittest.mock import patch
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

    def test_health_endpoint(self):
        """GET /api/risk/health returns 200 with service health and model status."""
        res = self.client.get("/api/risk/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "risk_screening")
        self.assertEqual(data["model_status"], "demo_oasis_not_validated_for_lasi_dad")
        self.assertIn("models", data)
        self.assertTrue(data["models"]["model_with_mmse"]["loaded"])
        self.assertTrue(data["models"]["model_without_mmse"]["loaded"])

    def test_form_spec_endpoint(self):
        """GET /api/risk/form-spec returns the form specification schema with dataset & schema_version."""
        res = self.client.get("/api/risk/form-spec")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("fields", data)
        self.assertIn("disclaimer", data)
        self.assertIn("schema_version", data)
        self.assertEqual(data.get("dataset"), "OASIS-demo")
        self.assertEqual(data.get("model_status"), "demo_oasis_not_validated_for_lasi_dad")
        self.assertTrue(any(f["name"] == "Age" for f in data["fields"]))
        self.assertTrue(any(f["name"] == "MMSE" for f in data["fields"]))

    def test_model_info_endpoint(self):
        """GET /api/risk/model-info returns metadata for both models including model_status."""
        res = self.client.get("/api/risk/model-info")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("model_with_mmse", data)
        self.assertIn("model_without_mmse", data)

        for variant in ["model_with_mmse", "model_without_mmse"]:
            info = data[variant]
            self.assertEqual(info["model_status"], "demo_oasis_not_validated_for_lasi_dad")
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
        self.assertEqual(data["model_status"], "demo_oasis_not_validated_for_lasi_dad")
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
        self.assertEqual(data["model_status"], "demo_oasis_not_validated_for_lasi_dad")
        self.assertIn("disclaimer", data)
        self.assertFalse(any(e["feature"] == "MMSE" for e in data["explanation"]))

    def test_input_validation_fuzzing(self):
        """Fuzz testing input validation: rejects out-of-range, nulls, wrong types, and huge payloads."""
        # 1. Unknown fields
        res1 = self.client.post("/api/risk/predict", json={
            "profile": {"Age": 70, "Sex": "F", "EDUC": 12, "unauthorized_field": "test"},
            "use_mmse": False
        })
        self.assertEqual(res1.status_code, 422)

        # 2. Extreme Age (<40 or >120)
        res2 = self.client.post("/api/risk/predict", json={
            "profile": {"Age": 25, "Sex": "M", "EDUC": 12},
            "use_mmse": False
        })
        self.assertEqual(res2.status_code, 422)

        res3 = self.client.post("/api/risk/predict", json={
            "profile": {"Age": 150, "Sex": "M", "EDUC": 12},
            "use_mmse": False
        })
        self.assertEqual(res3.status_code, 422)

        # 3. Wrong type for Age
        res4 = self.client.post("/api/risk/predict", json={
            "profile": {"Age": "eighty", "Sex": "M", "EDUC": 12},
            "use_mmse": False
        })
        self.assertEqual(res4.status_code, 422)

        # 4. Null value for required field
        res5 = self.client.post("/api/risk/predict", json={
            "profile": {"Age": None, "Sex": "M", "EDUC": 12},
            "use_mmse": False
        })
        self.assertEqual(res5.status_code, 422)

        # 5. Invalid categorical Sex
        res6 = self.client.post("/api/risk/predict", json={
            "profile": {"Age": 70, "Sex": "Other", "EDUC": 12},
            "use_mmse": False
        })
        self.assertEqual(res6.status_code, 422)

        # 6. Out of range MMSE (>30 or <0)
        res7 = self.client.post("/api/risk/predict", json={
            "profile": {"Age": 70, "Sex": "M", "EDUC": 12, "MMSE": 35},
            "use_mmse": True
        })
        self.assertEqual(res7.status_code, 422)

        # 7. Huge payload fuzzing (attempting DoS with 200 unknown fields)
        huge_profile = {"Age": 70, "Sex": "M", "EDUC": 12}
        huge_profile.update({f"fuzz_field_{i}": f"payload_{i}" for i in range(200)})
        res8 = self.client.post("/api/risk/predict", json={"profile": huge_profile, "use_mmse": False})
        self.assertEqual(res8.status_code, 422)

    def test_stateless_no_persistence_and_no_logging(self):
        """Audit test: Confirm no profile data is logged or persisted to DB."""
        unique_canary_age = 79.8765
        payload = {
            "profile": {"Age": unique_canary_age, "Sex": "M", "EDUC": 11, "SES": 3},
            "use_mmse": False
        }

        with connect() as con:
            initial_users = con.execute("SELECT count(*) as c FROM users").fetchone()["c"]
            initial_sessions = con.execute("SELECT count(*) as c FROM sessions").fetchone()["c"]
            initial_attempts = con.execute("SELECT count(*) as c FROM attempts").fetchone()["c"]

        # Capture any log messages via a memory log handler
        log_records = []
        class TestLogHandler(logging.Handler):
            def emit(self, record):
                log_records.append(self.format(record))

        handler = TestLogHandler()
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)

        try:
            res = self.client.post("/api/risk/predict", json=payload)
            self.assertEqual(res.status_code, 200)
        finally:
            root_logger.removeHandler(handler)

        # Confirm DB state is untouched
        with connect() as con:
            final_users = con.execute("SELECT count(*) as c FROM users").fetchone()["c"]
            final_sessions = con.execute("SELECT count(*) as c FROM sessions").fetchone()["c"]
            final_attempts = con.execute("SELECT count(*) as c FROM attempts").fetchone()["c"]

        self.assertEqual(initial_users, final_users)
        self.assertEqual(initial_sessions, final_sessions)
        self.assertEqual(initial_attempts, final_attempts)

        # Confirm canary value never appears in log messages
        for log_msg in log_records:
            self.assertNotIn(str(unique_canary_age), log_msg)

    def test_missing_model_returns_503_gracefully(self):
        """Rate-limit-safe / cold-start: missing model file returns clean 503 without crashing app or games."""
        from fastapi import HTTPException
        with patch("app.risk.get_model", side_effect=HTTPException(status_code=503, detail="Risk screening model 'model_without_mmse' is not available.")):
            res = self.client.post("/api/risk/predict", json={
                "profile": {"Age": 70, "Sex": "M", "EDUC": 12},
                "use_mmse": False
            })
            self.assertEqual(res.status_code, 503)
            self.assertIn("not available", res.json()["detail"])

        # Verify games health check still returns 200
        health_res = self.client.get("/api/health")
        self.assertEqual(health_res.status_code, 200)
        self.assertEqual(health_res.json(), {"ok": True})


if __name__ == "__main__":
    unittest.main()
