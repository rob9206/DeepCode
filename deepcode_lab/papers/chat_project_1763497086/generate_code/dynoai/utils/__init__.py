"""
DynoAI Utilities Package

This package contains utility functions and helper modules for the DynoAI application.
Provides common functionality used across different components of the system.
"""

from .helpers import (
    format_timestamp,
    sanitize_input,
    generate_session_id,
    validate_api_key,
    safe_json_loads,
    truncate_text,
    extract_keywords,
    calculate_response_time,
    log_conversation,
    get_file_size,
    ensure_directory_exists,
    clean_old_files
)

__version__ = "1.0.0"
__author__ = "DynoAI Team"

# Package-level constants
DEFAULT_SESSION_TIMEOUT = 3600  # 1 hour in seconds
MAX_MESSAGE_LENGTH = 4000
MAX_CONVERSATION_HISTORY = 100
SUPPORTED_FILE_TYPES = ['.txt', '.json', '.csv', '.md']

# Export all utility functions
__all__ = [
    'format_timestamp',
    'sanitize_input', 
    'generate_session_id',
    'validate_api_key',
    'safe_json_loads',
    'truncate_text',
    'extract_keywords',
    'calculate_response_time',
    'log_conversation',
    'get_file_size',
    'ensure_directory_exists',
    'clean_old_files',
    'DEFAULT_SESSION_TIMEOUT',
    'MAX_MESSAGE_LENGTH',
    'MAX_CONVERSATION_HISTORY',
    'SUPPORTED_FILE_TYPES'
]