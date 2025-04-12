"""
Db connection context manager
"""

from contextlib import contextmanager
import sqlite3

from config.config import AUTH_DB_PATH

@contextmanager
def db_conenciton():
    conn = sqlite3.connect(AUTH_DB_PATH)
    cursor = conn.cursor()

    yield cursor

    conn.commit()
    conn.close()
