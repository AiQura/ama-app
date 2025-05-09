"""
Service for managing file operations in the application.
"""
import os
import pathlib
import streamlit as st
import uuid
from typing import List, Optional, BinaryIO, Union
from datetime import datetime

from modules.file.file_model import FileModel
from config.config import UPLOAD_DIR
from utils.db_conenciton import db_conenciton, get_supabase_client
from modules.file.file_utils import delete_file

class FileService:
    """
    Service for managing file operations.
    """

    def __init__(self):
        """Initialize the FileService."""
        # Create necessary directories
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        self._initialize_db()

        supabase = get_supabase_client()
        self.bucket = supabase.storage.from_(st.secrets.bucket["BUCKET_NAME"])

    def _initialize_db(self) -> None:
        """Initialize the database tables for file storage."""
        with db_conenciton() as cursor:
            # Create files table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                file_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                size INTEGER NOT NULL,
                type TEXT,
                uploaded_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            ''')
            cursor.execute('ALTER TABLE files ENABLE ROW LEVEL SECURITY;')

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

            file_name = f"{file_id}_{filename}"
            file_path = os.path.join(user_upload_dir, file_name)
            file_relative_path = f"{user_id}/{file_name}"

            # Save the file - handle different types of inputs
            with open(file_path, "wb") as f:
                if hasattr(file, 'read'):
                    # If it's a file-like object
                    content = file.read()
                elif isinstance(file, (bytes, bytearray, memoryview)):
                    # If it's binary data
                    content = file
                else:
                    raise TypeError(f"Unsupported file type: {type(file)}")

                f.write(content)

            self.bucket.upload(
                file=pathlib.Path(file_path),
                path=file_relative_path,
                file_options={"cache-control": "86400", "upsert": "false"} # 86400 is 1 day
            )

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
            with db_conenciton() as cursor:
                cursor.execute(
                    """
                    INSERT INTO files
                    (file_id, user_id, name, path, size, type, uploaded_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        file_id, user_id, filename, file_relative_path,
                        file_size, file_type, uploaded_at
                    )
                )

            return file_model
        except Exception as e:
            print(f"Error adding file: {e}")
            return None

    def _relative_from_absolute_path(self, file_path: str) -> str:
        """
        takes the absolute path of the file, returns the file name with the parent directory

        Args:
            file_path: absolute path of the file

        Returns:
            str: Relative path of the file locally
        """

        p = pathlib.Path(file_path)
        return os.path.join(*p.parts[-2:])

    def _sync_file_with_bucket(self, file_path: str) -> str:
        """
        Check if file exists locally. If not, downloads it from the bucket

        Args:
            file_path: relative path of the file

        Returns:
            str: Absolute path of the file locally
        """
        absolute_path = os.path.join(UPLOAD_DIR, file_path)

        if os.path.isfile(absolute_path):
            return absolute_path

        os.makedirs(os.path.join(UPLOAD_DIR, file_path.split('/')[0]), exist_ok=True)

        with open(absolute_path, "wb+") as f:
            f.write(self.bucket.download(file_path))

        return absolute_path


    def get_file(self, file_id: str) -> Optional[FileModel]:
        """
        Get a file by ID.

        Args:
            file_id: ID of the file

        Returns:
            Optional[FileModel]: The file model or None if not found
        """
        try:
            with db_conenciton() as cursor:
                cursor.execute(
                    """
                    SELECT file_id, user_id, name, path, size, type, uploaded_at
                    FROM files
                    WHERE file_id = %s
                    """,
                    (file_id,)
                )
                row = cursor.fetchone()

            if row:
                file_id, user_id, name, path, size, type, uploaded_at = row

                file_path = self._sync_file_with_bucket(path)

                return FileModel(
                    id=file_id,
                    name=name,
                    path=file_path,
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
            with db_conenciton() as cursor:
                cursor.execute(
                    """
                    SELECT file_id, user_id, name, path, size, type, uploaded_at
                    FROM files
                    WHERE user_id = %s
                    ORDER BY uploaded_at DESC
                    """,
                    (user_id,)
                )

                rows = cursor.fetchall()

            files = []
            for row in rows:
                file_id, user_id, name, path, size, type, uploaded_at = row

                file_path = self._sync_file_with_bucket(path)

                # Check if file exists on disk
                if os.path.exists(file_path):
                    files.append(FileModel(
                        id=file_id,
                        name=name,
                        path=file_path,
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
            with db_conenciton() as cursor:
                cursor.execute(
                    """
                    SELECT file_id, user_id, name, path, size, type, uploaded_at
                    FROM files
                    ORDER BY uploaded_at DESC
                    """
                )

                rows = cursor.fetchall()

            files = []
            for row in rows:
                file_id, user_id, name, path, size, type, uploaded_at = row

                file_path = self._sync_file_with_bucket(path)

                # Check if file exists on disk
                if os.path.exists(file_path):
                    files.append(FileModel(
                        id=file_id,
                        name=name,
                        path=file_path,
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
                delete_file(file.path)

            # Delete from bucket
            self.bucket.remove([self._relative_from_absolute_path(file.path)])

            # Delete from database
            with db_conenciton() as cursor:
                cursor.execute("DELETE FROM files WHERE file_id = %s", (file_id,))

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
                # Delete from disk
                if os.path.exists(file.path):
                    delete_file(file.path)
                # Delete from bucket
                self.bucket.remove([self._relative_from_absolute_path(file.path)])


            # Delete from database
            with db_conenciton() as cursor:
                cursor.execute("DELETE FROM files WHERE user_id = %s", (user_id,))

            return True
        except Exception as e:
            print(f"Error deleting user files: {e}")
            return False
