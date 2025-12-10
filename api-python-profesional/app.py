"""
Main application file for the Songs API.
Professional Flask application with comprehensive error handling, logging, and validation.
"""
import logging
from datetime import datetime
from typing import Dict, Any

from flask import Flask, jsonify, request, Response
from flasgger import Swagger, swag_from
from werkzeug.exceptions import BadRequest

from config.settings import settings
from models.song import (
    Song, SongCreate, SongUpdate, SongList, SuccessResponse,
    DatabaseStats, ErrorResponse
)
from services.database import db_service, SongNotFoundError, DatabaseReadError, DatabaseWriteError
from utils.errors import (
    setup_logging, register_error_handlers, RequestLogger,
    ValidationError, NotFoundError, AppException,
    log_request, log_response, validate_json_content_type
)


def create_app() -> Flask:
    """
    Create and configure Flask application with best practices.
    
    Returns:
        Configured Flask application instance
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Configure app
    app.config.update(
        DEBUG=settings.DEBUG,
        JSON_AS_ASCII=False,  # Support for Unicode characters
        JSON_SORT_KEYS=False,
        JSONIFY_PRETTYPRINT_REGULAR=True,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max request size
    )
    
    # Setup logging
    setup_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Setup Swagger documentation
    setup_swagger(app)
    
    # Register middleware
    register_middleware(app)
    
    # Register routes
    register_routes(app)
    
    app.logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} initialized successfully")
    
    return app


def setup_swagger(app: Flask) -> None:
    """
    Setup Swagger/OpenAPI documentation.
    
    Args:
        app: Flask application instance
    """
    app.config['SWAGGER'] = {
        'title': settings.APP_NAME,
        'uiversion': 3,
        'specs_route': '/api/docs',
        'description': 'Professional REST API for managing song collections',
        'version': settings.APP_VERSION,
        'contact': {
            'name': 'API Support',
            'email': 'support@example.com'
        },
        'license': {
            'name': 'MIT',
            'url': 'https://opensource.org/licenses/MIT'
        }
    }
    
    Swagger(app)


def register_middleware(app: Flask) -> None:
    """
    Register request/response middleware.
    
    Args:
        app: Flask application instance
    """
    
    @app.before_request
    def before_request():
        """Execute before each request."""
        request.start_time = datetime.now()
        request.request_id = f"req_{int(datetime.now().timestamp() * 1000000)}"
        
        # Log incoming request
        log_request({
            "method": request.method,
            "path": request.path,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get('User-Agent'),
            "content_length": request.content_length,
            "request_id": request.request_id
        })
    
    @app.after_request
    def after_request(response: Response):
        """Execute after each request."""
        # Calculate duration
        if hasattr(request, 'start_time'):
            duration = (datetime.now() - request.start_time).total_seconds() * 1000
        else:
            duration = 0
        
        # Log outgoing response
        log_response({
            "status_code": response.status_code,
            "content_type": response.content_type,
            "content_length": response.content_length,
            "duration_ms": duration,
            "request_id": getattr(request, 'request_id', None)
        })
        
        # Add custom headers
        response.headers['X-API-Version'] = settings.APP_VERSION
        response.headers['X-Request-ID'] = getattr(request, 'request_id', '')
        
        return response


def register_routes(app: Flask) -> None:
    """
    Register all API routes.
    
    Args:
        app: Flask application instance
    """
    
    @app.route('/', methods=['GET'])
    @swag_from({
        'responses': {
            200: {
                'description': 'Welcome message',
                'schema': SuccessResponse
            }
        }
    })
    def health_check():
        """
        Health check endpoint.
        
        Returns:
            Welcome message and API status
        """
        response = SuccessResponse(
            message=f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION}",
            data={
                "status": "healthy",
                "version": settings.APP_VERSION,
                "timestamp": datetime.now().isoformat(),
                "database_connected": True
            }
        )
        return jsonify(response.dict()), 200
    
    @app.route('/api/v1/health', methods=['GET'])
    @swag_from({
        'responses': {
            200: {
                'description': 'Detailed health status',
                'schema': SuccessResponse
            }
        }
    })
    def detailed_health_check():
        """
        Detailed health check with database statistics.
        
        Returns:
            Detailed system status including database stats
        """
        try:
            stats = db_service.get_database_stats()
            response = SuccessResponse(
                message="System is healthy",
                data={
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "database": {
                        "connected": True,
                        "stats": stats
                    }
                }
            )
            return jsonify(response.dict()), 200
        except Exception as e:
            response = SuccessResponse(
                message="System health check failed",
                data={
                    "status": "unhealthy",
                    "timestamp": datetime.now().isoformat(),
                    "database": {
                        "connected": False,
                        "error": str(e)
                    }
                }
            )
            return jsonify(response.dict()), 503
    
    @app.route(f'{settings.API_PREFIX}/songs', methods=['GET'])
    @swag_from({
        'responses': {
            200: {
                'description': 'List of all songs',
                'schema': SongList
            }
        }
    })
    def get_songs():
        """
        Get all songs from the database.
        
        Returns:
            Paginated list of songs
            
        Query Parameters:
            page (int): Page number (default: 1)
            per_page (int): Items per page (default: 50, max: 100)
        """
        try:
            # Get query parameters
            page = max(1, request.args.get('page', 1, type=int))
            per_page = min(100, max(1, request.args.get('per_page', 50, type=int)))
            
            # Get all songs
            songs = db_service.get_all_songs()
            total = len(songs)
            
            # Calculate pagination
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_songs = songs[start_idx:end_idx]
            
            # Create response
            response = SongList(
                songs=paginated_songs,
                total=total,
                page=page,
                per_page=per_page,
                has_next=end_idx < total,
                has_prev=page > 1
            )
            
            return jsonify(response.dict()), 200
            
        except DatabaseReadError as e:
            raise AppException(
                message=f"Failed to retrieve songs: {str(e)}",
                error_code="DATABASE_READ_ERROR",
                status_code=500
            )
        except Exception as e:
            raise AppException(
                message="Unexpected error occurred while retrieving songs",
                error_code="INTERNAL_ERROR",
                status_code=500
            )
    
    @app.route(f'{settings.API_PREFIX}/songs/<int:song_id>', methods=['GET'])
    @swag_from({
        'responses': {
            200: {
                'description': 'Song details',
                'schema': Song
            },
            404: {
                'description': 'Song not found',
                'schema': ErrorResponse
            }
        }
    })
    def get_song(song_id: int):
        """
        Get a specific song by ID.
        
        Args:
            song_id: ID of the song to retrieve
            
        Returns:
            Song object
            
        Raises:
            NotFoundError: If song doesn't exist
        """
        try:
            with RequestLogger() as logger:
                song = db_service.get_song_by_id(song_id)
                
                if not song:
                    raise NotFoundError("Song", song_id)
                
                return jsonify(song.dict()), 200
                
        except NotFoundError:
            raise
        except DatabaseReadError as e:
            raise AppException(
                message=f"Failed to retrieve song: {str(e)}",
                error_code="DATABASE_READ_ERROR",
                status_code=500
            )
        except Exception as e:
            raise AppException(
                message="Unexpected error occurred while retrieving song",
                error_code="INTERNAL_ERROR",
                status_code=500
            )
    
    @app.route(f'{settings.API_PREFIX}/songs', methods=['POST'])
    @swag_from({
        'responses': {
            201: {
                'description': 'Song created successfully',
                'schema': Song
            },
            400: {
                'description': 'Validation error',
                'schema': ErrorResponse
            },
            500: {
                'description': 'Database error',
                'schema': ErrorResponse
            }
        }
    })
    def create_song():
        """
        Create a new song.
        
        Returns:
            Created song object
            
        Raises:
            ValidationError: If request data is invalid
            AppException: If database operation fails
        """
        try:
            with RequestLogger() as logger:
                # Validate content type
                validate_json_content_type(request)
                
                # Parse JSON data
                if not request.json:
                    raise ValidationError("Request body must be JSON")
                
                # Validate and create song
                song_data = SongCreate(**request.json)
                song = db_service.create_song(song_data)
                
                return jsonify(song.dict()), 201
                
        except ValidationError:
            raise
        except DatabaseWriteError as e:
            raise AppException(
                message=f"Failed to create song: {str(e)}",
                error_code="DATABASE_WRITE_ERROR",
                status_code=500
            )
        except Exception as e:
            raise AppException(
                message="Unexpected error occurred while creating song",
                error_code="INTERNAL_ERROR",
                status_code=500
            )
    
    @app.route(f'{settings.API_PREFIX}/songs/<int:song_id>', methods=['PUT'])
    @swag_from({
        'responses': {
            200: {
                'description': 'Song updated successfully',
                'schema': Song
            },
            400: {
                'description': 'Validation error',
                'schema': ErrorResponse
            },
            404: {
                'description': 'Song not found',
                'schema': ErrorResponse
            },
            500: {
                'description': 'Database error',
                'schema': ErrorResponse
            }
        }
    })
    def update_song(song_id: int):
        """
        Update an existing song.
        
        Args:
            song_id: ID of the song to update
            
        Returns:
            Updated song object
            
        Raises:
            ValidationError: If request data is invalid
            NotFoundError: If song doesn't exist
            AppException: If database operation fails
        """
        try:
            with RequestLogger() as logger:
                # Validate content type
                validate_json_content_type(request)
                
                # Parse JSON data
                if not request.json:
                    raise ValidationError("Request body must be JSON")
                
                # Validate and update song
                song_data = SongUpdate(**request.json)
                song = db_service.update_song(song_id, song_data)
                
                return jsonify(song.dict()), 200
                
        except ValidationError:
            raise
        except NotFoundError:
            raise
        except DatabaseWriteError as e:
            raise AppException(
                message=f"Failed to update song: {str(e)}",
                error_code="DATABASE_WRITE_ERROR",
                status_code=500
            )
        except Exception as e:
            raise AppException(
                message="Unexpected error occurred while updating song",
                error_code="INTERNAL_ERROR",
                status_code=500
            )
    
    @app.route(f'{settings.API_PREFIX}/songs/<int:song_id>', methods=['DELETE'])
    @swag_from({
        'responses': {
            200: {
                'description': 'Song deleted successfully',
                'schema': SuccessResponse
            },
            404: {
                'description': 'Song not found',
                'schema': ErrorResponse
            },
            500: {
                'description': 'Database error',
                'schema': ErrorResponse
            }
        }
    })
    def delete_song(song_id: int):
        """
        Delete a song from the database.
        
        Args:
            song_id: ID of the song to delete
            
        Returns:
            Success message
            
        Raises:
            NotFoundError: If song doesn't exist
            AppException: If database operation fails
        """
        try:
            with RequestLogger() as logger:
                success = db_service.delete_song(song_id)
                
                if not success:
                    raise NotFoundError("Song", song_id)
                
                response = SuccessResponse(
                    message=f"Song with ID {song_id} deleted successfully",
                    data={"song_id": song_id}
                )
                
                return jsonify(response.dict()), 200
                
        except NotFoundError:
            raise
        except DatabaseWriteError as e:
            raise AppException(
                message=f"Failed to delete song: {str(e)}",
                error_code="DATABASE_WRITE_ERROR",
                status_code=500
            )
        except Exception as e:
            raise AppException(
                message="Unexpected error occurred while deleting song",
                error_code="INTERNAL_ERROR",
                status_code=500
            )
    
    @app.route(f'{settings.API_PREFIX}/stats', methods=['GET'])
    @swag_from({
        'responses': {
            200: {
                'description': 'Database statistics',
                'schema': DatabaseStats
            }
        }
    })
    def get_database_stats():
        """
        Get database statistics.
        
        Returns:
            Database statistics including counts and metadata
        """
        try:
            with RequestLogger() as logger:
                stats = db_service.get_database_stats()
                return jsonify(stats), 200
                
        except DatabaseReadError as e:
            raise AppException(
                message=f"Failed to retrieve database stats: {str(e)}",
                error_code="DATABASE_READ_ERROR",
                status_code=500
            )
        except Exception as e:
            raise AppException(
                message="Unexpected error occurred while retrieving database stats",
                error_code="INTERNAL_ERROR",
                status_code=500
            )


# Create application instance
app = create_app()


if __name__ == '__main__':
    """Run the application."""
    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG,
        threaded=True
    )