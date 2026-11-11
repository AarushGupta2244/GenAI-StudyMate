import sqlite3
import os
from datetime import datetime
from config import DATABASE_PATH


def get_connection():
    """Create a database connection."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """Create all required database tables."""

    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS study_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature TEXT NOT NULL,
                title TEXT NOT NULL,
                input_text TEXT,
                output_text TEXT,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                total_questions INTEGER NOT NULL,
                correct_answers INTEGER NOT NULL,
                score REAL NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        conn.commit()


def save_study_history(feature, title, input_text, output_text):
    """Save generated study content."""

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO study_history
            (feature, title, input_text, output_text, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            feature,
            title,
            input_text,
            output_text,
            datetime.now().isoformat()
        ))

        conn.commit()


def save_chat_message(session_id, role, message):
    """Save a chat message."""

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO chat_history
            (session_id, role, message, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            session_id,
            role,
            message,
            datetime.now().isoformat()
        ))

        conn.commit()


def get_study_history(limit=100):
    """Retrieve recent study history."""

    with get_connection() as conn:
        return conn.execute("""
            SELECT * FROM study_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()


def get_chat_history(session_id):
    """Retrieve messages from a chat session."""

    with get_connection() as conn:
        return conn.execute("""
            SELECT * FROM chat_history
            WHERE session_id = ?
            ORDER BY id ASC
        """, (session_id,)).fetchall()


def save_quiz_result(topic, total_questions, correct_answers):
    """Save quiz performance."""

    score = (
        (correct_answers / total_questions) * 100
        if total_questions > 0 else 0
    )

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO quiz_results
            (topic, total_questions, correct_answers, score, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            topic,
            total_questions,
            correct_answers,
            score,
            datetime.now().isoformat()
        ))

        conn.commit()


def get_quiz_results(limit=50):
    """Retrieve recent quiz results."""

    with get_connection() as conn:
        return conn.execute("""
            SELECT * FROM quiz_results
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()