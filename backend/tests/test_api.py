import os
import tempfile

os.environ["COCARE_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")

from fastapi.testclient import TestClient  # noqa: E402

from app import adaptive  # noqa: E402
from app.main import app  # noqa: E402


def M(acc, rt, completed=True, n=10):
    return adaptive.Metrics(n, acc, rt, completed)


def test_rules():
    assert adaptive.decide("find_it", 2, M(0.9, 3000)).rule == "R4_HIGH_PERFORMANCE"
    assert adaptive.decide("find_it", 2, M(0.9, 3000)).new_level == 3
    assert adaptive.decide("find_it", 2, M(0.3, 3000)).new_level == 1
    assert adaptive.decide("find_it", 2, M(0.6, 12000)).rule == "R3_STRUGGLING"
    assert adaptive.decide("find_it", 2, M(0.9, 3000, completed=False)).rule == "R1_ABANDONED"
    assert adaptive.decide("find_it", 3, M(0.7, 5000)).new_level == 3
    assert adaptive.decide("find_it", 5, M(1.0, 1000)).new_level == 5
    assert adaptive.decide("find_it", 1, M(0.0, 1000)).new_level == 1
    assert adaptive.decide("find_it", 2, M(1.0, 1000), mode="fixed").new_level == 2


def test_full_flow():
    with TestClient(app) as c:
        assert c.post("/api/users", json={"name": "Test", "consent_given": False}).status_code == 400
        u = c.post("/api/users", json={"name": "Test", "age": 70, "consent_given": True}).json()
        assert u["lang"] == "or" and u["content_version"] == "localized"

        s = c.post("/api/sessions", json={"user_id": u["id"], "game": "find_it"}).json()
        assert s["level"] == 1 and s["params"]["grid_size"] == 4 and len(s["items"]) >= 16
        for _ in range(5):
            c.post(f"/api/sessions/{s['session_id']}/attempts", json={"correct": True, "response_ms": 2000, "item_id": "loc_mango"})
        r = c.post(f"/api/sessions/{s['session_id']}/end", json={"completed": True}).json()
        assert r["decision"]["new_level"] == 2 and r["decision"]["message_key"] == "level_up"

        s2 = c.post("/api/sessions", json={"user_id": u["id"], "game": "find_it"}).json()
        assert s2["level"] == 2

        c.patch(f"/api/users/{u['id']}", json={"content_version": "generic", "lang": "en"})
        s3 = c.post("/api/sessions", json={"user_id": u["id"], "game": "memory_match"}).json()
        assert s3["content_version"] == "generic" and s3["items"][0]["id"].startswith("gen_")

        h = c.get(f"/api/users/{u['id']}/history").json()
        assert h["levels"]["find_it"] == 2 and h["sessions"][0]["rule"] == "R4_HIGH_PERFORMANCE"
        assert c.get("/api/export/attempts.csv").text.startswith("id,session_id")
