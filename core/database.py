"""
Background SQLite Database Manager for the AI Helper Chatbot.
Provides zero-configuration, thread-safe, local persistence for:
- Chat sessions and full message history
- Persona & Model preferences
- Hardware usage telemetry (VRAM footprint)
"""

import sqlite3
import os
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default to data/chatbot.db inside the project folder
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, "chatbot.db")
        else:
            self.db_path = db_path

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Creates a connection with row factory and foreign keys enabled."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")  # Fast concurrent reads/writes
        return conn

    def _init_db(self):
        """Initializes tables and indexes if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    persona TEXT,
                    model TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    model TEXT,
                    vram_mb REAL,
                    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
                )
            """)

            # Settings / Key-Value store
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            # Indexes for lightning-fast retrieval
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_updated ON sessions(updated_at DESC)")
            conn.commit()

    # --- Session Management ---

    def create_session(self, title: str = "New Conversation", persona: str = "", model: str = "") -> str:
        """Creates a new chat session and returns its ID."""
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO sessions (id, title, persona, model, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (session_id, title, persona, model, now, now)
            )
            conn.commit()
        return session_id

    def get_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns all sessions ordered by most recently updated."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT id, title, persona, model, created_at, updated_at FROM sessions ORDER BY updated_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Returns a single session by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT id, title, persona, model, created_at, updated_at FROM sessions WHERE id = ?",
                (session_id,)
            ).fetchone()
            return dict(row) if row else None

    def update_session_title(self, session_id: str, new_title: str):
        """Updates the title of a session."""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?",
                (new_title, now, session_id)
            )
            conn.commit()

    def touch_session(self, session_id: str):
        """Updates the updated_at timestamp of a session."""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            conn.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (now, session_id))
            conn.commit()

    def delete_session(self, session_id: str):
        """Deletes a session and its associated messages."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()

    # --- Message Management ---

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        model: Optional[str] = None,
        vram_mb: Optional[float] = None
    ) -> str:
        """Stores a new message in the database and updates session timestamp."""
        msg_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO messages (id, session_id, role, content, timestamp, model, vram_mb)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (msg_id, session_id, role, content, now, model, vram_mb)
            )
            conn.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (now, session_id))
            conn.commit()
        return msg_id

    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieves all messages for a session in chronological order."""
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, session_id, role, content, timestamp, model, vram_mb
                FROM messages
                WHERE session_id = ?
                ORDER BY timestamp ASC
                """,
                (session_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    def search_messages(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Searches message contents across all sessions."""
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT m.id, m.session_id, m.role, m.content, m.timestamp, s.title as session_title
                FROM messages m
                JOIN sessions s ON m.session_id = s.id
                WHERE m.content LIKE ?
                ORDER BY m.timestamp DESC
                LIMIT ?
                """,
                (f"%{query}%", limit)
            ).fetchall()
            return [dict(r) for r in rows]

    # --- Settings Key-Value Store ---

    def set_setting(self, key: str, value: Any):
        """Saves a user preference or config setting."""
        val_str = json.dumps(value) if not isinstance(value, str) else value
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, val_str)
            )
            conn.commit()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Retrieves a setting by key."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
            if not row:
                return default
            val_str = row["value"]
            try:
                return json.loads(val_str)
            except Exception:
                return val_str

    # --- Export Utilities ---

    def export_session_markdown(self, session_id: str) -> str:
        """Exports a full session history as a formatted Markdown document."""
        session = self.get_session(session_id)
        if not session:
            return ""
        messages = self.get_messages(session_id)
        
        md = f"# {session['title']}\n"
        md += f"*Date: {session['created_at']} | Model: {session.get('model', 'Default')} | Persona: {session.get('persona', 'General')}*\n\n---\n\n"
        
        for msg in messages:
            speaker = "👤 User" if msg["role"] == "user" else "🤖 AI Helper"
            vram_tag = f" `[{msg['vram_mb']} MB VRAM]`" if msg.get("vram_mb") else ""
            md += f"### {speaker}{vram_tag}\n\n{msg['content']}\n\n---\n\n"
        
        return md

if __name__ == "__main__":
    db = DatabaseManager()
    sid = db.create_session("Test Session", "General Helper", "qwen2.5:0.5b")
    db.add_message(sid, "user", "What is the capital of France?")
    db.add_message(sid, "assistant", "The capital of France is Paris.", model="qwen2.5:0.5b", vram_mb=574.0)
    print("Sessions:", len(db.get_sessions()))
    print("Messages count:", len(db.get_messages(sid)))
    print("Database test passed successfully!")
