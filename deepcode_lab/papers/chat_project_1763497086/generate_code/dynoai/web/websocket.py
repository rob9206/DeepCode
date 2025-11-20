"""
WebSocket handler for real-time chat communication in DynoAI.

This module implements WebSocket functionality using Flask-SocketIO for real-time
bidirectional communication between the client and the AI engine. It handles
chat messages, typing indicators, connection management, and real-time status updates.
"""

import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from functools import wraps

from flask import request, session
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask_socketio import Namespace

from ..config import get_config
from ..ai.core import get_ai_engine, initialize_ai_engine
from ..ai.memory import get_memory_manager, initialize_memory_system
from ..ai.plugins import get_plugin_manager, initialize_plugin_system
from ..utils import (
    sanitize_input, generate_session_id, validate_api_key,
    calculate_response_time, log_conversation, format_timestamp,
    truncate_text, safe_json_loads, DEFAULT_SESSION_TIMEOUT
)
from . import (
    initialize_web_module, get_active_connections, add_connection,
    remove_connection, get_connection_stats, update_connection_activity
)

# Configure logging
logger = logging.getLogger(__name__)

# Global SocketIO instance
socketio = None

# Connection tracking
active_sessions: Dict[str, Dict[str, Any]] = {}
typing_users: Dict[str, List[str]] = {}  # room_id -> list of typing users

# WebSocket configuration
WEBSOCKET_CONFIG = {
    'ping_timeout': 60,
    'ping_interval': 25,
    'max_http_buffer_size': 1000000,
    'cors_allowed_origins': "*",
    'async_mode': 'threading'
}

def require_websocket_auth(f):
    """Decorator to require authentication for WebSocket events."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('session_id'):
            logger.warning(f"Unauthorized WebSocket access attempt from {request.sid}")
            emit('error', {
                'type': 'auth_error',
                'message': 'Authentication required',
                'timestamp': format_timestamp()
            })
            disconnect()
            return
        return f(*args, **kwargs)
    return decorated_function

def handle_websocket_error(f):
    """Decorator to handle WebSocket errors gracefully."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"WebSocket error in {f.__name__}: {str(e)}", exc_info=True)
            emit('error', {
                'type': 'server_error',
                'message': 'An error occurred processing your request',
                'timestamp': format_timestamp()
            })
    return decorated_function

class ChatNamespace(Namespace):
    """WebSocket namespace for chat functionality."""
    
    def on_connect(self, auth=None):
        """Handle client connection."""
        try:
            # Get or create session
            session_id = session.get('session_id')
            if not session_id:
                session_id = generate_session_id()
                session['session_id'] = session_id
            
            # Track connection
            client_info = {
                'session_id': session_id,
                'socket_id': request.sid,
                'connected_at': datetime.utcnow(),
                'last_activity': datetime.utcnow(),
                'user_agent': request.headers.get('User-Agent', 'Unknown'),
                'ip_address': request.remote_addr
            }
            
            active_sessions[request.sid] = client_info
            add_connection(session_id, request.sid)
            
            # Join session room
            join_room(session_id)
            
            logger.info(f"WebSocket client connected: {session_id} ({request.sid})")
            
            # Send connection confirmation
            emit('connected', {
                'session_id': session_id,
                'timestamp': format_timestamp(),
                'server_status': 'online'
            })
            
            # Send initial status
            self._send_status_update(session_id)
            
        except Exception as e:
            logger.error(f"Error handling WebSocket connection: {str(e)}", exc_info=True)
            emit('error', {
                'type': 'connection_error',
                'message': 'Failed to establish connection',
                'timestamp': format_timestamp()
            })
            disconnect()
    
    def on_disconnect(self):
        """Handle client disconnection."""
        try:
            if request.sid in active_sessions:
                session_info = active_sessions[request.sid]
                session_id = session_info['session_id']
                
                # Remove from typing indicators
                self._remove_from_typing(session_id)
                
                # Leave rooms
                leave_room(session_id)
                
                # Update connection tracking
                remove_connection(session_id, request.sid)
                del active_sessions[request.sid]
                
                logger.info(f"WebSocket client disconnected: {session_id} ({request.sid})")
                
        except Exception as e:
            logger.error(f"Error handling WebSocket disconnection: {str(e)}", exc_info=True)
    
    @require_websocket_auth
    @handle_websocket_error
    def on_chat_message(self, data):
        """Handle incoming chat messages."""
        session_id = session.get('session_id')
        
        # Validate message data
        if not isinstance(data, dict) or 'message' not in data:
            emit('error', {
                'type': 'invalid_data',
                'message': 'Invalid message format',
                'timestamp': format_timestamp()
            })
            return
        
        message = sanitize_input(data.get('message', ''))
        if not message.strip():
            emit('error', {
                'type': 'empty_message',
                'message': 'Message cannot be empty',
                'timestamp': format_timestamp()
            })
            return
        
        # Update activity
        self._update_activity(session_id)
        
        # Remove user from typing indicators
        self._remove_from_typing(session_id)
        
        # Echo message back to confirm receipt
        emit('message_received', {
            'message_id': data.get('message_id'),
            'timestamp': format_timestamp()
        })
        
        # Process message asynchronously
        self._process_chat_message(session_id, message, data)
    
    @require_websocket_auth
    @handle_websocket_error
    def on_typing_start(self, data):
        """Handle typing indicator start."""
        session_id = session.get('session_id')
        room_id = data.get('room_id', session_id)
        
        if room_id not in typing_users:
            typing_users[room_id] = []
        
        if session_id not in typing_users[room_id]:
            typing_users[room_id].append(session_id)
        
        # Broadcast typing indicator to room
        emit('user_typing', {
            'session_id': session_id,
            'typing': True,
            'timestamp': format_timestamp()
        }, room=room_id, include_self=False)
        
        self._update_activity(session_id)
    
    @require_websocket_auth
    @handle_websocket_error
    def on_typing_stop(self, data):
        """Handle typing indicator stop."""
        session_id = session.get('session_id')
        self._remove_from_typing(session_id)
    
    @require_websocket_auth
    @handle_websocket_error
    def on_get_conversation_history(self, data):
        """Handle request for conversation history."""
        session_id = session.get('session_id')
        
        try:
            ai_engine = get_ai_engine()
            if ai_engine:
                history = ai_engine.get_conversation_history(session_id)
                emit('conversation_history', {
                    'history': history,
                    'session_id': session_id,
                    'timestamp': format_timestamp()
                })
            else:
                emit('error', {
                    'type': 'service_unavailable',
                    'message': 'AI service is not available',
                    'timestamp': format_timestamp()
                })
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}", exc_info=True)
            emit('error', {
                'type': 'history_error',
                'message': 'Failed to retrieve conversation history',
                'timestamp': format_timestamp()
            })
    
    @require_websocket_auth
    @handle_websocket_error
    def on_clear_conversation(self, data):
        """Handle request to clear conversation."""
        session_id = session.get('session_id')
        
        try:
            ai_engine = get_ai_engine()
            if ai_engine:
                ai_engine.clear_conversation(session_id)
                emit('conversation_cleared', {
                    'session_id': session_id,
                    'timestamp': format_timestamp()
                })
                logger.info(f"Conversation cleared for session: {session_id}")
            else:
                emit('error', {
                    'type': 'service_unavailable',
                    'message': 'AI service is not available',
                    'timestamp': format_timestamp()
                })
        except Exception as e:
            logger.error(f"Error clearing conversation: {str(e)}", exc_info=True)
            emit('error', {
                'type': 'clear_error',
                'message': 'Failed to clear conversation',
                'timestamp': format_timestamp()
            })
    
    @require_websocket_auth
    @handle_websocket_error
    def on_switch_model(self, data):
        """Handle AI model switching."""
        session_id = session.get('session_id')
        model_name = data.get('model')
        
        if not model_name:
            emit('error', {
                'type': 'invalid_data',
                'message': 'Model name is required',
                'timestamp': format_timestamp()
            })
            return
        
        try:
            ai_engine = get_ai_engine()
            if ai_engine:
                success = ai_engine.switch_model(model_name, session_id)
                if success:
                    emit('model_switched', {
                        'model': model_name,
                        'session_id': session_id,
                        'timestamp': format_timestamp()
                    })
                    logger.info(f"Model switched to {model_name} for session: {session_id}")
                else:
                    emit('error', {
                        'type': 'model_switch_failed',
                        'message': f'Failed to switch to model: {model_name}',
                        'timestamp': format_timestamp()
                    })
            else:
                emit('error', {
                    'type': 'service_unavailable',
                    'message': 'AI service is not available',
                    'timestamp': format_timestamp()
                })
        except Exception as e:
            logger.error(f"Error switching model: {str(e)}", exc_info=True)
            emit('error', {
                'type': 'model_error',
                'message': 'Failed to switch AI model',
                'timestamp': format_timestamp()
            })
    
    @require_websocket_auth
    @handle_websocket_error
    def on_get_status(self, data):
        """Handle status request."""
        session_id = session.get('session_id')
        self._send_status_update(session_id)
    
    def _process_chat_message(self, session_id: str, message: str, data: Dict[str, Any]):
        """Process chat message and generate AI response."""
        try:
            # Show AI thinking indicator
            emit('ai_thinking', {
                'session_id': session_id,
                'timestamp': format_timestamp()
            })
            
            # Get AI engine
            ai_engine = get_ai_engine()
            if not ai_engine:
                emit('error', {
                    'type': 'service_unavailable',
                    'message': 'AI service is not available',
                    'timestamp': format_timestamp()
                })
                return
            
            # Generate response
            start_time = datetime.utcnow()
            
            # Check if streaming is requested
            stream_response = data.get('stream', True)
            
            if stream_response:
                # Stream response in chunks
                self._stream_ai_response(session_id, message, ai_engine, start_time)
            else:
                # Generate complete response
                response_data = ai_engine.generate_response(message, session_id)
                
                if response_data and response_data.get('success'):
                    response_time = calculate_response_time(start_time)
                    
                    emit('ai_response', {
                        'response': response_data['response'],
                        'session_id': session_id,
                        'model': response_data.get('model', 'unknown'),
                        'response_time': response_time,
                        'timestamp': format_timestamp(),
                        'metadata': response_data.get('metadata', {})
                    })
                    
                    # Log conversation
                    log_conversation(session_id, message, response_data['response'])
                    
                else:
                    emit('error', {
                        'type': 'ai_error',
                        'message': response_data.get('error', 'Failed to generate response'),
                        'timestamp': format_timestamp()
                    })
            
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
            emit('error', {
                'type': 'processing_error',
                'message': 'Failed to process your message',
                'timestamp': format_timestamp()
            })
        finally:
            # Hide AI thinking indicator
            emit('ai_thinking_stop', {
                'session_id': session_id,
                'timestamp': format_timestamp()
            })
    
    def _stream_ai_response(self, session_id: str, message: str, ai_engine, start_time: datetime):
        """Stream AI response in real-time chunks."""
        try:
            # This would be implemented if the AI engine supports streaming
            # For now, we'll simulate streaming by sending the complete response
            response_data = ai_engine.generate_response(message, session_id)
            
            if response_data and response_data.get('success'):
                response = response_data['response']
                
                # Simulate streaming by sending chunks
                chunk_size = 50  # Characters per chunk
                chunks = [response[i:i+chunk_size] for i in range(0, len(response), chunk_size)]
                
                for i, chunk in enumerate(chunks):
                    emit('ai_response_chunk', {
                        'chunk': chunk,
                        'chunk_index': i,
                        'is_final': i == len(chunks) - 1,
                        'session_id': session_id,
                        'timestamp': format_timestamp()
                    })
                    
                    # Small delay to simulate real streaming
                    import time
                    time.sleep(0.1)
                
                # Send final response summary
                response_time = calculate_response_time(start_time)
                emit('ai_response_complete', {
                    'session_id': session_id,
                    'model': response_data.get('model', 'unknown'),
                    'response_time': response_time,
                    'total_chunks': len(chunks),
                    'timestamp': format_timestamp(),
                    'metadata': response_data.get('metadata', {})
                })
                
                # Log conversation
                log_conversation(session_id, message, response)
                
            else:
                emit('error', {
                    'type': 'ai_error',
                    'message': response_data.get('error', 'Failed to generate response'),
                    'timestamp': format_timestamp()
                })
                
        except Exception as e:
            logger.error(f"Error streaming AI response: {str(e)}", exc_info=True)
            emit('error', {
                'type': 'streaming_error',
                'message': 'Failed to stream response',
                'timestamp': format_timestamp()
            })
    
    def _send_status_update(self, session_id: str):
        """Send status update to client."""
        try:
            ai_engine = get_ai_engine()
            memory_manager = get_memory_manager()
            plugin_manager = get_plugin_manager()
            
            status = {
                'session_id': session_id,
                'timestamp': format_timestamp(),
                'services': {
                    'ai_engine': {
                        'available': ai_engine is not None,
                        'model': ai_engine.current_model if ai_engine else None,
                        'status': ai_engine.get_model_status() if ai_engine else 'unavailable'
                    },
                    'memory': {
                        'available': memory_manager is not None,
                        'conversations': len(memory_manager.get_all_conversations()) if memory_manager else 0
                    },
                    'plugins': {
                        'available': plugin_manager is not None,
                        'active_plugins': list(plugin_manager.get_active_plugins().keys()) if plugin_manager else []
                    }
                },
                'connection': {
                    'active_connections': len(get_active_connections()),
                    'session_active': session_id in [conn['session_id'] for conn in active_sessions.values()]
                }
            }
            
            emit('status_update', status)
            
        except Exception as e:
            logger.error(f"Error sending status update: {str(e)}", exc_info=True)
    
    def _update_activity(self, session_id: str):
        """Update last activity timestamp for session."""
        for sid, session_info in active_sessions.items():
            if session_info['session_id'] == session_id:
                session_info['last_activity'] = datetime.utcnow()
                update_connection_activity(session_id)
                break
    
    def _remove_from_typing(self, session_id: str):
        """Remove user from all typing indicators."""
        for room_id, users in typing_users.items():
            if session_id in users:
                users.remove(session_id)
                emit('user_typing', {
                    'session_id': session_id,
                    'typing': False,
                    'timestamp': format_timestamp()
                }, room=room_id, include_self=False)

def create_socketio(app):
    """Create and configure SocketIO instance."""
    global socketio
    
    try:
        config = get_config()
        
        # Update WebSocket configuration from app config
        websocket_config = WEBSOCKET_CONFIG.copy()
        if hasattr(config, 'WEBSOCKET_CONFIG'):
            websocket_config.update(config.WEBSOCKET_CONFIG)
        
        # Create SocketIO instance
        socketio = SocketIO(
            app,
            cors_allowed_origins=websocket_config['cors_allowed_origins'],
            ping_timeout=websocket_config['ping_timeout'],
            ping_interval=websocket_config['ping_interval'],
            max_http_buffer_size=websocket_config['max_http_buffer_size'],
            async_mode=websocket_config['async_mode'],
            logger=logger,
            engineio_logger=logger
        )
        
        # Register namespace
        socketio.on_namespace(ChatNamespace('/chat'))
        
        logger.info("SocketIO initialized successfully")
        return socketio
        
    except Exception as e:
        logger.error(f"Error creating SocketIO instance: {str(e)}", exc_info=True)
        raise

def initialize_websocket(app, app_config: Optional[Dict[str, Any]] = None):
    """Initialize WebSocket functionality."""
    try:
        # Initialize dependencies
        if not initialize_web_module(app_config):
            logger.error("Failed to initialize web module for WebSocket")
            return False
        
        if not initialize_ai_engine(app_config):
            logger.error("Failed to initialize AI engine for WebSocket")
            return False
        
        if not initialize_memory_system(app_config):
            logger.error("Failed to initialize memory system for WebSocket")
            return False
        
        if not initialize_plugin_system(app_config):
            logger.error("Failed to initialize plugin system for WebSocket")
            return False
        
        # Create SocketIO instance
        socketio_instance = create_socketio(app)
        
        logger.info("WebSocket module initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing WebSocket module: {str(e)}", exc_info=True)
        return False

def get_socketio():
    """Get the global SocketIO instance."""
    return socketio

def cleanup_websocket():
    """Cleanup WebSocket resources."""
    global socketio, active_sessions, typing_users
    
    try:
        # Clear session data
        active_sessions.clear()
        typing_users.clear()
        
        # Stop SocketIO if running
        if socketio:
            socketio.stop()
            socketio = None
        
        logger.info("WebSocket module cleaned up successfully")
        
    except Exception as e:
        logger.error(f"Error cleaning up WebSocket module: {str(e)}", exc_info=True)

def is_websocket_initialized():
    """Check if WebSocket module is initialized."""
    return socketio is not None

def get_websocket_stats():
    """Get WebSocket connection statistics."""
    try:
        return {
            'active_sessions': len(active_sessions),
            'typing_users': sum(len(users) for users in typing_users.values()),
            'total_rooms': len(typing_users),
            'socketio_initialized': socketio is not None,
            'connection_stats': get_connection_stats()
        }
    except Exception as e:
        logger.error(f"Error getting WebSocket stats: {str(e)}", exc_info=True)
        return {}

def broadcast_system_message(message: str, message_type: str = 'info'):
    """Broadcast system message to all connected clients."""
    if not socketio:
        logger.warning("Cannot broadcast message: SocketIO not initialized")
        return
    
    try:
        socketio.emit('system_message', {
            'message': message,
            'type': message_type,
            'timestamp': format_timestamp()
        }, namespace='/chat')
        
        logger.info(f"Broadcasted system message: {message}")
        
    except Exception as e:
        logger.error(f"Error broadcasting system message: {str(e)}", exc_info=True)

def send_message_to_session(session_id: str, message: str, message_type: str = 'info'):
    """Send message to specific session."""
    if not socketio:
        logger.warning("Cannot send message: SocketIO not initialized")
        return
    
    try:
        socketio.emit('system_message', {
            'message': message,
            'type': message_type,
            'timestamp': format_timestamp()
        }, room=session_id, namespace='/chat')
        
        logger.info(f"Sent message to session {session_id}: {message}")
        
    except Exception as e:
        logger.error(f"Error sending message to session: {str(e)}", exc_info=True)

# Export main components
__all__ = [
    'create_socketio',
    'initialize_websocket',
    'get_socketio',
    'cleanup_websocket',
    'is_websocket_initialized',
    'get_websocket_stats',
    'broadcast_system_message',
    'send_message_to_session',
    'ChatNamespace'
]