import sqlite3
from typing import Any

DB_PATH = "paynsnap.db"

class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            purchases INTEGER DEFAULT 0,
            last_purchase TIMESTAMP
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bans (
            username TEXT PRIMARY KEY
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stores (
            username TEXT PRIMARY KEY
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_ops (
            block_num INTEGER,
            op_id TEXT,
            PRIMARY KEY (block_num, op_id)
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_num INTEGER,
            op_id TEXT,
            username TEXT,
            amount REAL,
            memo TEXT,
            snap_permlink TEXT,
            paid INTEGER,
            reason TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()

    def add_user(self, username: str):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (username,))
        self.conn.commit()

    def ban_user(self, username: str):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO bans (username) VALUES (?)", (username,))
        self.conn.commit()

    def is_banned(self, username: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM bans WHERE username = ?", (username,))
        return cursor.fetchone() is not None

    # ...additional methods for stores, ops, purchases...

db = Database()
