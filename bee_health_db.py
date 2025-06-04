import sqlite3
import datetime
import os
import time
from email_service import EmailService

# Register datetime adapter/converter to avoid deprecation warnings in Python 3.12+
sqlite3.register_adapter(datetime.datetime, lambda val: val.isoformat())
sqlite3.register_converter("timestamp", lambda val: datetime.datetime.fromisoformat(val.decode("utf-8")))

class BeeHealthDatabase:
    def __init__(self, db_path="bee_health.db"):
        self.db_path = db_path
        self.create_tables_if_not_exist()
        self.current_session_id = None
        self.email_service = EmailService()

    def _connect(self):
        return sqlite3.connect(
            self.db_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )

    def create_tables_if_not_exist(self):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            source VARCHAR(255) NOT NULL DEFAULT 'default',
            notes TEXT,
            email_sent BOOLEAN DEFAULT 0
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bee_metrics (
            metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            unique_bee_count INTEGER NOT NULL,
            unique_varroa_count INTEGER NOT NULL,
            infestation_ratio REAL NOT NULL,
            frame_count INTEGER NOT NULL,
            fps REAL,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bee_metrics_session_id ON bee_metrics(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bee_metrics_timestamp ON bee_metrics(timestamp)')

        conn.commit()
        conn.close()

    def start_new_session(self, source="default", notes=""):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO sessions (start_time, source, notes) VALUES (?, ?, ?)',
            (datetime.datetime.now(), source, notes)
        )
        self.current_session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.current_session_id

    def end_session(self, session_id=None):
        if session_id is None:
            session_id = self.current_session_id
        if session_id is None:
            return False

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE sessions SET end_time = ? WHERE session_id = ?',
            (datetime.datetime.now(), session_id)
        )
        conn.commit()
        try:
            email_sent = self.email_service.send_session_summary(session_id, self.db_path)
            if email_sent:
                cursor.execute(
                    'UPDATE sessions SET email_sent = 1 WHERE session_id = ?',
                    (session_id,)
                )
                conn.commit()
                print(f"Email sent for session {session_id}")
            else:
                print(f"Email not sent for session {session_id}")
        except Exception as e:
            print(f"Error sending email: {e}")
        conn.close()
        if session_id == self.current_session_id:
            self.current_session_id = None
        return True

    def save_metrics(self, unique_bee_count, unique_varroa_count, frame_count, fps=None, session_id=None):
        if session_id is None:
            session_id = self.current_session_id
        if session_id is None:
            session_id = self.start_new_session()

        infestation_ratio = (
            unique_varroa_count / unique_bee_count if unique_bee_count > 0 else 0
        )

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO bee_metrics (session_id, timestamp, unique_bee_count, unique_varroa_count, infestation_ratio, frame_count, fps) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (session_id, datetime.datetime.now(), unique_bee_count, unique_varroa_count, infestation_ratio, frame_count, fps)
        )
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def get_latest_metrics(self, limit=10, session_id=None):
        conn = self._connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if session_id:
            cursor.execute(
                'SELECT * FROM bee_metrics WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?',
                (session_id, limit)
            )
        else:
            cursor.execute(
                'SELECT * FROM bee_metrics ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            )
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_sessions(self, limit=10):
        conn = self._connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM sessions ORDER BY start_time DESC LIMIT ?',
            (limit,)
        )
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
