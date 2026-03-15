import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/nagger.db")
DB_PATH.parent.mkdir(exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY, 
                platform TEXT, 
                username TEXT, 
                last_activity_nag TEXT
            );
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                course_code TEXT,
                name TEXT,
                date TEXT,
                weight REAL,
                topics TEXT, -- JSON list
                last_topic_prompt TEXT,
                notified_days TEXT -- JSON list
            );
            CREATE TABLE IF NOT EXISTS pending_quizzes (
                user_id TEXT PRIMARY KEY,
                question TEXT,
                expected_keywords TEXT -- JSON list
            );
        """)

def upsert_user(user_id: str, platform: str, username: str):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO users (id, platform, username) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET username=?",
            (user_id, platform, username, username)
        )

def add_assessment(user_id: str, course_code: str, name: str, date: str, weight: float, topics: list):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO assessments (user_id, course_code, name, date, weight, topics, notified_days) VALUES (?, ?, ?, ?, ?, ?, '[]')",
            (user_id, course_code, name, date, weight, json.dumps(topics))
        )

def get_user_assessments(user_id: str):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM assessments WHERE user_id = ? ORDER BY date ASC", (user_id,)).fetchall()
        return [dict(r) for r in rows]

def get_all_assessments():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM assessments ORDER BY date ASC").fetchall()
        return [dict(r) for r in rows]

def set_pending_quiz(user_id: str, question: str, expected_keywords: list):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO pending_quizzes (user_id, question, expected_keywords) VALUES (?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET question=?, expected_keywords=?",
            (user_id, question, json.dumps(expected_keywords), question, json.dumps(expected_keywords))
        )

def get_pending_quiz(user_id: str):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM pending_quizzes WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None

def clear_pending_quiz(user_id: str):
    with get_db() as conn:
        conn.execute("DELETE FROM pending_quizzes WHERE user_id = ?", (user_id,))
        
def update_assessment_topics(assessment_id: int, topics: list):
    with get_db() as conn:
        conn.execute("UPDATE assessments SET topics = ? WHERE id = ?", (json.dumps(topics), assessment_id))

def update_notified_days(assessment_id: int, notified_days: list):
     with get_db() as conn:
        conn.execute("UPDATE assessments SET notified_days = ? WHERE id = ?", (json.dumps(notified_days), assessment_id))

def update_last_topic_prompt(assessment_id: int):
     with get_db() as conn:
        conn.execute("UPDATE assessments SET last_topic_prompt = ? WHERE id = ?", (datetime.utcnow().isoformat(), assessment_id))
