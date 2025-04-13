"""
Db connection context manager
"""

from contextlib import contextmanager
import sqlite3

from config.config import DB_PATH


@contextmanager
def db_conenciton():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    yield cursor

    conn.commit()
    conn.close()
