"""
DynoAI Utility Helper Functions
Provides common utility functions for data processing, validation, and system operations.
"""

import os
import re
import json
import time
import uuid
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Union


def format_timestamp(timestamp: Optional[float] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format timestamp for display.
    
    Args:
        timestamp: Unix timestamp (defaults to current time)
        format_str: Format string for datetime formatting
        
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = time.time()
    
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime(format_str)


def sanitize_input(user_input: str, max_length: int = 4000) -> str:
    """
    Clean and validate user input.
    
    Args:
        user_input: Raw user input string
        max_length: Maximum allowed length
        
    Returns:
        Sanitized input string
    """
    if not isinstance(user_input, str):
        return ""
    
    # Remove potentially harmful characters
    sanitized = re.sub(r'[<>"\']', '', user_input)
    
    # Remove excessive whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip()
    
    return sanitized


def generate_session_id() -> str:
    """
    Create unique session identifier.
    
    Returns:
        Unique session ID string
    """
    return str(uuid.uuid4())


def validate_api_key(api_key: str, key_type: str = "openai") -> bool:
    """
    Validate API key format and authenticity.
    
    Args:
        api_key: API key to validate
        key_type: Type of API key (openai, anthropic, etc.)
        
    Returns:
        True if valid format, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Remove whitespace
    api_key = api_key.strip()
    
    if key_type.lower() == "openai":
        # OpenAI keys start with 'sk-' and are typically 51 characters
        return api_key.startswith("sk-") and len(api_key) >= 20
    elif key_type.lower() == "anthropic":
        # Anthropic keys start with 'sk-ant-'
        return api_key.startswith("sk-ant-") and len(api_key) >= 20
    else:
        # Generic validation - at least 10 characters
        return len(api_key) >= 10


def safe_json_loads(json_str: str) -> Optional[Dict[str, Any]]:
    """
    Safely parse JSON with error handling.
    
    Args:
        json_str: JSON string to parse
        
    Returns:
        Parsed dictionary or None if parsing fails
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text string
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text.
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of extracted keywords
    """
    if not text:
        return []
    
    # Simple keyword extraction - remove common words and extract meaningful terms
    common_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    }
    
    # Extract words (alphanumeric, 3+ characters)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Filter out common words and get unique keywords
    keywords = list(set(word for word in words if word not in common_words))
    
    # Sort by length (longer words first) and return top keywords
    keywords.sort(key=len, reverse=True)
    
    return keywords[:max_keywords]


def calculate_response_time(start_time: float) -> float:
    """
    Measure response time.
    
    Args:
        start_time: Start timestamp
        
    Returns:
        Response time in seconds
    """
    return time.time() - start_time


def log_conversation(user_id: str, message: str, response: str, 
                    conversation_id: Optional[str] = None) -> None:
    """
    Log conversation data.
    
    Args:
        user_id: User identifier
        message: User message
        response: AI response
        conversation_id: Optional conversation identifier
    """
    try:
        log_data = {
            'timestamp': time.time(),
            'user_id': user_id,
            'conversation_id': conversation_id or generate_session_id(),
            'message': sanitize_input(message),
            'response': sanitize_input(response),
            'message_length': len(message),
            'response_length': len(response)
        }
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.join('data', 'conversations')
        ensure_directory_exists(log_dir)
        
        # Log to file (simple JSON format)
        log_file = os.path.join(log_dir, f"conversation_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_data) + '\n')
            
    except Exception as e:
        # Use Python logging as fallback
        logging.error(f"Failed to log conversation: {e}")


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes, 0 if file doesn't exist
    """
    try:
        return os.path.getsize(file_path)
    except (OSError, FileNotFoundError):
        return 0


def ensure_directory_exists(directory_path: str) -> None:
    """
    Create directory if it doesn't exist.
    
    Args:
        directory_path: Path to directory
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
    except OSError as e:
        logging.error(f"Failed to create directory {directory_path}: {e}")


def clean_old_files(directory: str, max_age_days: int = 30, 
                   file_pattern: str = "*.log") -> None:
    """
    Remove old files based on criteria.
    
    Args:
        directory: Directory to clean
        max_age_days: Maximum age in days
        file_pattern: File pattern to match
    """
    try:
        if not os.path.exists(directory):
            return
            
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        
        for filename in os.listdir(directory):
            if file_pattern == "*.log" and not filename.endswith('.log'):
                continue
            elif file_pattern != "*.log" and not re.match(file_pattern.replace('*', '.*'), filename):
                continue
                
            file_path = os.path.join(directory, filename)
            
            try:
                if os.path.getmtime(file_path) < cutoff_time:
                    os.remove(file_path)
                    logging.info(f"Removed old file: {file_path}")
            except OSError as e:
                logging.error(f"Failed to remove file {file_path}: {e}")
                
    except Exception as e:
        logging.error(f"Error cleaning old files in {directory}: {e}")


def hash_string(text: str, algorithm: str = "sha256") -> str:
    """
    Generate hash of string.
    
    Args:
        text: Text to hash
        algorithm: Hash algorithm (md5, sha1, sha256)
        
    Returns:
        Hexadecimal hash string
    """
    if algorithm == "md5":
        return hashlib.md5(text.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(text.encode()).hexdigest()
    else:  # default to sha256
        return hashlib.sha256(text.encode()).hexdigest()


def is_valid_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def get_system_info() -> Dict[str, Any]:
    """
    Get basic system information.
    
    Returns:
        Dictionary with system information
    """
    import platform
    import psutil
    
    try:
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'python_version': platform.python_version(),
            'cpu_count': os.cpu_count(),
            'memory_total': psutil.virtual_memory().total if 'psutil' in globals() else 'N/A',
            'memory_available': psutil.virtual_memory().available if 'psutil' in globals() else 'N/A',
            'disk_usage': psutil.disk_usage('/').percent if 'psutil' in globals() else 'N/A'
        }
    except ImportError:
        # Fallback if psutil is not available
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'python_version': platform.python_version(),
            'cpu_count': os.cpu_count(),
            'memory_total': 'N/A',
            'memory_available': 'N/A',
            'disk_usage': 'N/A'
        }