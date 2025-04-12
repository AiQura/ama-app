"""
Service for managing link operations in the application.
"""
import uuid
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime

from models.link_model import LinkModel
from config.config import AUTH_DB_PATH
from auth.auth_service import User


class LinkService:
    """
    Service for managing link operations.
    """

    def __init__(self):
        """Initialize the LinkService."""
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Initialize the database tables for link storage."""
        conn = sqlite3.connect(AUTH_DB_PATH)
        cursor = conn.cursor()

        # Create links table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS links (
            link_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT,
            added_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')

        conn.commit()
        conn.close()

    def add_link(self, url: str, description: str = "", user_id: str = "") -> Optional[LinkModel]:
        """
        Add a new link to the system.

        Args:
            url: URL of the link
            description: Description of the link
            user_id: ID of the user who owns the link

        Returns:
            Optional[LinkModel]: The added link model or None if invalid
        """
        try:
            # Create a new link model
            link_id = str(uuid.uuid4())
            added_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            link_model = LinkModel(
                id=link_id,
                url=url,
                description=description,
                added_at=added_at,
                user_id=user_id
            )

            # Validate the link
            if not link_model.is_valid():
                return None

            # Add to database
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO links
                (link_id, user_id, url, description, added_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (link_id, user_id, url, description, added_at)
            )

            conn.commit()
            conn.close()

            return link_model
        except Exception as e:
            print(f"Error adding link: {e}")
            return None

    def get_link(self, link_id: str) -> Optional[LinkModel]:
        """
        Get a link by ID.

        Args:
            link_id: ID of the link

        Returns:
            Optional[LinkModel]: The link model or None if not found
        """
        try:
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT link_id, user_id, url, description, added_at
                FROM links
                WHERE link_id = ?
                """,
                (link_id,)
            )

            row = cursor.fetchone()
            conn.close()

            if row:
                link_id, user_id, url, description, added_at = row

                return LinkModel(
                    id=link_id,
                    url=url,
                    description=description,
                    added_at=added_at,
                    user_id=user_id
                )

            return None
        except Exception as e:
            print(f"Error getting link: {e}")
            return None

    def get_user_links(self, user_id: str) -> List[LinkModel]:
        """
        Get all links for a specific user.

        Args:
            user_id: ID of the user

        Returns:
            List[LinkModel]: List of link models
        """
        try:
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT link_id, user_id, url, description, added_at
                FROM links
                WHERE user_id = ?
                ORDER BY added_at DESC
                """,
                (user_id,)
            )

            rows = cursor.fetchall()
            conn.close()

            links = []
            for row in rows:
                link_id, user_id, url, description, added_at = row

                links.append(LinkModel(
                    id=link_id,
                    url=url,
                    description=description,
                    added_at=added_at,
                    user_id=user_id
                ))

            return links
        except Exception as e:
            print(f"Error getting user links: {e}")
            return []

    def get_all_links(self) -> List[LinkModel]:
        """
        Get all links.

        Returns:
            List[LinkModel]: List of all link models
        """
        try:
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT link_id, user_id, url, description, added_at
                FROM links
                ORDER BY added_at DESC
                """
            )

            rows = cursor.fetchall()
            conn.close()

            links = []
            for row in rows:
                link_id, user_id, url, description, added_at = row

                links.append(LinkModel(
                    id=link_id,
                    url=url,
                    description=description,
                    added_at=added_at,
                    user_id=user_id
                ))

            return links
        except Exception as e:
            print(f"Error getting all links: {e}")
            return []

    def delete_link(self, link_id: str) -> bool:
        """
        Delete a link.

        Args:
            link_id: ID of the link

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM links WHERE link_id = ?", (link_id,))

            conn.commit()
            conn.close()

            return True
        except Exception as e:
            print(f"Error deleting link: {e}")
            return False

    def delete_user_links(self, user_id: str) -> bool:
        """
        Delete all links for a specific user.

        Args:
            user_id: ID of the user

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM links WHERE user_id = ?", (user_id,))

            conn.commit()
            conn.close()

            return True
        except Exception as e:
            print(f"Error deleting user links: {e}")
            return False

    def update_link(self, link_id: str, url: Optional[str] = None,
                   description: Optional[str] = None) -> Optional[LinkModel]:
        """
        Update a link.

        Args:
            link_id: ID of the link
            url: New URL (optional)
            description: New description (optional)

        Returns:
            Optional[LinkModel]: The updated link model or None if not found
        """
        try:
            # Get current link
            link = self.get_link(link_id)

            if not link:
                return None

            # Update fields
            if url is not None:
                link.url = url

            if description is not None:
                link.description = description

            # Re-validate the link
            if not link.is_valid():
                return None

            # Update in database
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE links
                SET url = ?, description = ?
                WHERE link_id = ?
                """,
                (link.url, link.description, link_id)
            )

            conn.commit()
            conn.close()

            return link
        except Exception as e:
            print(f"Error updating link: {e}")
            return None
