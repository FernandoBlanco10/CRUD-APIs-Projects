"""
Data models for the Songs API using Pydantic for validation.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, root_validator
from uuid import uuid4


class SongBase(BaseModel):
    """
    Base song model with common fields.
    """
    titulo: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Title of the song",
        example="Bohemian Rhapsody"
    )
    artista: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Artist name",
        example="Queen"
    )
    album: Optional[str] = Field(
        None,
        max_length=200,
        description="Album name",
        example="A Night at the Opera"
    )
    año: Optional[int] = Field(
        None,
        ge=1800,
        le=datetime.now().year,
        description="Release year",
        example=1975
    )
    
    @validator('titulo', 'artista')
    def strip_whitespace(cls, v):
        """Strip leading and trailing whitespace from string fields."""
        if isinstance(v, str):
            return v.strip()
        return v
    
    @validator('titulo', 'artista')
    def no_empty_after_strip(cls, v):
        """Ensure fields are not empty after stripping whitespace."""
        if not v:
            raise ValueError('Field cannot be empty after removing whitespace')
        return v


class SongCreate(SongBase):
    """
    Model for creating a new song.
    """
    # Additional fields for creation can be added here
    pass


class SongUpdate(BaseModel):
    """
    Model for updating an existing song.
    All fields are optional for partial updates.
    """
    titulo: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Title of the song"
    )
    artista: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Artist name"
    )
    album: Optional[str] = Field(
        None,
        max_length=200,
        description="Album name"
    )
    año: Optional[int] = Field(
        None,
        ge=1800,
        le=datetime.now().year,
        description="Release year"
    )
    
    @validator('titulo', 'artista')
    def strip_whitespace(cls, v):
        """Strip leading and trailing whitespace from string fields."""
        if isinstance(v, str):
            return v.strip()
        return v
    
    @root_validator
    def at_least_one_field(cls, values):
        """Ensure at least one field is provided for update."""
        if not any(values.get(field) is not None for field in ['titulo', 'artista', 'album', 'año']):
            raise ValueError('At least one field must be provided for update')
        return values


class Song(SongBase):
    """
    Complete song model including database fields.
    """
    id: int = Field(..., description="Unique song identifier")
    uuid: str = Field(..., description="UUID for additional identification")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "id": 1,
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "titulo": "Bohemian Rhapsody",
                "artista": "Queen",
                "album": "A Night at the Opera",
                "año": 1975,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        }


class SongList(BaseModel):
    """
    Model for song list responses.
    """
    songs: List[Song] = Field(..., description="List of songs")
    total: int = Field(..., description="Total number of songs")
    page: int = Field(default=1, description="Current page number")
    per_page: int = Field(default=50, description="Songs per page")
    has_next: bool = Field(default=False, description="Whether there are more pages")
    has_prev: bool = Field(default=False, description="Whether there are previous pages")


class ErrorResponse(BaseModel):
    """
    Standard error response model.
    """
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Request validation failed",
                "details": {
                    "field": "titulo",
                    "reason": "Field cannot be empty"
                },
                "timestamp": "2023-01-01T00:00:00"
            }
        }


class SuccessResponse(BaseModel):
    """
    Standard success response model.
    """
    success: bool = Field(default=True, description="Success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class DatabaseStats(BaseModel):
    """
    Model for database statistics.
    """
    total_songs: int = Field(..., description="Total number of songs")
    total_artists: int = Field(..., description="Total number of unique artists")
    total_albums: int = Field(..., description="Total number of unique albums")
    year_range: Dict[str, Optional[int]] = Field(
        ...,
        description="Year range (min_year, max_year)"
    )
    database_size: int = Field(..., description="Database file size in bytes")


class BulkOperationRequest(BaseModel):
    """
    Model for bulk operations on songs.
    """
    operation: str = Field(..., description="Operation type (create, update, delete)")
    songs: List[SongCreate] = Field(..., description="Songs to operate on")
    
    @validator('operation')
    def validate_operation(cls, v):
        """Validate operation type."""
        allowed_operations = ['create', 'update', 'delete']
        if v not in allowed_operations:
            raise ValueError(f'Operation must be one of: {allowed_operations}')
        return v


class BulkOperationResponse(BaseModel):
    """
    Model for bulk operation responses.
    """
    operation: str = Field(..., description="Operation performed")
    processed: int = Field(..., description="Number of songs processed")
    successful: int = Field(..., description="Number of successful operations")
    failed: int = Field(..., description="Number of failed operations")
    errors: List[ErrorResponse] = Field(default_factory=list, description="List of errors")
    created_ids: Optional[List[int]] = Field(None, description="IDs of created songs")