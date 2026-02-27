import sqlite3
import hashlib
from datetime import datetime, timedelta
from dateutil import parser

DB_PATH = "data/agent_registry.db"

class Registry:
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artifacts (
                id TEXT PRIMARY KEY,
                url TEXT,
                source_module TEXT,
                status TEXT DEFAULT 'DISCOVERED',
                raw_content TEXT,
                title TEXT,
                summary TEXT,
                score INTEGER DEFAULT 0,
                relevance_reasoning TEXT,
                strategic_insight TEXT,
                final_post TEXT,
                published_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    def exists(self, uid):
        """Checks if the article ID already exists in the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM artifacts WHERE id = ?", (uid,))
        return cursor.fetchone() is not None
        
    def is_fresh(self, date_obj):
        """Checks if the article date is within the last 30 days"""
        if not date_obj: 
            return True # If no date found, we assume fresh (safer than missing it)
        
        # Normalize timezone to avoid crash
        if date_obj.tzinfo is not None:
             date_obj = date_obj.replace(tzinfo=None)
             
        cutoff = datetime.now() - timedelta(days=30) # 30 Day Window
        return date_obj > cutoff

    def register_artifact(self, url, content, source_module, title="Unknown", pub_date=None):
        """Registers article ONLY if it is fresh (< 30 days) and new."""
        
        # 1. Date Validity Check
        if pub_date and not self.is_fresh(pub_date):
            # We silently skip old stuff to keep logs clean
            return False

        uid = hashlib.sha256(url.encode()).hexdigest()
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO artifacts (id, url, raw_content, source_module, title, published_date, status)
                VALUES (?, ?, ?, ?, ?, ?, 'DISCOVERED')
            ''', (uid, url, content, source_module, title, pub_date))
            self.conn.commit()
            return True # Successfully added
        except sqlite3.IntegrityError:
            return False # Duplicate (already exists)

    def fetch_batch(self, status, limit=10):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM artifacts WHERE status = ? LIMIT ?", (status, limit))
        cols = [description[0] for description in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def update_artifact(self, uid, updates: dict):
        cursor = self.conn.cursor()
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [uid]
        cursor.execute(f"UPDATE artifacts SET {set_clause} WHERE id = ?", values)
        self.conn.commit()
    
    def get_all_scored(self):
        """Helper for your review tool"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM artifacts WHERE score > 0 ORDER BY score DESC")
        cols = [description[0] for description in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]