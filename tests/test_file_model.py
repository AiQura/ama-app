"""
Tests for the FileModel class.
"""
import pytest
from datetime import datetime

from models.file_model import FileModel


def test_file_model_init():
    """Test FileModel initialization."""
    # Create a file model
    file = FileModel(
        id="test-id",
        name="test.txt",
        path="/path/to/test.txt",
        size=1024,
        type="text/plain",
        uploaded_at="2025-03-17 12:00:00"
    )

    # Check attributes
    assert file.id == "test-id"
    assert file.name == "test.txt"
    assert file.path == "/path/to/test.txt"
    assert file.size == 1024
    assert file.type == "text/plain"
    assert file.uploaded_at == "2025-03-17 12:00:00"


def test_file_model_from_dict():
    """Test FileModel creation from dictionary."""
    # Test data
    data = {
        "id": "test-id",
        "name": "test.txt",
        "path": "/path/to/test.txt",
        "size": 1024,
        "type": "text/plain",
        "uploaded_at": "2025-03-17 12:00:00"
    }

    # Create from dictionary
    file = FileModel.from_dict(data)

    # Check attributes
    assert file.id == "test-id"
    assert file.name == "test.txt"
    assert file.path == "/path/to/test.txt"
    assert file.size == 1024
    assert file.type == "text/plain"
    assert file.uploaded_at == "2025-03-17 12:00:00"


def test_file_model_to_dict():
    """Test FileModel conversion to dictionary."""
    # Create a file model
    file = FileModel(
        id="test-id",
        name="test.txt",
        path="/path/to/test.txt",
        size=1024,
        type="text/plain",
        uploaded_at="2025-03-17 12:00:00"
    )

    # Convert to dictionary
    data = file.to_dict()

    # Check dictionary values
    assert data["id"] == "test-id"
    assert data["name"] == "test.txt"
    assert data["path"] == "/path/to/test.txt"
    assert data["size"] == 1024
    assert data["type"] == "text/plain"
    assert data["uploaded_at"] == "2025-03-17 12:00:00"


def test_file_model_size_in_kb():
    """Test FileModel size_in_kb property."""
    # Create a file model with size in bytes
    file = FileModel(
        id="test-id",
        name="test.txt",
        path="/path/to/test.txt",
        size=2048,  # 2 KB in bytes
        type="text/plain",
        uploaded_at="2025-03-17 12:00:00"
    )

    # Check size in KB
    assert file.size_in_kb == 2.0


def test_file_model_extension():
    """Test FileModel extension property."""
    # Create a file model with an extension
    file = FileModel(
        id="test-id",
        name="test.txt",
        path="/path/to/test.txt",
        size=1024,
        type="text/plain",
        uploaded_at="2025-03-17 12:00:00"
    )

    # Check extension
    assert file.extension == "txt"

    # Create a file model without an extension
    file = FileModel(
        id="test-id",
        name="test",
        path="/path/to/test",
        size=1024,
        type="text/plain",
        uploaded_at="2025-03-17 12:00:00"
    )

    # Check extension
    assert file.extension == ""


def test_file_model_str():
    """Test FileModel string representation."""
    # Create a file model
    file = FileModel(
        id="test-id",
        name="test.txt",
        path="/path/to/test.txt",
        size=1024,
        type="text/plain",
        uploaded_at="2025-03-17 12:00:00"
    )

    # Check string representation
    assert str(file) == "test.txt (1.00 KB, 2025-03-17 12:00:00)"
