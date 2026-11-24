"""CO CARE backend API (FastAPI).

Run:  uvicorn app.main:app --reload --port 8000   (from the backend folder)
Docs: http://localhost:8000/docs
"""
import csv
import io
import json
import os
from contextlib import asynccontextmanager
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import adaptive
from .content import load_items
from .db import connect, init_db

@asynccontextmanager
async def lifespan(_app):
    init_db()
    yield


app = FastAPI(title="CO CARE API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Lang = Literal["or", "en"]
Version = Literal["localized", "generic"]
Mode = Literal["adaptive", "fixed"]
Game = Literal["memory_match", "picture_recall", "find_it"]


# ---------- request bodies ----------
class UserIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    age: Optional[int] = Field(default=None, ge=40, le=120)
    lang: Lang = "or"
    consent_given: bool
    content_version: Version = "localized"
    difficulty_mode: Mode = "adaptive"


class UserPatch(BaseModel):
    lang: Optional[Lang] = None
    content_version: Optional[Version] = None
    difficulty_mode: Optional[Mode] = None


class SessionIn(BaseModel):
    user_id: int
    game: Game


class AttemptIn(BaseModel):
    round_no: int = 1
    item_id: Optional[str] = None
    correct: bool
    response_ms: int = Field(ge=0, le=600000)
    error_type: Optional[str] = None


class EndIn(BaseModel):
    completed: bool


# ---------- helpers ----------
def _user(con, user_id: int) -> dict:
    row = con.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        raise HTTPException(404, "user not found")
    return dict(row)


def _level(con, user_id: int, game: str) -> int:
    row = con.execute("SELECT level FROM user_levels WHERE user_id = ? AND game = ?", (user_id, game)).fetchone()
    return row["level"] if row else 1


# ---------- routes ----------
@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/games")
def games():
    return {g: {"levels": adaptive.GAME_LEVELS[g], "thresholds": adaptive.THRESHOLDS[g]} for g in adaptive.GAME_LEVELS}


@app.post("/api/users")
def create_user(body: UserIn):
    if not body.consent_given:
        raise HTTPException(400, "consent is required before playing")
    with connect() as con:
        cur = con.execute(
            "INSERT INTO users (name, age, lang, consent_given, content_version, difficulty_mode) VALUES (?,?,?,?,?,?)",
            (body.name.strip(), body.age, body.lang, 1, body.content_version, body.difficulty_mode),
        )
        return _user(con, cur.lastrowid)


@app.get("/api/users")
def list_users():
    with connect() as con:
        return [dict(r) for r in con.execute("SELECT * FROM users ORDER BY id")]


@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    with connect() as con:
        u = _user(con, user_id)
        u["levels"] = {g: _level(con, user_id, g) for g in adaptive.GAME_LEVELS}
        return u


@app.patch("/api/users/{user_id}")
def update_user(user_id: int, body: UserPatch):
    changes = body.model_dump(exclude_none=True)
    with connect() as con:
        _user(con, user_id)
        for col, val in changes.items():
            con.execute(f"UPDATE users SET {col} = ? WHERE id = ?", (val, user_id))
        return _user(con, user_id)


@app.post("/api/sessions")
def start_session(body: SessionIn):
    with connect() as con:
        u = _user(con, body.user_id)
        level = _level(con, body.user_id, body.game)
        cur = con.execute(
            "INSERT INTO sessions (user_id, game, level, lang, content_version, difficulty_mode) VALUES (?,?,?,?,?,?)",
            (u["id"], body.game, level, u["lang"], u["content_version"], u["difficulty_mode"]),
        )
        return {
            "session_id": cur.lastrowid,
            "game": body.game,
            "level": level,
            "params": adaptive.params_for(body.game, level),
            "lang": u["lang"],
            "content_version": u["content_version"],
            "items": load_items(u["content_version"]),
        }


@app.post("/api/sessions/{session_id}/attempts")
def log_attempt(session_id: int, body: AttemptIn):
    with connect() as con:
        s = con.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not s:
            raise HTTPException(404, "session not found")
        if s["completed"] is not None:
            raise HTTPException(409, "session already ended")
        con.execute(
            "INSERT INTO attempts (session_id, round_no, item_id, correct, response_ms, error_type) VALUES (?,?,?,?,?,?)",
            (session_id, body.round_no, body.item_id, int(body.correct), body.response_ms, body.error_type),
        )
    return {"ok": True}


@app.post("/api/sessions/{session_id}/end")
def end_session(session_id: int, body: EndIn):
    with connect() as con:
        s = con.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not s:
            raise HTTPException(404, "session not found")
        if s["completed"] is not None:
            raise HTTPException(409, "session already ended")
        attempts = [dict(a) for a in con.execute("SELECT correct, response_ms FROM attempts WHERE session_id = ?", (session_id,))]
        m = adaptive.compute_metrics(attempts, body.completed)
        d = adaptive.decide(s["game"], s["level"], m, s["difficulty_mode"])

        con.execute(
            "UPDATE sessions SET ended_at = datetime('now'), completed = ?, accuracy = ?, median_rt_ms = ?, n_attempts = ? WHERE id = ?",
            (int(body.completed), m.accuracy, m.median_rt_ms, m.n_attempts, session_id),
        )
        con.execute(
            "INSERT INTO user_levels (user_id, game, level) VALUES (?,?,?) "
            "ON CONFLICT(user_id, game) DO UPDATE SET level = excluded.level",
            (s["user_id"], s["game"], d.new_level),
        )
        con.execute(
            "INSERT INTO adaptation_log (user_id, session_id, game, old_level, new_level, rule, reason, metrics_json) VALUES (?,?,?,?,?,?,?,?)",
            (s["user_id"], session_id, s["game"], d.old_level, d.new_level, d.rule, d.reason, json.dumps(m.__dict__)),
        )
        return {"metrics": m.__dict__, "decision": adaptive.decision_dict(d)}


@app.get("/api/users/{user_id}/history")
def history(user_id: int):
    with connect() as con:
        _user(con, user_id)
        sessions = [dict(r) for r in con.execute(
            "SELECT s.*, a.old_level, a.new_level, a.rule, a.reason FROM sessions s "
            "LEFT JOIN adaptation_log a ON a.session_id = s.id "
            "WHERE s.user_id = ? AND s.completed IS NOT NULL ORDER BY s.id DESC", (user_id,))]
        return {"sessions": sessions, "levels": {g: _level(con, user_id, g) for g in adaptive.GAME_LEVELS}}


EXPORTABLE = ("users", "sessions", "attempts", "adaptation_log")


@app.get("/api/export/{table}.csv")
def export_csv(table: str):
    """Download raw data for analysis in Excel / Python."""
    if table not in EXPORTABLE:
        raise HTTPException(404, "unknown table")
    with connect() as con:
        cur = con.execute(f"SELECT * FROM {table}")
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow([c[0] for c in cur.description])
        w.writerows(cur.fetchall())
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": f"attachment; filename={table}.csv"})



# ---------- Risk Screening (ML) Module ----------
from .risk import router as risk_router
app.include_router(risk_router)
# ------------------------------------------------


# ---------- serve the built frontend (after `npm run build`) ----------
DIST = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.isdir(DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST, "assets")), name="assets")

    @app.get("/{path:path}")
    def spa(path: str):
        f = os.path.join(DIST, path)
        return FileResponse(f if path and os.path.isfile(f) else os.path.join(DIST, "index.html"))
