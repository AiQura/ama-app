"""
Utility functions for persistent storage operations.
"""
import json
import os
from typing import Dict, List, Any, Optional


def save_json(data: Any, file_path: str) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data: The data to save
        file_path: Path to the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")
        return False


def load_json(file_path: str, default: Any = None) -> Any:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the file
        default: Default value to return if loading fails
        
    Returns:
        The loaded data or the default value
    """
    if not os.path.exists(file_path):
        return default
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return default


def delete_file(file_path: str) -> bool:
    """
    Delete a file from the filesystem.
    
    Args:
        file_path: Path to the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
        return False


def ensure_directory(directory_path: str) -> bool:
    """
    Ensure a directory exists.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {directory_path}: {e}")
        return False