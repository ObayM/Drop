import sqlite3
import os
import string
import random
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dropzone.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            size INTEGER NOT NULL,
            mimetype TEXT,
            upload_date TEXT NOT NULL,
            downloads INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def generate_code(length=6):
    chars = string.ascii_lowercase + string.digits
    conn = get_db()
    while True:
        code = ''.join(random.choices(chars, k=length))
        row = conn.execute('SELECT id FROM files WHERE code = ?', (code,)).fetchone()
        if row is None:
            conn.close()
            return code

def save_file(filename, original_name, code, size, mimetype):
    conn = get_db()
    conn.execute(
        'INSERT INTO files (filename, original_name, code, size, mimetype, upload_date) VALUES (?, ?, ?, ?, ?, ?)',
        (filename, original_name, code, size, mimetype, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_file_by_code(code):
    conn = get_db()
    row = conn.execute('SELECT * FROM files WHERE code = ?', (code,)).fetchone()
    conn.close()
    return dict(row) if row else None

def increment_downloads(code):
    conn = get_db()
    conn.execute('UPDATE files SET downloads = downloads + 1 WHERE code = ?', (code,))
    conn.commit()
    conn.close()
