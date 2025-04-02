"""
Link model for representing external links in the application.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class LinkModel:
    """
    Model representing an external link.
    """
    id: str
    url: str
    user_id: str  # Added user_id to associate links with users
    description: Optional[str] = None
    added_at: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values if not provided."""
        if self.added_at is None:
            self.added_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.description is None:
            self.description = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LinkModel':
        """
        Create a LinkModel instance from a dictionary.
        
        Args:
            data: Dictionary containing link data
            
        Returns:
            LinkModel: Instance of LinkModel
        """
        return cls(
            id=data.get('id', ''),
            url=data.get('url', ''),
            description=data.get('description', ''),
            added_at=data.get('added_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            user_id=data.get('user_id', '')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert a LinkModel instance to a dictionary.
        
        Returns:
            Dict: Dictionary representation of the LinkModel
        """
        return {
            'id': self.id,
            'url': self.url,
            'description': self.description,
            'added_at': self.added_at,
            'user_id': self.user_id
        }
    
    def is_valid(self) -> bool:
        """
        Check if the link URL is valid.
        
        Returns:
            bool: True if valid, False otherwise
        """
        return self.url.startswith(('http://', 'https://'))
    
    def __str__(self) -> str:
        if self.description:
            return f"{self.url} - {self.description} ({self.added_at})"
        return f"{self.url} ({self.added_at})"