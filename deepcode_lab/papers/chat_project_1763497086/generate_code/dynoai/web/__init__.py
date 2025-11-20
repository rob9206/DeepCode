"""
DynoAI Web Module

This module provides the web interface components for the DynoAI application,
including Flask routes, WebSocket handlers, and real-time communication.

Components:
- routes: API endpoints for chat functionality
- websocket: Real-time WebSocket communication
"""

import logging
from typing import Optional, Dict, Any

# Configure logging for web module
logger = logging.getLogger(__name__)

# Module version
__version__ = "1.0.0"

# Web module configuration
WEB_CONFIG = {
    'cors_enabled': True,
    'websocket_enabled': True,
    'max_connections': 100,
    'request_timeout': 30,
    'max_message_size': 4096,
    'rate_limit_per_minute': 60,
    'session_timeout': 3600,  # 1 hour
    'enable_compression': True,
    'enable_logging': True
}

# Global web module state
_web_initialized = False
_active_connections = {}
_connection_stats = {
    'total_connections': 0,
    'active_connections': 0,
    'messages_sent': 0,
    'messages_received': 0,
    'errors': 0
}


def initialize_web_module(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Initialize the web module with configuration.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        bool: True if initialization successful, False otherwise
    """
    global _web_initialized, WEB_CONFIG
    
    try:
        if config:
            WEB_CONFIG.update(config)
            
        # Initialize logging
        if WEB_CONFIG.get('enable_logging', True):
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
        logger.info("Web module initialized successfully")
        logger.info(f"Configuration: {WEB_CONFIG}")
        
        _web_initialized = True
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize web module: {e}")
        return False


def is_web_initialized() -> bool:
    """
    Check if the web module is initialized.
    
    Returns:
        bool: True if initialized, False otherwise
    """
    return _web_initialized


def get_web_config() -> Dict[str, Any]:
    """
    Get the current web module configuration.
    
    Returns:
        Dict[str, Any]: Current configuration
    """
    return WEB_CONFIG.copy()


def update_web_config(config: Dict[str, Any]) -> bool:
    """
    Update web module configuration.
    
    Args:
        config: Configuration updates
        
    Returns:
        bool: True if update successful, False otherwise
    """
    global WEB_CONFIG
    
    try:
        WEB_CONFIG.update(config)
        logger.info(f"Web configuration updated: {config}")
        return True
    except Exception as e:
        logger.error(f"Failed to update web configuration: {e}")
        return False


def register_connection(session_id: str, connection_info: Dict[str, Any]) -> bool:
    """
    Register a new WebSocket connection.
    
    Args:
        session_id: Unique session identifier
        connection_info: Connection metadata
        
    Returns:
        bool: True if registration successful, False otherwise
    """
    global _active_connections, _connection_stats
    
    try:
        if len(_active_connections) >= WEB_CONFIG.get('max_connections', 100):
            logger.warning("Maximum connections reached")
            return False
            
        _active_connections[session_id] = {
            'info': connection_info,
            'connected_at': connection_info.get('timestamp'),
            'last_activity': connection_info.get('timestamp'),
            'message_count': 0
        }
        
        _connection_stats['total_connections'] += 1
        _connection_stats['active_connections'] = len(_active_connections)
        
        logger.info(f"Connection registered: {session_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to register connection {session_id}: {e}")
        return False


def unregister_connection(session_id: str) -> bool:
    """
    Unregister a WebSocket connection.
    
    Args:
        session_id: Session identifier to unregister
        
    Returns:
        bool: True if unregistration successful, False otherwise
    """
    global _active_connections, _connection_stats
    
    try:
        if session_id in _active_connections:
            del _active_connections[session_id]
            _connection_stats['active_connections'] = len(_active_connections)
            logger.info(f"Connection unregistered: {session_id}")
            return True
        else:
            logger.warning(f"Connection not found for unregistration: {session_id}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to unregister connection {session_id}: {e}")
        return False


def get_active_connections() -> Dict[str, Any]:
    """
    Get information about active connections.
    
    Returns:
        Dict[str, Any]: Active connections information
    """
    return _active_connections.copy()


def get_connection_stats() -> Dict[str, Any]:
    """
    Get connection statistics.
    
    Returns:
        Dict[str, Any]: Connection statistics
    """
    return _connection_stats.copy()


def update_connection_activity(session_id: str, timestamp: Optional[float] = None) -> bool:
    """
    Update last activity timestamp for a connection.
    
    Args:
        session_id: Session identifier
        timestamp: Activity timestamp (current time if None)
        
    Returns:
        bool: True if update successful, False otherwise
    """
    global _active_connections
    
    try:
        if session_id in _active_connections:
            import time
            _active_connections[session_id]['last_activity'] = timestamp or time.time()
            return True
        else:
            logger.warning(f"Connection not found for activity update: {session_id}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to update connection activity {session_id}: {e}")
        return False


def increment_message_stats(message_type: str = 'sent') -> None:
    """
    Increment message statistics.
    
    Args:
        message_type: Type of message ('sent' or 'received')
    """
    global _connection_stats
    
    try:
        if message_type == 'sent':
            _connection_stats['messages_sent'] += 1
        elif message_type == 'received':
            _connection_stats['messages_received'] += 1
    except Exception as e:
        logger.error(f"Failed to increment message stats: {e}")


def increment_error_stats() -> None:
    """Increment error statistics."""
    global _connection_stats
    
    try:
        _connection_stats['errors'] += 1
    except Exception as e:
        logger.error(f"Failed to increment error stats: {e}")


def cleanup_inactive_connections(timeout_seconds: Optional[int] = None) -> int:
    """
    Clean up inactive connections based on timeout.
    
    Args:
        timeout_seconds: Timeout in seconds (uses config default if None)
        
    Returns:
        int: Number of connections cleaned up
    """
    global _active_connections, _connection_stats
    
    try:
        import time
        
        timeout = timeout_seconds or WEB_CONFIG.get('session_timeout', 3600)
        current_time = time.time()
        inactive_sessions = []
        
        for session_id, conn_info in _active_connections.items():
            last_activity = conn_info.get('last_activity', 0)
            if current_time - last_activity > timeout:
                inactive_sessions.append(session_id)
        
        # Remove inactive connections
        for session_id in inactive_sessions:
            del _active_connections[session_id]
        
        _connection_stats['active_connections'] = len(_active_connections)
        
        if inactive_sessions:
            logger.info(f"Cleaned up {len(inactive_sessions)} inactive connections")
            
        return len(inactive_sessions)
        
    except Exception as e:
        logger.error(f"Failed to cleanup inactive connections: {e}")
        return 0


def reset_web_module() -> bool:
    """
    Reset the web module to initial state.
    
    Returns:
        bool: True if reset successful, False otherwise
    """
    global _web_initialized, _active_connections, _connection_stats
    
    try:
        _web_initialized = False
        _active_connections.clear()
        _connection_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'errors': 0
        }
        
        logger.info("Web module reset successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to reset web module: {e}")
        return False


def shutdown_web_module() -> bool:
    """
    Shutdown the web module gracefully.
    
    Returns:
        bool: True if shutdown successful, False otherwise
    """
    try:
        # Clean up all active connections
        connection_count = len(_active_connections)
        
        # Reset module state
        reset_web_module()
        
        logger.info(f"Web module shutdown complete. Cleaned up {connection_count} connections.")
        return True
        
    except Exception as e:
        logger.error(f"Failed to shutdown web module: {e}")
        return False


# Module exports
__all__ = [
    'initialize_web_module',
    'is_web_initialized',
    'get_web_config',
    'update_web_config',
    'register_connection',
    'unregister_connection',
    'get_active_connections',
    'get_connection_stats',
    'update_connection_activity',
    'increment_message_stats',
    'increment_error_stats',
    'cleanup_inactive_connections',
    'reset_web_module',
    'shutdown_web_module',
    'WEB_CONFIG',
    '__version__'
]

# Initialize module on import
if not _web_initialized:
    initialize_web_module()