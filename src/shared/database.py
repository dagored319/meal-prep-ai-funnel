"""Database models and setup for the Organic Funnel Agent."""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from pathlib import Path
import json


class Database:
    """SQLite database manager for the funnel system."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    @contextmanager
    def get_connection(self):
        """Get a database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _init_database(self):
        """Initialize database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Trends table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    summary TEXT,
                    raw_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    used_for_content BOOLEAN DEFAULT 0
                )
            """)

            # Content table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trend_id INTEGER,
                    script TEXT NOT NULL,
                    video_path TEXT,
                    status TEXT DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    published_at TIMESTAMP,
                    FOREIGN KEY (trend_id) REFERENCES trends(id)
                )
            """)

            # Leads table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    preferences TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    subscription_status TEXT DEFAULT 'free',
                    subscription_start TIMESTAMP
                )
            """)

            # Conversations table (for chatbot)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id INTEGER,
                    session_id TEXT NOT NULL,
                    messages TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (lead_id) REFERENCES leads(id)
                )
            """)

            # Meal plans table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meal_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id INTEGER NOT NULL,
                    plan_type TEXT DEFAULT 'free',
                    plan_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sent_at TIMESTAMP,
                    FOREIGN KEY (lead_id) REFERENCES leads(id)
                )
            """)

            conn.commit()

    # Trend methods
    def save_trend(self, source: str, topic: str, summary: str, raw_data: Dict[str, Any]) -> int:
        """Save a detected trend."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO trends (source, topic, summary, raw_data) VALUES (?, ?, ?, ?)",
                (source, topic, summary, json.dumps(raw_data))
            )
            return cursor.lastrowid

    def get_unused_trends(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get trends that haven't been used for content yet."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM trends WHERE used_for_content = 0 ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def mark_trend_used(self, trend_id: int):
        """Mark a trend as used for content."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE trends SET used_for_content = 1 WHERE id = ?", (trend_id,))

    # Content methods
    def save_content(self, trend_id: Optional[int], script: str, video_path: Optional[str] = None) -> int:
        """Save generated content."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO content (trend_id, script, video_path) VALUES (?, ?, ?)",
                (trend_id, script, video_path)
            )
            return cursor.lastrowid

    def update_content_status(self, content_id: int, status: str, published_at: Optional[datetime] = None):
        """Update content status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if published_at:
                cursor.execute(
                    "UPDATE content SET status = ?, published_at = ? WHERE id = ?",
                    (status, published_at, content_id)
                )
            else:
                cursor.execute(
                    "UPDATE content SET status = ? WHERE id = ?",
                    (status, content_id)
                )

    # Lead methods
    def save_lead(self, email: str, name: Optional[str] = None, preferences: Optional[Dict] = None) -> int:
        """Save a new lead."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO leads (email, name, preferences) VALUES (?, ?, ?)",
                    (email, name, json.dumps(preferences) if preferences else None)
                )
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Lead already exists, get their ID
                cursor.execute("SELECT id FROM leads WHERE email = ?", (email,))
                return cursor.fetchone()[0]

    def get_lead(self, email: str) -> Optional[Dict[str, Any]]:
        """Get lead by email."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM leads WHERE email = ?", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_subscription(self, lead_id: int, status: str):
        """Update lead's subscription status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE leads SET subscription_status = ?, subscription_start = ? WHERE id = ?",
                (status, datetime.now() if status == 'premium' else None, lead_id)
            )

    # Conversation methods
    def save_conversation(self, session_id: str, messages: List[Dict], lead_id: Optional[int] = None):
        """Save or update a conversation."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM conversations WHERE session_id = ?", (session_id,))
            existing = cursor.fetchone()

            if existing:
                cursor.execute(
                    "UPDATE conversations SET messages = ?, lead_id = ?, updated_at = ? WHERE session_id = ?",
                    (json.dumps(messages), lead_id, datetime.now(), session_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO conversations (session_id, messages, lead_id) VALUES (?, ?, ?)",
                    (session_id, json.dumps(messages), lead_id)
                )

    def get_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation by session ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM conversations WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['messages'] = json.loads(result['messages'])
                return result
            return None

    # Meal plan methods
    def save_meal_plan(self, lead_id: int, plan_type: str, plan_data: Dict[str, Any]) -> int:
        """Save a generated meal plan."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO meal_plans (lead_id, plan_type, plan_data) VALUES (?, ?, ?)",
                (lead_id, plan_type, json.dumps(plan_data))
            )
            return cursor.lastrowid

    def mark_plan_sent(self, plan_id: int):
        """Mark a meal plan as sent."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE meal_plans SET sent_at = ? WHERE id = ?",
                (datetime.now(), plan_id)
            )
