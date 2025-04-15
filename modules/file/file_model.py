"""
File model for representing uploaded files in the application.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass
class FileModel:
    """
    Model representing an uploaded file.
    """
    id: str
    name: str
    path: str
    size: int
    type: str
    uploaded_at: str
    user_id: str  # Added user_id to associate files with users

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileModel':
        """
        Create a FileModel instance from a dictionary.

        Args:
            data: Dictionary containing file data

        Returns:
            FileModel: Instance of FileModel
        """
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            path=data.get('path', ''),
            size=data.get('size', 0),
            type=data.get('type', ''),
            uploaded_at=data.get('uploaded_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            user_id=data.get('user_id', '')
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert a FileModel instance to a dictionary.

        Returns:
            Dict: Dictionary representation of the FileModel
        """
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'size': self.size,
            'type': self.type,
            'uploaded_at': self.uploaded_at,
            'user_id': self.user_id
        }

    @property
    def size_in_kb(self) -> float:
        """
        Get the file size in kilobytes.

        Returns:
            float: File size in KB
        """
        return self.size / 1024

    @property
    def extension(self) -> str:
        """
        Get the file extension.

        Returns:
            str: File extension
        """
        return self.name.split('.')[-1] if '.' in self.name else ''

    def __str__(self) -> str:
        return f"{self.name} ({self.size_in_kb:.2f} KB, {self.uploaded_at})"
