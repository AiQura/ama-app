"""
Authentication service for the Streamlit AMA.
"""

import hashlib
import uuid
from typing import Dict, Optional, Any
from dataclasses import dataclass
import sqlite3
from datetime import datetime, timedelta
import streamlit as st

from config.config import SESSION_DURATION_IN_DAYS
from utils.db_conenciton import db_conenciton


@dataclass
class User:
    """User model for authentication."""
    email: str
    user_id: str
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            'email': self.email,
            'user_id': self.user_id,
            'name': self.name
        }


class AuthService:
    """Service for handling authentication and user management."""

    def __init__(self):
        """Initialize the authentication service."""
        self._initialize_db()
        self._initialize_predefined_users()
        self.delete_expired_sessions()

    def _initialize_db(self) -> None:
        """Initialize the SQLite database for authentication."""
        # Connect to the database
        with db_conenciton() as cursor:
            # Create users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT,
                created_at TIMESTAMP NOT NULL
            )
            ''')
            cursor.execute('ALTER TABLE users ENABLE ROW LEVEL SECURITY;')

            # Create sessions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            ''')
            cursor.execute('ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;')

    def _initialize_predefined_users(self) -> None:
        """Initialize predefined users in the database."""
        # Load predefined users from config
        for user_data in st.secrets.auth["PREDEFINED_USERS"]:
            email = user_data['email']
            password = user_data['password']
            name = user_data.get('name', '')

            # Check if user already exists
            with db_conenciton() as cursor:
                cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
                exists = cursor.fetchone()

            if not exists:
                # Add user to database
                self.create_user(email, password, name)

    def _get_salt(self) -> str:
        """Get the salt for password hashing."""
        return st.secrets.auth["AUTH_SALT"]

    def _hash_password(self, password: str) -> str:
        """
        Hash a password with the salt.

        Args:
            password: Plain text password

        Returns:
            str: Hashed password
        """
        salt = self._get_salt()
        salted_password = password + salt
        return hashlib.sha256(salted_password.encode()).hexdigest()

    def create_user(self, email: str, password: str, name: str = "") -> Optional[User]:
        """
        Create a new user.

        Args:
            email: User's email
            password: User's password
            name: User's name (optional)

        Returns:
            Optional[User]: The created user or None if failed
        """
        try:
            user_id = str(uuid.uuid4())
            password_hash = self._hash_password(password)
            created_at = datetime.now().isoformat()

            with db_conenciton() as cursor:
                # Insert user into database
                cursor.execute(
                    "INSERT INTO users (user_id, email, password_hash, name, created_at) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, email, password_hash, name, created_at)
                )

            return User(email=email, user_id=user_id, name=name)
        except sqlite3.IntegrityError:
            # User already exists
            return None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user.

        Args:
            email: User's email
            password: User's password

        Returns:
            Optional[User]: The authenticated user or None if failed
        """
        try:
            password_hash = self._hash_password(password)

            with db_conenciton() as cursor:
                # Find user with matching email and password
                cursor.execute(
                    "SELECT user_id, email, name FROM users WHERE email = %s AND password_hash = %s",
                    (email, password_hash)
                )

                user_data = cursor.fetchone()

            if user_data:
                user_id, email, name = user_data
                return User(email=email, user_id=user_id, name=name)

            return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None

    def create_session(self, user: User) -> Optional[str]:
        """
        Create a new session for a user.

        Args:
            user: The user to create a session for

        Returns:
            Optional[str]: The session ID or None if failed
        """
        try:
            session_id = str(uuid.uuid4())
            created_at = datetime.now().isoformat()
            expires_at = (datetime.now() + timedelta(days=SESSION_DURATION_IN_DAYS)).isoformat()

            with db_conenciton() as cursor:
                # Insert session into database
                cursor.execute(
                    "INSERT INTO sessions (session_id, user_id, created_at, expires_at) VALUES (%s, %s, %s, %s)",
                    (session_id, user.user_id, created_at, expires_at)
                )

            return session_id
        except Exception as e:
            print(f"Error creating session: {e}")
            return None

    def validate_session(self, session_id: str) -> Optional[User]:
        """
        Validate a session and return the associated user.

        Args:
            session_id: The session ID to validate

        Returns:
            Optional[User]: The user associated with the session or None if invalid
        """
        try:
            with db_conenciton() as cursor:
                # Find session and check if it's expired
                cursor.execute(
                    """
                    SELECT s.user_id, u.email, u.name
                    FROM sessions s
                    JOIN users u ON s.user_id = u.user_id
                    WHERE s.session_id = %s AND s.expires_at > %s
                    """,
                    (session_id, datetime.now().isoformat())
                )

                session_data = cursor.fetchone()

            if session_data:
                user_id, email, name = session_data
                return User(email=email, user_id=user_id, name=name)

            return None
        except Exception as e:
            print(f"Error validating session: {e}")
            return None

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: The session ID to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with db_conenciton() as cursor:
                # Delete session from database
                cursor.execute(
                    "DELETE FROM sessions WHERE session_id = %s", (session_id,))

            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False

    def delete_expired_sessions(self) -> bool:
        """
        Delete all expired sessions.

        Args:
            session_id: The session ID to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with db_conenciton() as cursor:
                # Delete session from database
                cursor.execute(
                    "DELETE FROM sessions WHERE expires_at < %s", (datetime.now().isoformat(),))

            return True
        except Exception as e:
            print(f"Error deleting sessions: {e}")
            return False

    def get_user(self, user_id: str) -> Optional[User]:
        """
        Get a user by ID.

        Args:
            user_id: The user ID

        Returns:
            Optional[User]: The user or None if not found
        """
        try:
            with db_conenciton() as cursor:
                # Find user by ID
                cursor.execute(
                    "SELECT user_id, email, name FROM users WHERE user_id = %s",
                    (user_id,)
                )

                user_data = cursor.fetchone()

            if user_data:
                user_id, email, name = user_data
                return User(email=email, user_id=user_id, name=name)

            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.

        Args:
            email: The user's email

        Returns:
            Optional[User]: The user or None if not found
        """
        try:
            with db_conenciton() as cursor:
                # Find user by email
                cursor.execute(
                    "SELECT user_id, email, name FROM users WHERE email = %s",
                    (email,)
                )

                user_data = cursor.fetchone()

            if user_data:
                user_id, email, name = user_data
                return User(email=email, user_id=user_id, name=name)

            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None

    def get_all_user(self) -> list[User]:
        """
        Get all users

        Returns:
            list[User]: List of all users
        """
        try:
            with db_conenciton() as cursor:
                # Find user by ID
                cursor.execute(
                    "SELECT user_id, email, name FROM users"
                )

                rows = cursor.fetchall()

            users = []
            for row in rows:
                user_id, email, name = row
                users.append(User(email=email, user_id=user_id, name=name))

            return users

        except Exception as e:
            print(f"Error getting users: {e}")
            return None
