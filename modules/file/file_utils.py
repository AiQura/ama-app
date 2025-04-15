"""
Utility functions for persistent storage operations.
"""
import os

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
