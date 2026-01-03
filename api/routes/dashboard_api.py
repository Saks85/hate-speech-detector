from fastapi import APIRouter, Depends
import sqlite3
from datetime import datetime

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])


DB_PATH = "feedback.db"   # adjust if needed


def get_conn():
    return sqlite3.connect(DB_PATH)


@router.get("/stats")
def get_stats():
    conn = get_conn()
    cur = conn.cursor()

    total = cur.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]

    correct = cur.execute("""
        SELECT COUNT(*) FROM feedback WHERE model_label != correct_label
    """).fetchone()[0]

    overrides = cur.execute("""
        SELECT COUNT(*) FROM feedback WHERE applied_override = 1
    """).fetchone()[0]

    conn.close()

    return {
        "total_feedback": total,
        "model_errors": correct,
        "overrides": overrides
    }


@router.get("/list")
def get_feedback_list(limit: int = 200):
    conn = get_conn()
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT id, text, model_label, correct_label, timestamp
        FROM feedback
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,)).fetchall()

    conn.close()

    return [
        {
            "id": r[0],
            "text": r[1],
            "model_label": r[2],
            "correct_label": r[3],
            "timestamp": r[4],
        }
        for r in rows
    ]
