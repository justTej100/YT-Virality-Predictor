import sqlite3
from contextlib import contextmanager

from app.core.config import DB_PATH


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS prediction_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                video_id TEXT NOT NULL,
                title TEXT,
                viral_potential_score REAL,
                label TEXT,
                model_version INTEGER
            )
            """
        )
        conn.commit()


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
