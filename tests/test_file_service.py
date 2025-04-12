"""
Tests for the FileService class.
"""
import os
import pytest
import io
from unittest.mock import MagicMock

from services.file_service import FileService
from models.file_model import FileModel


def test_file_service_init(mock_file_service):
    """Test FileService initialization."""
    assert isinstance(mock_file_service, FileService)
    assert hasattr(mock_file_service, 'files')
    assert isinstance(mock_file_service.files, dict)


def test_file_service_add_file(mock_file_service, temp_dir):
    """Test adding a file."""
    # Create a mock file
    file_content = b"Test file content"
    file = io.BytesIO(file_content)
    filename = "test_file.txt"
    file_type = "text/plain"

    # Add the file
    file_model = mock_file_service.add_file(file, filename, file_type)

    # Test with bytes directly
    bytes_file_model = mock_file_service.add_file(file_content, "bytes_file.txt", "text/plain")

    # Test with memoryview
    memoryview_content = memoryview(file_content)
    memoryview_file_model = mock_file_service.add_file(memoryview_content, "memoryview_file.txt", "text/plain")

    # Check the file model
    assert file_model is not None
    assert file_model.name == filename
    assert file_model.type == file_type
    assert os.path.exists(file_model.path)

    # Check the file was added to the registry
    assert file_model.id in mock_file_service.files
    assert mock_file_service.files[file_model.id].name == filename

    # Check file content was saved correctly
    with open(file_model.path, 'rb') as f:
        assert f.read() == file_content


def test_file_service_get_file(mock_file_service):
    """Test getting a file by ID."""
    # Create a mock file
    file_content = b"Test file content"
    file = io.BytesIO(file_content)
    filename = "test_file.txt"
    file_type = "text/plain"

    # Add the file
    file_model = mock_file_service.add_file(file, filename, file_type)

    # Get the file
    retrieved_file = mock_file_service.get_file(file_model.id)

    # Check the retrieved file
    assert retrieved_file is not None
    assert retrieved_file.id == file_model.id
    assert retrieved_file.name == filename
    assert retrieved_file.type == file_type


def test_file_service_get_all_files(mock_file_service):
    """Test getting all files."""
    # Add some files
    file1 = mock_file_service.add_file(io.BytesIO(b"File 1"), "file1.txt", "text/plain")
    file2 = mock_file_service.add_file(io.BytesIO(b"File 2"), "file2.txt", "text/plain")

    # Get all files
    files = mock_file_service.get_all_files()

    # Check the files
    assert len(files) == 2
    assert any(f.id == file1.id for f in files)
    assert any(f.id == file2.id for f in files)


def test_file_service_delete_file(mock_file_service):
    """Test deleting a file."""
    # Add a file
    file = mock_file_service.add_file(io.BytesIO(b"Test file"), "test.txt", "text/plain")
    file_path = file.path

    # Check the file exists
    assert os.path.exists(file_path)

    # Delete the file
    result = mock_file_service.delete_file(file.id)

    # Check the result
    assert result is True

    # Check the file was removed from the registry
    assert file.id not in mock_file_service.files

    # Check the file was deleted from disk
    assert not os.path.exists(file_path)


def test_file_service_delete_nonexistent_file(mock_file_service):
    """Test deleting a nonexistent file."""
    # Try to delete a nonexistent file
    result = mock_file_service.delete_file("nonexistent-id")

    # Check the result
    assert result is False


def test_file_service_save_and_load(mock_file_service, monkeypatch, temp_dir):
    """Test saving and loading files."""
    # Add some files
    file1 = mock_file_service.add_file(io.BytesIO(b"File 1"), "file1.txt", "text/plain")
    file2 = mock_file_service.add_file(io.BytesIO(b"File 2"), "file2.txt", "text/plain")

    # Save the files
    assert mock_file_service.save_files() is True

    # Create a new service instance to test loading
    files_registry_path = os.path.join(temp_dir, 'files.json')

    # Mock the config path to use our test path
    monkeypatch.setattr('config.config.FILES_REGISTRY_PATH', files_registry_path)

    # Create a new service that will load from the saved file
    new_service = FileService()

    # Check the files were loaded
    assert len(new_service.files) == 2
    assert file1.id in new_service.files
    assert file2.id in new_service.files
    assert new_service.files[file1.id].name == "file1.txt"
    assert new_service.files[file2.id].name == "file2.txt"
