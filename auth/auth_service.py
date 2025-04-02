"""
Authentication service for the Streamlit AMA.
"""
import os
import json
import hashlib
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import sqlite3
from datetime import datetime, timedelta

from config.config import AUTH_DB_PATH, SALT_FILE_PATH, PREDEFINED_USERS


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
        self._initialize_salt()
        self._initialize_predefined_users()

    def _initialize_db(self) -> None:
        """Initialize the SQLite database for authentication."""
        # Ensure the directory exists
        os.makedirs(os.path.dirname(AUTH_DB_PATH), exist_ok=True)

        # Connect to the database
        conn = sqlite3.connect(AUTH_DB_PATH)
        cursor = conn.cursor()

        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT,
            created_at TEXT NOT NULL
        )
        ''')

        # Create sessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')

        conn.commit()
        conn.close()

    def _initialize_salt(self) -> None:
        """Initialize the salt for password hashing."""
        if not os.path.exists(SALT_FILE_PATH):
            # Create a random salt
            salt = os.urandom(32).hex()

            # Save the salt to a file
            with open(SALT_FILE_PATH, 'w') as f:
                f.write(salt)

    def _initialize_predefined_users(self) -> None:
        """Initialize predefined users in the database."""
        # Load predefined users from config
        for user_data in PREDEFINED_USERS:
            email = user_data['email']
            password = user_data['password']
            name = user_data.get('name', '')

            # Check if user already exists
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
            exists = cursor.fetchone()
            conn.close()

            if not exists:
                # Add user to database
                self.create_user(email, password, name)

    def _get_salt(self) -> str:
        """Get the salt for password hashing."""
        with open(SALT_FILE_PATH, 'r') as f:
            return f.read()

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

            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            # Insert user into database
            cursor.execute(
                "INSERT INTO users (user_id, email, password_hash, name, created_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, email, password_hash, name, created_at)
            )

            conn.commit()
            conn.close()

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

            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            # Find user with matching email and password
            cursor.execute(
                "SELECT user_id, email, name FROM users WHERE email = ? AND password_hash = ?",
                (email, password_hash)
            )

            user_data = cursor.fetchone()
            conn.close()

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
            expires_at = (datetime.now() + timedelta(days=7)).isoformat()

            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            # Insert session into database
            cursor.execute(
                "INSERT INTO sessions (session_id, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
                (session_id, user.user_id, created_at, expires_at)
            )

            conn.commit()
            conn.close()

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
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            # Find session and check if it's expired
            cursor.execute(
                """
                SELECT s.user_id, u.email, u.name
                FROM sessions s
                JOIN users u ON s.user_id = u.user_id
                WHERE s.session_id = ? AND s.expires_at > ?
                """,
                (session_id, datetime.now().isoformat())
            )

            session_data = cursor.fetchone()
            conn.close()

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
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            # Delete session from database
            cursor.execute(
                "DELETE FROM sessions WHERE session_id = ?", (session_id,))

            conn.commit()
            conn.close()

            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
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
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            # Find user by ID
            cursor.execute(
                "SELECT user_id, email, name FROM users WHERE user_id = ?",
                (user_id,)
            )

            user_data = cursor.fetchone()
            conn.close()

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
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            # Find user by email
            cursor.execute(
                "SELECT user_id, email, name FROM users WHERE email = ?",
                (email,)
            )

            user_data = cursor.fetchone()
            conn.close()

            if user_data:
                user_id, email, name = user_data
                return User(email=email, user_id=user_id, name=name)

            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
