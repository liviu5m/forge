import sqlite3
import json
from typing import List, Dict, Any

DB_FILE = "agent_sessions.db"


def init_db():
    """Initializes the SQLite database and creates the sessions table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            history TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_session(session_id: str, history: List[Dict[str, Any]]):
    """Saves or updates the conversation history for a given session ID."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    serialized_history = []
    for msg in history:
        if hasattr(msg, "model_dump"):
            model_dump_method = getattr(msg, "model_dump", None)
            serialized_history.append(model_dump_method)
        elif isinstance(msg, dict):
            clean_msg = {k: v for k, v in msg.items() if k not in ["function"]}
            serialized_history.append(clean_msg)
        else:
            serialized_history.append(
                dict(msg) if hasattr(msg, "__iter__") else str(msg)
            )

    cursor.execute(
        """
        INSERT INTO sessions (session_id, history, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(session_id) DO UPDATE SET
            history = excluded.history,
            updated_at = CURRENT_TIMESTAMP
    """,
        (session_id, json.dumps(serialized_history)),
    )

    conn.commit()
    conn.close()


def load_session(session_id: str) -> List[Dict[str, Any]]:
    """Loads past conversation history for a given session ID."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT history FROM sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()

    if row and row[0]:
        return json.loads(row[0])
    return []


def list_sessions() -> List[str]:
    """Lists all available saved session IDs."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT session_id FROM sessions ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    conn.close()

    return [row[0] for row in rows]
