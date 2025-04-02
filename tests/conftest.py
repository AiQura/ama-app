"""
Test configuration and fixtures for the Streamlit AMA.
"""
import os
import pytest
import tempfile
import shutil
from pathlib import Path

from models.file_model import FileModel
from models.link_model import LinkModel
from services.file_service import FileService
from services.link_service import LinkService
from services.ai_service import AIService


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_file_data():
    """Sample file data for testing."""
    return {
        "id": "test-file-id",
        "name": "test.txt",
        "path": "/path/to/test.txt",
        "size": 1024,
        "type": "text/plain",
        "uploaded_at": "2025-03-17 12:00:00"
    }


@pytest.fixture
def sample_file(sample_file_data):
    """Sample FileModel instance for testing."""
    return FileModel.from_dict(sample_file_data)


@pytest.fixture
def sample_link_data():
    """Sample link data for testing."""
    return {
        "id": "test-link-id",
        "url": "https://example.com",
        "description": "Example website",
        "added_at": "2025-03-17 12:00:00"
    }


@pytest.fixture
def sample_link(sample_link_data):
    """Sample LinkModel instance for testing."""
    return LinkModel.from_dict(sample_link_data)


@pytest.fixture
def mock_file_service(monkeypatch, temp_dir):
    """
    Mock FileService for testing.

    This fixture creates a FileService that uses the temporary directory
    for its operations and doesn't interfere with real files.
    """
    # Create mock config for testing
    monkeypatch.setattr('config.config.UPLOAD_DIR',
                        os.path.join(temp_dir, 'uploads'))
    monkeypatch.setattr('config.config.FILES_REGISTRY_PATH',
                        os.path.join(temp_dir, 'files.json'))

    # Ensure directories exist
    os.makedirs(os.path.join(temp_dir, 'uploads'), exist_ok=True)

    # Return the service
    return FileService()


@pytest.fixture
def mock_link_service(monkeypatch, temp_dir):
    """
    Mock LinkService for testing.

    This fixture creates a LinkService that uses the temporary directory
    for its operations and doesn't interfere with real data.
    """
    # Create mock config for testing
    monkeypatch.setattr('config.config.LINKS_REGISTRY_PATH',
                        os.path.join(temp_dir, 'links.json'))

    # Return the service
    return LinkService()


@pytest.fixture
def mock_ai_service(monkeypatch, temp_dir):
    """
    Mock AIService for testing.

    This fixture creates an AIService that uses the temporary directory
    for its operations and doesn't interfere with real data.
    """
    # Create mock config for testing
    monkeypatch.setattr('config.config.CONVERSATION_HISTORY_PATH',
                        os.path.join(temp_dir, 'history.json'))

    # Return the service
    return AIService()
