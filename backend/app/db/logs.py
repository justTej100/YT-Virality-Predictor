from datetime import datetime, timezone

from app.db.database import get_connection


def log_prediction(video_id: str, title: str, score: float, label: str, model_version: int) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO prediction_log (created_at, video_id, title, viral_potential_score, label, model_version)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (datetime.now(timezone.utc).isoformat(), video_id, title, score, label, model_version),
        )
        conn.commit()


def count_predictions() -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM prediction_log").fetchone()
        return row["c"] if row else 0


def recent_predictions(limit: int = 20) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM prediction_log ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
