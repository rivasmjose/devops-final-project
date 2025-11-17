"""Unit tests for Flask Notes App."""

import json
from unittest.mock import MagicMock, patch
import pytest
from app.app import app

@pytest.fixture
def client():
    """Provide a Flask test client with app context."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_home_page(client):
    """Test that home page renders correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data

@patch("app.app.Note.query")
def test_get_notes(mock_query, client):
    """Test GET /notes returns mocked notes."""
    mock_note = MagicMock()
    mock_note.to_dict.return_value = {"id": 1, "title": "Test", "content": "Content"}
    mock_query.all.return_value = [mock_note]

    response = client.get("/notes")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == [{"id": 1, "title": "Test", "content": "Content"}]

@patch("app.app.db.session")
@patch("app.app.Note")
def test_add_note(mock_note_class, mock_session, client):
    """Test POST /notes adds a new note."""
    mock_note_instance = MagicMock()
    mock_note_instance.to_dict.return_value = {"id": 1, "title": "New", "content": "Note"}
    mock_note_class.return_value = mock_note_instance

    response = client.post(
        "/notes",
        data=json.dumps({"title": "New", "content": "Note"}),
        content_type="application/json",
    )

    mock_session.add.assert_called_once_with(mock_note_instance)
    mock_session.commit.assert_called_once()
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data == {"id": 1, "title": "New", "content": "Note"}

@patch("app.app.db.session")
@patch("app.app.Note.query")
def test_delete_note(mock_query, mock_session, client):
    """Test DELETE /notes/<id> deletes a note."""
    mock_note_instance = MagicMock()
    mock_query.get_or_404.return_value = mock_note_instance

    response = client.delete("/notes/1")

    mock_session.delete.assert_called_once_with(mock_note_instance)
    mock_session.commit.assert_called_once()
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == {"message": "Note deleted"}

def test_metrics_endpoint(client):
    """Test /metrics endpoint returns Prometheus metrics."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/plain")
