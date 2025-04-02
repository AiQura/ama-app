"""
Tests for the AIService class.
"""
import os
import pytest
from unittest.mock import MagicMock, patch

from services.ai_service import AIService
from models.file_model import FileModel
from models.link_model import LinkModel


def test_ai_service_init(mock_ai_service):
    """Test AIService initialization."""
    assert isinstance(mock_ai_service, AIService)
    assert hasattr(mock_ai_service, 'history')
    assert isinstance(mock_ai_service.history, list)


def test_ai_service_query_ai_basic(mock_ai_service):
    """Test basic AI query without files or links."""
    # Make a query
    query = "What is the weather today?"
    result = mock_ai_service.query_ai(query)
    
    # Check the result structure
    assert "thinking" in result
    assert "response" in result
    
    # Check thinking steps
    thinking_steps = result["thinking"]
    assert isinstance(thinking_steps, list)
    assert len(thinking_steps) > 0
    
    # Each thinking step should have a step and content
    for step in thinking_steps:
        assert "step" in step
        assert "content" in step
    
    # Check the response
    response = result["response"]
    assert isinstance(response, str)
    assert query in response
    assert "weather" in response.lower()  # The mock service responds to weather queries


def test_ai_service_query_ai_with_files(mock_ai_service, sample_file):
    """Test AI query with files."""
    # Make a query with a file
    query = "Analyze this data"
    result = mock_ai_service.query_ai(query, files=[sample_file])
    
    # Check the result
    assert "thinking" in result
    assert "response" in result
    
    # Check if file is mentioned in the thinking steps
    file_mentioned = False
    for step in result["thinking"]:
        if sample_file.name in step["content"]:
            file_mentioned = True
            break
    
    assert file_mentioned, "The file should be mentioned in the thinking steps"
    
    # Check the response for data-related content (mock service responds to 'data' when files are present)
    assert "data" in result["response"].lower()


def test_ai_service_query_ai_with_links(mock_ai_service, sample_link):
    """Test AI query with links."""
    # Make a query with a link
    query = "What's on this website?"
    result = mock_ai_service.query_ai(query, links=[sample_link])
    
    # Check the result
    assert "thinking" in result
    assert "response" in result
    
    # Check if link is mentioned in the thinking steps
    link_mentioned = False
    for step in result["thinking"]:
        if sample_link.url in step["content"]:
            link_mentioned = True
            break
    
    assert link_mentioned, "The link should be mentioned in the thinking steps"
    
    # Check the response for link reference
    assert sample_link.url in result["response"]


def test_ai_service_add_to_history(mock_ai_service, sample_file, sample_link):
    """Test adding a query to history."""
    # Prepare test data
    query = "Test query"
    files = [sample_file]
    links = [sample_link]
    result = {
        "thinking": [{"step": "Test step", "content": "Test content"}],
        "response": "Test response"
    }
    
    # Add to history
    mock_ai_service.add_to_history(query, files, links, result)
    
    # Check the history
    assert len(mock_ai_service.history) == 1
    
    history_item = mock_ai_service.history[0]
    assert history_item["query"] == query
    assert len(history_item["selected_files"]) == 1
    assert history_item["selected_files"][0]["name"] == sample_file.name
    assert len(history_item["selected_links"]) == 1
    assert history_item["selected_links"][0]["url"] == sample_link.url
    assert history_item["result"] == result


def test_ai_service_get_history(mock_ai_service):
    """Test getting conversation history."""
    # Empty history initially
    assert len(mock_ai_service.get_history()) == 0
    
    # Add some history items
    mock_ai_service.history = [
        {"item": 1},
        {"item": 2}
    ]
    
    # Check the history
    history = mock_ai_service.get_history()
    assert len(history) == 2
    assert history[0]["item"] == 1
    assert history[1]["item"] == 2


def test_ai_service_clear_history(mock_ai_service):
    """Test clearing conversation history."""
    # Add some history items
    mock_ai_service.history = [
        {"item": 1},
        {"item": 2}
    ]
    
    # Clear the history
    result = mock_ai_service.clear_history()
    
    # Check the result
    assert result is True
    
    # Check the history was cleared
    assert len(mock_ai_service.history) == 0


@patch('services.ai_service.save_json')
def test_ai_service_save_history(mock_save_json, mock_ai_service):
    """Test saving conversation history."""
    # Set up the mock
    mock_save_json.return_value = True
    
    # Add some history items
    mock_ai_service.history = [
        {"item": 1},
        {"item": 2}
    ]
    
    # Save the history
    result = mock_ai_service.save_history()
    
    # Check the result
    assert result is True
    
    # Check save_json was called with the correct arguments
    mock_save_json.assert_called_once()
    args, _ = mock_save_json.call_args
    assert args[0] == mock_ai_service.history


@patch('services.ai_service.load_json')
def test_ai_service_load_history(mock_load_json, mock_ai_service):
    """Test loading conversation history."""
    # Set up the mock
    mock_history = [{"item": 1}, {"item": 2}]
    mock_load_json.return_value = mock_history
    
    # Load the history
    mock_ai_service.load_history()
    
    # Check the history was loaded
    assert mock_ai_service.history == mock_history
    
    # Check load_json was called with the correct arguments
    mock_load_json.assert_called_once()


def test_ai_service_save_and_load(mock_ai_service, monkeypatch, temp_dir):
    """Test saving and loading conversation history to/from disk."""
    # Add some queries to history
    query1 = "Test query 1"
    query2 = "Test query 2"
    
    mock_ai_service.query_ai(query1)
    mock_ai_service.query_ai(query2)
    
    # Save the history
    assert mock_ai_service.save_history() is True
    
    # Create a new service instance to test loading
    history_path = os.path.join(temp_dir, 'history.json')
    
    # Mock the config path to use our test path
    monkeypatch.setattr('config.config.CONVERSATION_HISTORY_PATH', history_path)
    
    # Create a new service that will load from the saved file
    new_service = AIService()
    
    # Check the history was loaded
    assert len(new_service.history) == 2
    assert new_service.history[0]["query"] == query1
    assert new_service.history[1]["query"] == query2