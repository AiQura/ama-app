"""
Tests for the LinkModel class.
"""
import pytest
from datetime import datetime

from models.link_model import LinkModel


def test_link_model_init():
    """Test LinkModel initialization."""
    # Create a link model
    link = LinkModel(
        id="test-id",
        url="https://example.com",
        description="Example website",
        added_at="2025-03-17 12:00:00"
    )

    # Check attributes
    assert link.id == "test-id"
    assert link.url == "https://example.com"
    assert link.description == "Example website"
    assert link.added_at == "2025-03-17 12:00:00"


def test_link_model_default_values():
    """Test LinkModel default values."""
    # Create a link model with minimal parameters
    link = LinkModel(
        id="test-id",
        url="https://example.com"
    )

    # Check default values
    assert link.id == "test-id"
    assert link.url == "https://example.com"
    assert link.description == ""
    assert link.added_at is not None  # Should have a timestamp


def test_link_model_from_dict():
    """Test LinkModel creation from dictionary."""
    # Test data
    data = {
        "id": "test-id",
        "url": "https://example.com",
        "description": "Example website",
        "added_at": "2025-03-17 12:00:00"
    }

    # Create from dictionary
    link = LinkModel.from_dict(data)

    # Check attributes
    assert link.id == "test-id"
    assert link.url == "https://example.com"
    assert link.description == "Example website"
    assert link.added_at == "2025-03-17 12:00:00"


def test_link_model_to_dict():
    """Test LinkModel conversion to dictionary."""
    # Create a link model
    link = LinkModel(
        id="test-id",
        url="https://example.com",
        description="Example website",
        added_at="2025-03-17 12:00:00"
    )

    # Convert to dictionary
    data = link.to_dict()

    # Check dictionary values
    assert data["id"] == "test-id"
    assert data["url"] == "https://example.com"
    assert data["description"] == "Example website"
    assert data["added_at"] == "2025-03-17 12:00:00"


def test_link_model_is_valid():
    """Test LinkModel is_valid method."""
    # Valid URLs
    valid_urls = [
        "http://example.com",
        "https://example.com",
        "http://www.example.com/path?query=value",
        "https://subdomain.example.com/path"
    ]

    # Invalid URLs
    invalid_urls = [
        "example.com",
        "ftp://example.com",
        "www.example.com",
        "not-a-url"
    ]

    # Test valid URLs
    for url in valid_urls:
        link = LinkModel(id="test", url=url)
        assert link.is_valid() is True

    # Test invalid URLs
    for url in invalid_urls:
        link = LinkModel(id="test", url=url)
        assert link.is_valid() is False


def test_link_model_str():
    """Test LinkModel string representation."""
    # Link with description
    link_with_desc = LinkModel(
        id="test-id",
        url="https://example.com",
        description="Example website",
        added_at="2025-03-17 12:00:00"
    )

    # Link without description
    link_without_desc = LinkModel(
        id="test-id",
        url="https://example.com",
        description="",
        added_at="2025-03-17 12:00:00"
    )

    # Check string representations
    assert str(link_with_desc) == "https://example.com - Example website (2025-03-17 12:00:00)"
    assert str(link_without_desc) == "https://example.com (2025-03-17 12:00:00)"
