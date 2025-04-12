"""
Tests for the LinkService class.
"""
import os
import pytest
from unittest.mock import MagicMock

from services.link_service import LinkService
from models.link_model import LinkModel


def test_link_service_init(mock_link_service):
    """Test LinkService initialization."""
    assert isinstance(mock_link_service, LinkService)
    assert hasattr(mock_link_service, 'links')
    assert isinstance(mock_link_service.links, dict)


def test_link_service_add_link(mock_link_service):
    """Test adding a link."""
    # Add a valid link
    url = "https://example.com"
    description = "Example website"

    link_model = mock_link_service.add_link(url, description)

    # Check the link model
    assert link_model is not None
    assert link_model.url == url
    assert link_model.description == description

    # Check the link was added to the registry
    assert link_model.id in mock_link_service.links
    assert mock_link_service.links[link_model.id].url == url


def test_link_service_add_invalid_link(mock_link_service):
    """Test adding an invalid link."""
    # Try to add an invalid link
    url = "example.com"  # Missing http:// or https://
    description = "Invalid URL"

    link_model = mock_link_service.add_link(url, description)

    # Check the link was not added
    assert link_model is None


def test_link_service_get_link(mock_link_service):
    """Test getting a link by ID."""
    # Add a link
    url = "https://example.com"
    description = "Example website"

    link_model = mock_link_service.add_link(url, description)

    # Get the link
    retrieved_link = mock_link_service.get_link(link_model.id)

    # Check the retrieved link
    assert retrieved_link is not None
    assert retrieved_link.id == link_model.id
    assert retrieved_link.url == url
    assert retrieved_link.description == description


def test_link_service_get_all_links(mock_link_service):
    """Test getting all links."""
    # Add some links
    link1 = mock_link_service.add_link("https://example1.com", "Example 1")
    link2 = mock_link_service.add_link("https://example2.com", "Example 2")

    # Get all links
    links = mock_link_service.get_all_links()

    # Check the links
    assert len(links) == 2
    assert any(l.id == link1.id for l in links)
    assert any(l.id == link2.id for l in links)


def test_link_service_delete_link(mock_link_service):
    """Test deleting a link."""
    # Add a link
    link = mock_link_service.add_link("https://example.com", "Example")

    # Delete the link
    result = mock_link_service.delete_link(link.id)

    # Check the result
    assert result is True

    # Check the link was removed from the registry
    assert link.id not in mock_link_service.links


def test_link_service_delete_nonexistent_link(mock_link_service):
    """Test deleting a nonexistent link."""
    # Try to delete a nonexistent link
    result = mock_link_service.delete_link("nonexistent-id")

    # Check the result
    assert result is False


def test_link_service_update_link(mock_link_service):
    """Test updating a link."""
    # Add a link
    link = mock_link_service.add_link("https://example.com", "Example")

    # Update the link
    new_url = "https://updated-example.com"
    new_description = "Updated Example"

    updated_link = mock_link_service.update_link(link.id, new_url, new_description)

    # Check the updated link
    assert updated_link is not None
    assert updated_link.id == link.id
    assert updated_link.url == new_url
    assert updated_link.description == new_description

    # Check the link was updated in the registry
    assert mock_link_service.links[link.id].url == new_url
    assert mock_link_service.links[link.id].description == new_description


def test_link_service_update_link_partial(mock_link_service):
    """Test partially updating a link."""
    # Add a link
    original_url = "https://example.com"
    original_description = "Example"
    link = mock_link_service.add_link(original_url, original_description)

    # Update only the description
    new_description = "Updated Example"
    updated_link = mock_link_service.update_link(link.id, description=new_description)

    # Check the updated link
    assert updated_link is not None
    assert updated_link.url == original_url  # URL should remain unchanged
    assert updated_link.description == new_description


def test_link_service_update_nonexistent_link(mock_link_service):
    """Test updating a nonexistent link."""
    # Try to update a nonexistent link
    updated_link = mock_link_service.update_link(
        "nonexistent-id",
        "https://example.com",
        "Example"
    )

    # Check the result
    assert updated_link is None


def test_link_service_update_link_invalid_url(mock_link_service):
    """Test updating a link with an invalid URL."""
    # Add a link
    link = mock_link_service.add_link("https://example.com", "Example")

    # Try to update with an invalid URL
    invalid_url = "example.com"  # Missing http:// or https://
    updated_link = mock_link_service.update_link(link.id, invalid_url)

    # Check the result
    assert updated_link is None


def test_link_service_save_and_load(mock_link_service, monkeypatch, temp_dir):
    """Test saving and loading links."""
    # Add some links
    link1 = mock_link_service.add_link("https://example1.com", "Example 1")
    link2 = mock_link_service.add_link("https://example2.com", "Example 2")

    # Save the links
    assert mock_link_service.save_links() is True

    # Create a new service instance to test loading
    links_registry_path = os.path.join(temp_dir, 'links.json')

    # Mock the config path to use our test path
    monkeypatch.setattr('config.config.LINKS_REGISTRY_PATH', links_registry_path)

    # Create a new service that will load from the saved file
    new_service = LinkService()

    # Check the links were loaded
    assert len(new_service.links) == 2
    assert link1.id in new_service.links
    assert link2.id in new_service.links
    assert new_service.links[link1.id].url == "https://example1.com"
    assert new_service.links[link2.id].url == "https://example2.com"
