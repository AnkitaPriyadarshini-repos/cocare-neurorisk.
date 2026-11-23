"""SQLite database setup. One file, no ORM, so it is easy to read and explain in the report."""
import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.environ.get("COCARE_DB", os.path.join(os.path.dirname(__file__), "..", "cocare.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL,
    age              INTEGER,
    lang             TEXT NOT NULL DEFAULT 'or',          -- 'or' (Odia) or 'en' (English fallback)
    content_version  TEXT NOT NULL DEFAULT 'localized',   -- 'localized' or 'generic'  (study condition)
    difficulty_mode  TEXT NOT NULL DEFAULT 'adaptive',    -- 'adaptive' or 'fixed'     (study condition)
    consent_given    INTEGER NOT NULL DEFAULT 0,
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Current difficulty level per user per game (1 = easiest, 5 = hardest)
CREATE TABLE IF NOT EXISTS user_levels (
    user_id  INTEGER NOT NULL REFERENCES users(id),
    game     TEXT NOT NULL,
    level    INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (user_id, game)
);

-- One row per game played
CREATE TABLE IF NOT EXISTS sessions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL REFERENCES users(id),
    game             TEXT NOT NULL,
    level            INTEGER NOT NULL,
    lang             TEXT NOT NULL,
    content_version  TEXT NOT NULL,
    difficulty_mode  TEXT NOT NULL,
    started_at       TEXT NOT NULL DEFAULT (datetime('now')),
    ended_at         TEXT,
    completed        INTEGER,            -- 1 finished, 0 abandoned, NULL still running
    accuracy         REAL,
    median_rt_ms     REAL,
    n_attempts       INTEGER
);

-- One row per user response (tap / flip / selection)
CREATE TABLE IF NOT EXISTS attempts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id   INTEGER NOT NULL REFERENCES sessions(id),
    round_no     INTEGER NOT NULL DEFAULT 1,
    item_id      TEXT,
    correct      INTEGER NOT NULL,
    response_ms  INTEGER NOT NULL,
    error_type   TEXT,                   -- e.g. 'wrong_item', 'timeout', 'mismatch'
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Every difficulty decision, with the rule and the numbers behind it (explainability)
CREATE TABLE IF NOT EXISTS adaptation_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL REFERENCES users(id),
    session_id   INTEGER NOT NULL REFERENCES sessions(id),
    game         TEXT NOT NULL,
    old_level    INTEGER NOT NULL,
    new_level    INTEGER NOT NULL,
    rule         TEXT NOT NULL,
    reason       TEXT NOT NULL,
    metrics_json TEXT NOT NULL,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def init_db(path: str | None = None) -> None:
    with connect(path) as con:
        con.executescript(SCHEMA)


@contextmanager
def connect(path: str | None = None):
    con = sqlite3.connect(path or DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
        con.commit()
    finally:
        con.close()
