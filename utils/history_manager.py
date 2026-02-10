"""
SEO Score History Manager
Stores and retrieves scan history using SQLite.
"""

import sqlite3
import os
import json
from datetime import datetime


class HistoryManager:
    """Manages SEO scan history in a SQLite database."""

    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'seo_history.db')
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                score INTEGER NOT NULL,
                grade TEXT,
                category_scores TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def save_scan(self, url, score, grade, category_scores=None):
        """Save a scan result."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO scans (url, score, grade, category_scores, timestamp) VALUES (?, ?, ?, ?, ?)',
            (
                url,
                score,
                grade,
                json.dumps(category_scores) if category_scores else '{}',
                datetime.now().isoformat()
            )
        )
        conn.commit()
        conn.close()

    def get_history(self, url=None, limit=50):
        """Get scan history, optionally filtered by URL."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if url:
            cursor.execute(
                'SELECT * FROM scans WHERE url = ? ORDER BY timestamp DESC LIMIT ?',
                (url, limit)
            )
        else:
            cursor.execute(
                'SELECT * FROM scans ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            )

        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            results.append({
                'id': row['id'],
                'url': row['url'],
                'score': row['score'],
                'grade': row['grade'],
                'category_scores': json.loads(row['category_scores']) if row['category_scores'] else {},
                'timestamp': row['timestamp']
            })
        return results

    def get_trend(self, url, limit=10):
        """Get score trend for a URL (oldest first for charting)."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            'SELECT score, timestamp FROM scans WHERE url = ? ORDER BY timestamp ASC LIMIT ?',
            (url, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        return [{'score': row['score'], 'timestamp': row['timestamp']} for row in rows]

    def clear_history(self):
        """Clear all history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM scans')
        conn.commit()
        conn.close()
