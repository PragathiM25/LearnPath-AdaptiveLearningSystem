
import sqlite3
from contextlib import contextmanager
from .config import DATABASE_PATH


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def get_db():
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            stored_path TEXT NOT NULL,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            topic TEXT NOT NULL,
            question TEXT NOT NULL,
            correct INTEGER NOT NULL,
            difficulty TEXT DEFAULT 'medium',
            response_seconds REAL DEFAULT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)


def save_document(filename: str, stored_path: str) -> int:
    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO documents(filename, stored_path) VALUES (?, ?)",
            (filename, stored_path),
        )
        return cursor.lastrowid


def list_documents():
    with get_db() as db:
        rows = db.execute(
            "SELECT id, filename, uploaded_at FROM documents "
            "ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def save_attempt(
    student_id: str,
    topic: str,
    question: str,
    correct: bool,
    difficulty: str = "medium",
    response_seconds: float | None = None,
):
    with get_db() as db:
        db.execute(
            """INSERT INTO quiz_attempts
            (student_id, topic, question, correct, difficulty,
             response_seconds)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (
                student_id,
                topic,
                question,
                int(correct),
                difficulty,
                response_seconds,
            ),
        )


def get_attempts(student_id: str):
    with get_db() as db:
        rows = db.execute(
            """SELECT topic, question, correct, difficulty,
                      response_seconds, created_at
               FROM quiz_attempts
               WHERE student_id = ?
               ORDER BY id ASC""",
            (student_id,),
        ).fetchall()
        return [dict(row) for row in rows]
