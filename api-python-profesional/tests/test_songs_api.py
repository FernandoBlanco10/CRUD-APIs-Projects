"""
Comprehensive tests for the Songs API endpoints.
"""
import json
import pytest
from flask import Flask
from flask.testing import FlaskClient

from models.song import Song, SongCreate, SongUpdate
from tests.conftest import (
    assert_valid_song_response,
    assert_valid_error_response,
    assert_valid_success_response
)


@pytest.mark.unit
@pytest.mark.database
class TestSongsAPI:
    """Test suite for Songs API endpoints."""
    
    def test_health_check(self, test_client: FlaskClient) -> None:
        """Test health check endpoint."""
        response = test_client.get('/')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert_valid_success_response(response_data)
        assert response_data["message"].startswith("Welcome to Songs API")
        assert response_data["data"]["status"] == "healthy"
    
    def test_get_all_songs_empty(self, test_client: FlaskClient, api_prefix: str) -> None:
        """Test getting all songs when database is empty."""
        response = test_client.get(f'{api_prefix}/songs')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert "songs" in response_data
        assert "total" in response_data
        assert "page" in response_data
        assert "per_page" in response_data
        
        assert response_data["total"] == 0
        assert response_data["songs"] == []
    
    def test_get_all_songs_with_data(
        self,
        test_client: FlaskClient,
        api_prefix: str,
        populate_test_database
    ) -> None:
        """Test getting all songs when database has data."""
        response = test_client.get(f'{api_prefix}/songs')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert response_data["total"] == 3
        assert len(response_data["songs"]) == 3
        assert response_data["page"] == 1
        assert response_data["has_next"] is False
        
        # Check first song structure
        first_song = response_data["songs"][0]
        assert_valid_song_response(first_song, None)  # Don't check exact values
    
    def test_get_song_by_id_success(
        self,
        test_client: FlaskClient,
        api_prefix: str,
        populate_test_database
    ) -> None:
        """Test getting a specific song by ID."""
        response = test_client.get(f'{api_prefix}/songs/1')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert_valid_song_response(response_data, None)
        assert response_data["id"] == 1
        assert response_data["titulo"] == "Bohemian Rhapsody"
    
    def test_get_song_by_id_not_found(self, test_client: FlaskClient, api_prefix: str) -> None:
        """Test getting a song that doesn't exist."""
        response = test_client.get(f'{api_prefix}/songs/999')
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        
        assert_valid_error_response(response_data, 404)
        assert "Song with id '999' not found" in response_data["message"]
    
    def test_create_song_success(
        self,
        test_client: FlaskClient,
        api_prefix: str,
        create_song_data: SongCreate
    ) -> None:
        """Test creating a new song successfully."""
        response = test_client.post(
            f'{api_prefix}/songs',
            json=create_song_data.dict(),
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        
        assert_valid_song_response(response_data, None)
        assert response_data["titulo"] == create_song_data.titulo
        assert response_data["artista"] == create_song_data.artista
        assert response_data["album"] == create_song_data.album
        assert response_data["año"] == create_song_data.año
        assert response_data["id"] == 1  # First song should have ID 1
    
    def test_create_song_missing_fields(self, test_client: FlaskClient, api_prefix: str) -> None:
        """Test creating a song with missing required fields."""
        response = test_client.post(
            f'{api_prefix}/songs',
            json={"titulo": "Test Song"},  # Missing 'artista'
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        
        assert_valid_error_response(response_data, 400)
        assert "ValidationError" in response_data["error"]
    
    def test_create_song_empty_title(self, test_client: FlaskClient, api_prefix: str) -> None:
        """Test creating a song with empty title."""
        response = test_client.post(
            f'{api_prefix}/songs',
            json={"titulo": "", "artista": "Test Artist"},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        
        assert_valid_error_response(response_data, 400)
    
    def test_create_song_invalid_content_type(self, test_client: FlaskClient, api_prefix: str) -> None:
        """Test creating a song with invalid content type."""
        response = test_client.post(
            f'{api_prefix}/songs',
            data="invalid data",
            headers={"Content-Type": "text/plain"}
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        
        assert_valid_error_response(response_data, 400)
    
    def test_update_song_success(
        self,
        test_client: FlaskClient,
        api_prefix: str,
        populate_test_database,
        update_song_data: SongUpdate
    ) -> None:
        """Test updating an existing song successfully."""
        response = test_client.put(
            f'{api_prefix}/songs/1',
            json=update_song_data.dict(),
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert_valid_song_response(response_data, None)
        assert response_data["id"] == 1
        assert response_data["album"] == update_song_data.album
        assert response_data["año"] == update_song_data.año
        assert response_data["titulo"] == "Bohemian Rhapsody"  # Should be unchanged
    
    def test_update_song_not_found(self, test_client: FlaskClient, api_prefix: str) -> None:
        """Test updating a song that doesn't exist."""
        response = test_client.put(
            f'{api_prefix}/songs/999',
            json={"album": "Test Album"},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        
        assert_valid_error_response(response_data, 404)
        assert "Song with id '999' not found" in response_data["message"]
    
    def test_update_song_empty_data(self, test_client: FlaskClient, api_prefix: str, populate_test_database) -> None:
        """Test updating a song with empty data."""
        response = test_client.put(
            f'{api_prefix}/songs/1',
            json={},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        
        assert_valid_error_response(response_data, 400)
    
    def test_delete_song_success(
        self,
        test_client: FlaskClient,
        api_prefix: str,
        populate_test_database
    ) -> None:
        """Test deleting a song successfully."""
        response = test_client.delete(f'{api_prefix}/songs/1')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert_valid_success_response(response_data)
        assert "deleted successfully" in response_data["message"]
        assert response_data["data"]["song_id"] == 1
        
        # Verify song is actually deleted
        get_response = test_client.get(f'{api_prefix}/songs/1')
        assert get_response.status_code == 404
    
    def test_delete_song_not_found(self, test_client: FlaskClient, api_prefix: str) -> None:
        """Test deleting a song that doesn't exist."""
        response = test_client.delete(f'{api_prefix}/songs/999')
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        
        assert_valid_error_response(response_data, 404)
        assert "Song with id '999' not found" in response_data["message"]
    
    def test_get_database_stats(
        self,
        test_client: FlaskClient,
        api_prefix: str,
        populate_test_database
    ) -> None:
        """Test getting database statistics."""
        response = test_client.get(f'{api_prefix}/stats')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        # Verify statistics structure
        assert "total_songs" in response_data
        assert "total_artists" in response_data
        assert "total_albums" in response_data
        assert "year_range" in response_data
        assert "database_size" in response_data
        
        assert response_data["total_songs"] == 3
        assert response_data["total_artists"] == 3  # Queen, John Lennon, The Beatles
        assert response_data["total_albums"] == 3
    
    def test_pagination(
        self,
        test_client: FlaskClient,
        api_prefix: str,
        populate_test_database
    ) -> None:
        """Test pagination functionality."""
        # Test with page size of 1
        response = test_client.get(f'{api_prefix}/songs?per_page=1&page=1')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert len(response_data["songs"]) == 1
        assert response_data["total"] == 3
        assert response_data["per_page"] == 1
        assert response_data["has_next"] is True
        assert response_data["has_prev"] is False
        
        # Test second page
        response = test_client.get(f'{api_prefix}/songs?per_page=1&page=2')
        response_data = json.loads(response.data)
        
        assert len(response_data["songs"]) == 1
        assert response_data["has_next"] is True
        assert response_data["has_prev"] is True
    
    def test_invalid_route(self, test_client: FlaskClient) -> None:
        """Test accessing invalid route."""
        response = test_client.get('/invalid/route')
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        
        assert_valid_error_response(response_data, 404)
        assert "not found" in response_data["message"]


@pytest.mark.unit
@pytest.mark.database
class TestSongsAPIEdgeCases:
    """Test suite for edge cases and boundary conditions."""
    
    def test_large_year_value(self, test_client: FlaskClient, api_prefix: str) -> None:
        """Test creating a song with a year far in the future."""
        response = test_client.post(
            f'{api_prefix}/songs',
            json={
                "titulo": "Future Song",
                "artista": "Future Artist",
                "año": 2099
            },
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400  # Should be rejected
    
    def test_very_long_title(self, test_client: FlaskClient, api_prefix: str) -> None:
        """Test creating a song with very long title."""
        long_title = "A" * 201  # Exceeds max_length of 200
        
        response = test_client.post(
            f'{api_prefix}/songs',
            json={
                "titulo": long_title,
                "artista": "Test Artist"
            },
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400
    
    def test_special_characters(
        self,
        test_client: FlaskClient,
        api_prefix: str
    ) -> None:
        """Test creating a song with special characters."""
        response = test_client.post(
            f'{api_prefix}/songs',
            json={
                "titulo": "Canción con ñáéíóú",
                "artista": "Artista con acentos àèìòù",
                "album": "Álbum con símbolos @#$%"
            },
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert "ñáéíóú" in response_data["titulo"]
        assert "àèìòù" in response_data["artista"]
        assert "@#$%" in response_data["album"]
    
    def test_negative_id_routing(self, test_client: FlaskClient, api_prefix: str) -> None:
        """Test routing with negative song ID."""
        response = test_client.get(f'{api_prefix}/songs/-1')
        # Should be handled gracefully (likely 404 or bad request)
        assert response.status_code in [404, 400]