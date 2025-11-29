"""
Db connection context manager
"""

from contextlib import contextmanager
import psycopg2

import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(st.secrets.supabase["SUPABASE_URL"], st.secrets.supabase["SUPABASE_KEY"])


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
def db_conneciton():
    conn = get_db_connection()
    cursor = conn.cursor()

    yield cursor

    conn.commit()
