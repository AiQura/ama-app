"""
Service for managing file operations in the application.
"""
import os
import uuid
import sqlite3
from typing import Dict, List, Optional, BinaryIO, Union
from datetime import datetime

from models.file_model import FileModel
from config.config import UPLOAD_DIR, AUTH_DB_PATH
from utils.storage import delete_file
from auth.auth_service import User


class FileService:
    """
    Service for managing file operations.
    """

    def __init__(self):
        """Initialize the FileService."""
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Initialize the database tables for file storage."""
        conn = sqlite3.connect(AUTH_DB_PATH)
        cursor = conn.cursor()

        # Create files table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            file_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            size INTEGER NOT NULL,
            type TEXT,
            uploaded_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')

        conn.commit()
        conn.close()

    def add_file(self, file: Union[BinaryIO, bytes, bytearray, memoryview],
                filename: str, file_type: str = "", user_id: str = "") -> Optional[FileModel]:
        """
        Add a new file to the system.

        Args:
            file: File-like object or bytes data to save
            filename: Name of the file
            file_type: MIME type of the file
            user_id: ID of the user who owns the file

        Returns:
            Optional[FileModel]: The added file model or None if failed
        """
        try:
            # Generate a unique ID for the file
            file_id = str(uuid.uuid4())

            # Create user-specific directory
            user_upload_dir = os.path.join(UPLOAD_DIR, user_id) if user_id else UPLOAD_DIR
            os.makedirs(user_upload_dir, exist_ok=True)

            file_path = os.path.join(user_upload_dir, f"{file_id}_{filename}")

            # Save the file - handle different types of inputs
            with open(file_path, "wb") as f:
                if hasattr(file, 'read'):
                    # If it's a file-like object
                    f.write(file.read())
                elif isinstance(file, (bytes, bytearray, memoryview)):
                    # If it's binary data
                    f.write(file)
                else:
                    raise TypeError(f"Unsupported file type: {type(file)}")

            # Get file size
            file_size = os.path.getsize(file_path)

            # Current timestamp
            uploaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Create file model
            file_model = FileModel(
                id=file_id,
                name=filename,
                path=file_path,
                size=file_size,
                type=file_type,
                uploaded_at=uploaded_at,
                user_id=user_id
            )

            # Save to database
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO files
                (file_id, user_id, name, path, size, type, uploaded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    file_id, user_id, filename, file_path,
                    file_size, file_type, uploaded_at
                )
            )

            conn.commit()
            conn.close()

            return file_model
        except Exception as e:
            print(f"Error adding file: {e}")
            return None

    def get_file(self, file_id: str) -> Optional[FileModel]:
        """
        Get a file by ID.

        Args:
            file_id: ID of the file

        Returns:
            Optional[FileModel]: The file model or None if not found
        """
        try:
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT file_id, user_id, name, path, size, type, uploaded_at
                FROM files
                WHERE file_id = ?
                """,
                (file_id,)
            )

            row = cursor.fetchone()
            conn.close()

            if row:
                file_id, user_id, name, path, size, type, uploaded_at = row

                return FileModel(
                    id=file_id,
                    name=name,
                    path=path,
                    size=size,
                    type=type,
                    uploaded_at=uploaded_at,
                    user_id=user_id
                )

            return None
        except Exception as e:
            print(f"Error getting file: {e}")
            return None

    def get_user_files(self, user_id: str) -> List[FileModel]:
        """
        Get all files for a specific user.

        Args:
            user_id: ID of the user

        Returns:
            List[FileModel]: List of file models
        """
        try:
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT file_id, user_id, name, path, size, type, uploaded_at
                FROM files
                WHERE user_id = ?
                ORDER BY uploaded_at DESC
                """,
                (user_id,)
            )

            rows = cursor.fetchall()
            conn.close()

            files = []
            for row in rows:
                file_id, user_id, name, path, size, type, uploaded_at = row

                # Check if file exists on disk
                if os.path.exists(path):
                    files.append(FileModel(
                        id=file_id,
                        name=name,
                        path=path,
                        size=size,
                        type=type,
                        uploaded_at=uploaded_at,
                        user_id=user_id
                    ))
                else:
                    # File doesn't exist on disk, delete from database
                    self.delete_file(file_id)

            return files
        except Exception as e:
            print(f"Error getting user files: {e}")
            return []

    def get_all_files(self) -> List[FileModel]:
        """
        Get all files.

        Returns:
            List[FileModel]: List of all file models
        """
        try:
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT file_id, user_id, name, path, size, type, uploaded_at
                FROM files
                ORDER BY uploaded_at DESC
                """
            )

            rows = cursor.fetchall()
            conn.close()

            files = []
            for row in rows:
                file_id, user_id, name, path, size, type, uploaded_at = row

                # Check if file exists on disk
                if os.path.exists(path):
                    files.append(FileModel(
                        id=file_id,
                        name=name,
                        path=path,
                        size=size,
                        type=type,
                        uploaded_at=uploaded_at,
                        user_id=user_id
                    ))
                else:
                    # File doesn't exist on disk, delete from database
                    self.delete_file(file_id)

            return files
        except Exception as e:
            print(f"Error getting all files: {e}")
            return []

    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file.

        Args:
            file_id: ID of the file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get file info
            file = self.get_file(file_id)

            if not file:
                return False

            # Delete from disk
            if os.path.exists(file.path):
                if not delete_file(file.path):
                    return False

            # Delete from database
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM files WHERE file_id = ?", (file_id,))

            conn.commit()
            conn.close()

            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    def delete_user_files(self, user_id: str) -> bool:
        """
        Delete all files for a specific user.

        Args:
            user_id: ID of the user

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get user files
            files = self.get_user_files(user_id)

            # Delete each file
            for file in files:
                if os.path.exists(file.path):
                    delete_file(file.path)

            # Delete from database
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM files WHERE user_id = ?", (user_id,))

            conn.commit()
            conn.close()

            return True
        except Exception as e:
            print(f"Error deleting user files: {e}")
            return False
