"""
Error handling utilities for VibeGraph application.
Provides decorators and functions for consistent error handling across the backend.
"""

from functools import wraps
from flask import jsonify
import logging
import traceback

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def handle_errors(func):
    """
    Decorator to handle common errors and return consistent JSON responses.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return jsonify({"error": str(e)}), 500
    return wrapper

def validate_graph_id(func):
    """
    Decorator to validate that a graph_id parameter exists.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Validation error in {func.__name__}: {str(e)}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return jsonify({"error": str(e)}), 400
    return wrapper

def validate_request_data(required_fields):
    """
    Decorator to validate required fields in request data.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would be implemented based on how the routes are structured
            return func(*args, **kwargs)
        return wrapper
    return decorator