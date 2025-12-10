"""
Database service for JSON-based song storage with comprehensive error handling.
"""
import json
import os
import shutil
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from models.song import Song, SongCreate, SongUpdate
from config.settings import settings


class DatabaseService:
    """
    Service class for managing JSON database operations.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db_path = Path(settings.DATABASE_PATH)
        self.backup_path = Path(settings.DATABASE_BACKUP_PATH)
        self._ensure_directories()
        self._initialize_database()
    
    def _ensure_directories(self) -> None:
        """Ensure database directories exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.backup_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _initialize_database(self) -> None:
        """Initialize database if it doesn't exist."""
        if not self.db_path.exists():
            self.logger.info(f"Creating new database at {self.db_path}")
            self._write_data({"songs": [], "metadata": self._get_metadata()})
        else:
            self.logger.info(f"Using existing database at {self.db_path}")
    
    def _get_metadata(self) -> Dict[str, Any]:
        """Get database metadata."""
        return {
            "version": settings.APP_VERSION,
            "created_at": datetime.now().isoformat(),
            "last_migration": datetime.now().isoformat(),
            "total_records": 0
        }
    
    def _read_data(self) -> Dict[str, Any]:
        """
        Read data from JSON database with error handling.
        
        Returns:
            Dictionary containing database data
            
        Raises:
            DatabaseReadError: If database cannot be read
        """
        try:
            if not self.db_path.exists():
                self.logger.warning(f"Database file {self.db_path} not found, creating new one")
                self._initialize_database()
                return {"songs": [], "metadata": self._get_metadata()}
            
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate data structure
            if not isinstance(data, dict):
                raise ValueError("Database data must be a dictionary")
            
            if "songs" not in data:
                data["songs"] = []
            
            if "metadata" not in data:
                data["metadata"] = self._get_metadata()
            
            self.logger.debug(f"Successfully read {len(data.get('songs', []))} songs from database")
            return data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in database file: {e}")
            raise DatabaseReadError(f"Invalid JSON format in database: {e}")
        except PermissionError as e:
            self.logger.error(f"Permission denied reading database: {e}")
            raise DatabaseReadError(f"Permission denied accessing database: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error reading database: {e}")
            raise DatabaseReadError(f"Unexpected error reading database: {e}")
    
    def _write_data(self, data: Dict[str, Any]) -> None:
        """
        Write data to JSON database with backup and error handling.
        
        Args:
            data: Data to write to database
            
        Raises:
            DatabaseWriteError: If database cannot be written
        """
        try:
            # Create backup before writing
            self._create_backup()
            
            # Ensure data structure
            if not isinstance(data, dict):
                raise ValueError("Data must be a dictionary")
            
            # Update metadata
            if "metadata" not in data:
                data["metadata"] = self._get_metadata()
            
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            data["metadata"]["total_records"] = len(data.get("songs", []))
            
            # Write data with atomic operation
            temp_path = self.db_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            # Replace original file
            temp_path.replace(self.db_path)
            
            self.logger.debug(f"Successfully wrote data to database ({len(data.get('songs', []))} songs)")
            
        except PermissionError as e:
            self.logger.error(f"Permission denied writing database: {e}")
            raise DatabaseWriteError(f"Permission denied writing database: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error writing database: {e}")
            raise DatabaseWriteError(f"Unexpected error writing database: {e}")
    
    def _create_backup(self) -> None:
        """Create a backup of the current database."""
        try:
            if self.db_path.exists():
                shutil.copy2(self.db_path, self.backup_path)
                self.logger.debug("Database backup created successfully")
        except Exception as e:
            self.logger.warning(f"Failed to create backup: {e}")
    
    def get_all_songs(self) -> List[Song]:
        """
        Retrieve all songs from database.
        
        Returns:
            List of all songs
            
        Raises:
            DatabaseReadError: If database cannot be read
        """
        try:
            data = self._read_data()
            songs_data = data.get("songs", [])
            
            songs = []
            for song_data in songs_data:
                try:
                    song = Song(**song_data)
                    songs.append(song)
                except Exception as e:
                    self.logger.warning(f"Skipping invalid song data: {e}")
                    continue
            
            return songs
            
        except DatabaseReadError:
            raise
        except Exception as e:
            self.logger.error(f"Error processing songs: {e}")
            raise DatabaseReadError(f"Error processing songs: {e}")
    
    def get_song_by_id(self, song_id: int) -> Optional[Song]:
        """
        Retrieve a specific song by ID.
        
        Args:
            song_id: ID of the song to retrieve
            
        Returns:
            Song object if found, None otherwise
        """
        try:
            songs = self.get_all_songs()
            for song in songs:
                if song.id == song_id:
                    return song
            return None
            
        except DatabaseReadError:
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving song {song_id}: {e}")
            raise DatabaseReadError(f"Error retrieving song: {e}")
    
    def create_song(self, song_data: SongCreate) -> Song:
        """
        Create a new song in database.
        
        Args:
            song_data: Song data to create
            
        Returns:
            Created Song object
            
        Raises:
            DatabaseWriteError: If song cannot be created
        """
        try:
            data = self._read_data()
            songs_data = data.get("songs", [])
            
            # Generate new ID
            existing_ids = [song.get("id", 0) for song in songs_data]
            new_id = max(existing_ids, default=0) + 1
            
            # Create song with metadata
            from uuid import uuid4
            now = datetime.now()
            
            song_dict = {
                "id": new_id,
                "uuid": str(uuid4()),
                **song_data.dict(),
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            }
            
            song = Song(**song_dict)
            
            # Add to database
            songs_data.append(song.dict())
            data["songs"] = songs_data
            
            self._write_data(data)
            self.logger.info(f"Created song with ID {new_id}")
            
            return song
            
        except DatabaseReadError:
            raise
        except Exception as e:
            self.logger.error(f"Error creating song: {e}")
            raise DatabaseWriteError(f"Error creating song: {e}")
    
    def update_song(self, song_id: int, song_data: SongUpdate) -> Song:
        """
        Update an existing song.
        
        Args:
            song_id: ID of the song to update
            song_data: Updated song data
            
        Returns:
            Updated Song object
            
        Raises:
            SongNotFoundError: If song doesn't exist
            DatabaseWriteError: If song cannot be updated
        """
        try:
            data = self._read_data()
            songs_data = data.get("songs", [])
            
            # Find song by ID
            song_index = None
            for i, song_dict in enumerate(songs_data):
                if song_dict.get("id") == song_id:
                    song_index = i
                    break
            
            if song_index is None:
                raise SongNotFoundError(f"Song with ID {song_id} not found")
            
            # Update song data
            current_song = songs_data[song_index]
            update_data = song_data.dict(exclude_unset=True)
            
            # Update fields
            for key, value in update_data.items():
                current_song[key] = value
            
            # Update timestamp
            current_song["updated_at"] = datetime.now().isoformat()
            
            # Validate updated song
            updated_song = Song(**current_song)
            songs_data[song_index] = updated_song.dict()
            
            data["songs"] = songs_data
            self._write_data(data)
            
            self.logger.info(f"Updated song with ID {song_id}")
            return updated_song
            
        except SongNotFoundError:
            raise
        except DatabaseWriteError:
            raise
        except Exception as e:
            self.logger.error(f"Error updating song {song_id}: {e}")
            raise DatabaseWriteError(f"Error updating song: {e}")
    
    def delete_song(self, song_id: int) -> bool:
        """
        Delete a song from database.
        
        Args:
            song_id: ID of the song to delete
            
        Returns:
            True if song was deleted, False if not found
            
        Raises:
            DatabaseWriteError: If song cannot be deleted
        """
        try:
            data = self._read_data()
            songs_data = data.get("songs", [])
            
            # Find and remove song by ID
            original_length = len(songs_data)
            songs_data = [song for song in songs_data if song.get("id") != song_id]
            
            if len(songs_data) == original_length:
                return False  # Song not found
            
            data["songs"] = songs_data
            self._write_data(data)
            
            self.logger.info(f"Deleted song with ID {song_id}")
            return True
            
        except DatabaseWriteError:
            raise
        except Exception as e:
            self.logger.error(f"Error deleting song {song_id}: {e}")
            raise DatabaseWriteError(f"Error deleting song: {e}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        try:
            songs = self.get_all_songs()
            
            artists = set()
            albums = set()
            years = []
            
            for song in songs:
                artists.add(song.artista)
                if song.album:
                    albums.add(song.album)
                if song.año:
                    years.append(song.año)
            
            stats = {
                "total_songs": len(songs),
                "total_artists": len(artists),
                "total_albums": len(albums),
                "year_range": {
                    "min_year": min(years) if years else None,
                    "max_year": max(years) if years else None
                },
                "database_size": self.db_path.stat().st_size if self.db_path.exists() else 0
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting database stats: {e}")
            raise DatabaseReadError(f"Error getting database stats: {e}")


# Custom exceptions
class DatabaseError(Exception):
    """Base database exception."""
    pass


class DatabaseReadError(DatabaseError):
    """Exception raised when database read operation fails."""
    pass


class DatabaseWriteError(DatabaseError):
    """Exception raised when database write operation fails."""
    pass


class SongNotFoundError(DatabaseError):
    """Exception raised when a song is not found."""
    pass


# Global database service instance
db_service = DatabaseService()