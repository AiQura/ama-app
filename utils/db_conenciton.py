"""
Db connection context manager
"""

from contextlib import contextmanager
import psycopg2

import streamlit as st

@st.cache_resource
def get_db_connection():
    return psycopg2.connect(
        database=st.secrets.db["DB_NAME"],
        user=st.secrets.db["DB_USER"],
        password=st.secrets.db["DB_PASSWORD"],
        host=st.secrets.db["DB_HOST"],
        port=st.secrets.db["DB_PORT"]
    )

@contextmanager
def db_conenciton():
    conn = get_db_connection()
    cursor = conn.cursor()

    yield cursor

    conn.commit()
