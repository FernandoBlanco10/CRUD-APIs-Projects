"""
Pytest configuration and shared fixtures for testing.
"""
import json
import tempfile
import os
from datetime import datetime
from typing import Dict, Any, Generator
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from services.database import DatabaseService
from models.song import Song, SongCreate, SongUpdate
from config.settings import settings


@pytest.fixture(scope="session")
def test_app() -> Flask:
    """
    Create a test Flask application with test configuration.
    
    Returns:
        Flask application configured for testing
    """
    # Override settings for testing
    settings.DEBUG = True
    settings.LOG_LEVEL = "DEBUG"
    settings.DATABASE_PATH = "./tests/fixtures/test_db.json"
    settings.DATABASE_BACKUP_PATH = "./tests/fixtures/test_db_backup.json"
    
    # Create app with test configuration
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SERVER_NAME": "localhost"
    })
    
    return app


@pytest.fixture
def test_client(test_app: Flask) -> FlaskClient:
    """
    Create a test client for the Flask application.
    
    Args:
        test_app: Flask application fixture
        
    Returns:
        Flask test client
    """
    return test_app.test_client()


@pytest.fixture(scope="function")
def test_database() -> Generator[DatabaseService, None, None]:
    """
    Create a fresh test database for each test.
    
    Yields:
        DatabaseService instance with test data
    """
    # Ensure test directory exists
    test_dir = Path("./tests/fixtures")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Use temporary database file
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.json',
        delete=False,
        dir=str(test_dir)
    ) as f:
        # Initialize with empty database
        json.dump({"songs": [], "metadata": {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "last_migration": datetime.now().isoformat(),
            "total_records": 0
        }}, f)
        temp_db_path = f.name
    
    # Override database path
    original_db_path = settings.DATABASE_PATH
    settings.DATABASE_PATH = temp_db_path
    
    try:
        # Create database service
        db_service = DatabaseService()
        yield db_service
    finally:
        # Cleanup
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)
        settings.DATABASE_PATH = original_db_path


@pytest.fixture
def sample_songs_data() -> Dict[str, Any]:
    """
    Provide sample song data for testing.
    
    Returns:
        Dictionary containing sample song data
    """
    return {
        "songs": [
            {
                "id": 1,
                "uuid": "550e8400-e29b-41d4-a716-446655440001",
                "titulo": "Bohemian Rhapsody",
                "artista": "Queen",
                "album": "A Night at the Opera",
                "año": 1975,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            },
            {
                "id": 2,
                "uuid": "550e8400-e29b-41d4-a716-446655440002",
                "titulo": "Imagine",
                "artista": "John Lennon",
                "album": "Imagine",
                "año": 1971,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            },
            {
                "id": 3,
                "uuid": "550e8400-e29b-41d4-a716-446655440003",
                "titulo": "Yesterday",
                "artista": "The Beatles",
                "album": "Help!",
                "año": 1965,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        ]
    }


@pytest.fixture
def populate_test_database(test_database: DatabaseService, sample_songs_data: Dict[str, Any]) -> None:
    """
    Populate test database with sample data.
    
    Args:
        test_database: Database service fixture
        sample_songs_data: Sample song data fixture
    """
    # Write sample data to test database
    test_database._write_data(sample_songs_data)


@pytest.fixture
def create_song_data() -> SongCreate:
    """
    Provide valid song creation data.
    
    Returns:
        SongCreate instance with valid data
    """
    return SongCreate(
        titulo="Test Song",
        artista="Test Artist",
        album="Test Album",
        año=2023
    )


@pytest.fixture
def create_song_data_invalid() -> Dict[str, Any]:
    """
    Provide invalid song creation data for testing validation.
    
    Returns:
        Dictionary with invalid song data
    """
    return {
        "titulo": "",  # Empty title
        "artista": "Test Artist"
    }


@pytest.fixture
def update_song_data() -> SongUpdate:
    """
    Provide valid song update data.
    
    Returns:
        SongUpdate instance with valid data
    """
    return SongUpdate(
        album="Updated Album",
        año=2024
    )


@pytest.fixture
def api_prefix() -> str:
    """
    Provide the API prefix for endpoint construction.
    
    Returns:
        API prefix string
    """
    return settings.API_PREFIX


@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """
    Provide standard authentication headers.
    
    Returns:
        Dictionary containing authentication headers
    """
    return {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


# Pytest configuration
def pytest_configure(config):
    """
    Configure pytest with custom markers.
    
    Args:
        config: Pytest configuration object
    """
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "database: mark test as requiring database access"
    )


# Custom test assertion helpers
def assert_valid_song_response(response_data: Dict[str, Any], expected_song: Song) -> None:
    """
    Assert that response data matches expected song.
    
    Args:
        response_data: Response data to validate
        expected_song: Expected song object
    """
    assert response_data["id"] == expected_song.id
    assert response_data["titulo"] == expected_song.titulo
    assert response_data["artista"] == expected_song.artista
    assert response_data["album"] == expected_song.album
    assert response_data["año"] == expected_song.año
    assert "created_at" in response_data
    assert "updated_at" in response_data
    assert "uuid" in response_data


def assert_valid_error_response(response_data: Dict[str, Any], expected_status_code: int) -> None:
    """
    Assert that response data is a valid error response.
    
    Args:
        response_data: Response data to validate
        expected_status_code: Expected HTTP status code
    """
    assert "error" in response_data
    assert "message" in response_data
    assert "timestamp" in response_data
    assert response_data["error"] is not None
    assert response_data["message"] is not None


def assert_valid_success_response(response_data: Dict[str, Any]) -> None:
    """
    Assert that response data is a valid success response.
    
    Args:
        response_data: Response data to validate
    """
    assert "success" in response_data
    assert "message" in response_data
    assert "timestamp" in response_data
    assert response_data["success"] is True