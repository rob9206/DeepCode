"""
DynoAI Web Routes Module

This module implements the main API endpoints for the DynoAI web interface,
providing REST API endpoints for chat functionality, conversation management,
settings, and system status.

Key Features:
- Chat API endpoints for message processing
- Conversation history management
- User preference and settings management
- System status and health checks
- Plugin management endpoints
- Export/import functionality
"""

import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from functools import wraps

from flask import Blueprint, request, jsonify, session, current_app
from flask import render_template, redirect, url_for, flash

# Internal imports
from . import (
    initialize_web_module, register_connection, unregister_connection,
    get_active_connections, increment_message_stats, increment_error_stats,
    update_connection_activity, get_connection_stats
)
from ..config import get_config, AI_MODEL_PRESETS, PLUGIN_CONFIGS
from ..ai.core import get_ai_engine, initialize_ai_engine
from ..ai.memory import get_memory_manager, initialize_memory_system
from ..ai.plugins import get_plugin_manager, initialize_plugin_system
from ..utils import (
    sanitize_input, generate_session_id, validate_api_key,
    format_timestamp, truncate_text, safe_json_loads,
    calculate_response_time, log_conversation
)

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
routes_bp = Blueprint('routes', __name__)

# Global variables for component instances
ai_engine = None
memory_manager = None
plugin_manager = None
config = None

def initialize_routes(app_config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Initialize the routes module with required components.
    
    Args:
        app_config: Optional configuration dictionary
        
    Returns:
        bool: True if initialization successful, False otherwise
    """
    global ai_engine, memory_manager, plugin_manager, config
    
    try:
        # Get configuration
        config = get_config()
        if app_config:
            config.update(app_config)
        
        # Initialize web module
        initialize_web_module(config)
        
        # Initialize AI engine
        if not initialize_ai_engine(config):
            logger.error("Failed to initialize AI engine")
            return False
        ai_engine = get_ai_engine()
        
        # Initialize memory system
        if not initialize_memory_system(config):
            logger.error("Failed to initialize memory system")
            return False
        memory_manager = get_memory_manager()
        
        # Initialize plugin system
        if not initialize_plugin_system(config):
            logger.error("Failed to initialize plugin system")
            return False
        plugin_manager = get_plugin_manager()
        
        logger.info("Routes module initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize routes module: {e}")
        return False

def require_session(f):
    """Decorator to ensure valid session exists."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_id' not in session:
            session['session_id'] = generate_session_id()
            register_connection(session['session_id'], {
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'timestamp': datetime.now().timestamp()
            })
        
        update_connection_activity(session['session_id'])
        return f(*args, **kwargs)
    return decorated_function

def handle_api_error(f):
    """Decorator for consistent API error handling."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"API error in {f.__name__}: {e}")
            increment_error_stats()
            return jsonify({
                'success': False,
                'error': str(e),
                'timestamp': format_timestamp()
            }), 500
    return decorated_function

# Main page routes
@routes_bp.route('/')
@require_session
def index():
    """Main chat interface page."""
    try:
        return render_template('index.html', 
                             session_id=session['session_id'],
                             config=config)
    except Exception as e:
        logger.error(f"Error rendering index page: {e}")
        return f"Error loading chat interface: {e}", 500

@routes_bp.route('/chat')
@require_session
def chat():
    """Chat page with conversation history."""
    try:
        # Get recent conversations for this session
        conversations = []
        if memory_manager:
            conversations = memory_manager.get_user_conversations(
                session['session_id'], limit=10
            )
        
        return render_template('chat.html',
                             session_id=session['session_id'],
                             conversations=conversations,
                             config=config)
    except Exception as e:
        logger.error(f"Error rendering chat page: {e}")
        return f"Error loading chat page: {e}", 500

# API endpoints
@routes_bp.route('/api/chat/message', methods=['POST'])
@require_session
@handle_api_error
def send_message():
    """Process chat message and return AI response."""
    start_time = datetime.now()
    
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Message content required'
            }), 400
        
        # Sanitize and validate input
        user_message = sanitize_input(data['message'])
        if not user_message.strip():
            return jsonify({
                'success': False,
                'error': 'Empty message not allowed'
            }), 400
        
        # Get optional parameters
        conversation_id = data.get('conversation_id')
        model_name = data.get('model', 'balanced')
        use_plugins = data.get('use_plugins', True)
        
        # Generate AI response
        if not ai_engine:
            return jsonify({
                'success': False,
                'error': 'AI engine not available'
            }), 503
        
        # Switch model if requested
        if model_name != ai_engine.current_model:
            ai_engine.switch_model(model_name)
        
        # Generate response
        response_data = ai_engine.generate_response(
            user_message,
            session_id=session['session_id'],
            conversation_id=conversation_id,
            use_plugins=use_plugins and plugin_manager is not None
        )
        
        # Store conversation in memory
        if memory_manager and response_data.get('success'):
            memory_manager.store_conversation(
                session_id=session['session_id'],
                conversation_id=response_data.get('conversation_id'),
                messages=[
                    {'role': 'user', 'content': user_message, 'timestamp': start_time.isoformat()},
                    {'role': 'assistant', 'content': response_data.get('response', ''), 'timestamp': datetime.now().isoformat()}
                ]
            )
        
        # Calculate response time
        response_time = calculate_response_time(start_time)
        
        # Update statistics
        increment_message_stats('sent')
        increment_message_stats('received')
        
        # Log conversation
        log_conversation(session['session_id'], user_message, response_data.get('response', ''))
        
        return jsonify({
            'success': True,
            'response': response_data.get('response', ''),
            'conversation_id': response_data.get('conversation_id'),
            'model_used': ai_engine.current_model,
            'response_time': response_time,
            'plugins_used': response_data.get('plugins_used', []),
            'timestamp': format_timestamp()
        })
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        increment_error_stats()
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': format_timestamp()
        }), 500

@routes_bp.route('/api/chat/history', methods=['GET'])
@require_session
@handle_api_error
def get_chat_history():
    """Get conversation history for current session."""
    try:
        conversation_id = request.args.get('conversation_id')
        limit = int(request.args.get('limit', 50))
        
        if not memory_manager:
            return jsonify({
                'success': False,
                'error': 'Memory system not available'
            }), 503
        
        if conversation_id:
            # Get specific conversation
            conversation = memory_manager.get_conversation(conversation_id)
            if conversation:
                return jsonify({
                    'success': True,
                    'conversation': conversation.to_dict(),
                    'timestamp': format_timestamp()
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Conversation not found'
                }), 404
        else:
            # Get all conversations for session
            conversations = memory_manager.get_user_conversations(
                session['session_id'], limit=limit
            )
            return jsonify({
                'success': True,
                'conversations': [conv.to_dict() for conv in conversations],
                'count': len(conversations),
                'timestamp': format_timestamp()
            })
            
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@routes_bp.route('/api/chat/clear', methods=['POST'])
@require_session
@handle_api_error
def clear_chat():
    """Clear conversation history."""
    try:
        data = request.get_json() or {}
        conversation_id = data.get('conversation_id')
        
        if conversation_id:
            # Clear specific conversation
            if ai_engine:
                ai_engine.clear_conversation(conversation_id)
            success = True
        else:
            # Clear all conversations for session
            if ai_engine:
                ai_engine.clear_conversation(session['session_id'])
            success = True
        
        return jsonify({
            'success': success,
            'message': 'Chat history cleared',
            'timestamp': format_timestamp()
        })
        
    except Exception as e:
        logger.error(f"Error clearing chat: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@routes_bp.route('/api/models', methods=['GET'])
@require_session
@handle_api_error
def get_models():
    """Get available AI models."""
    try:
        models = []
        for name, preset in AI_MODEL_PRESETS.items():
            model_info = {
                'name': name,
                'display_name': preset.get('display_name', name.title()),
                'description': preset.get('description', ''),
                'type': preset.get('type', 'openai'),
                'available': True
            }
            
            # Check if model is actually available
            if ai_engine:
                status = ai_engine.get_model_status(name)
                model_info['available'] = status.get('available', False)
                model_info['status'] = status.get('status', 'unknown')
            
            models.append(model_info)
        
        current_model = ai_engine.current_model if ai_engine else 'balanced'
        
        return jsonify({
            'success': True,
            'models': models,
            'current_model': current_model,
            'timestamp': format_timestamp()
        })
        
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@routes_bp.route('/api/models/switch', methods=['POST'])
@require_session
@handle_api_error
def switch_model():
    """Switch AI model."""
    try:
        data = request.get_json()
        if not data or 'model' not in data:
            return jsonify({
                'success': False,
                'error': 'Model name required'
            }), 400
        
        model_name = data['model']
        
        if not ai_engine:
            return jsonify({
                'success': False,
                'error': 'AI engine not available'
            }), 503
        
        # Switch model
        success = ai_engine.switch_model(model_name)
        
        if success:
            return jsonify({
                'success': True,
                'current_model': ai_engine.current_model,
                'message': f'Switched to {model_name} model',
                'timestamp': format_timestamp()
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to switch to {model_name} model'
            }), 400
            
    except Exception as e:
        logger.error(f"Error switching model: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@routes_bp.route('/api/plugins', methods=['GET'])
@require_session
@handle_api_error
def get_plugins():
    """Get available plugins."""
    try:
        plugins = []
        
        if plugin_manager:
            available_plugins = plugin_manager.get_available_plugins()
            for plugin_name, plugin_info in available_plugins.items():
                plugins.append({
                    'name': plugin_name,
                    'display_name': plugin_info.get('display_name', plugin_name.title()),
                    'description': plugin_info.get('description', ''),
                    'enabled': plugin_manager.is_plugin_enabled(plugin_name),
                    'status': plugin_info.get('status', 'unknown')
                })
        else:
            # Fallback to config-based plugin info
            for plugin_name, plugin_config in PLUGIN_CONFIGS.items():
                plugins.append({
                    'name': plugin_name,
                    'display_name': plugin_config.get('display_name', plugin_name.title()),
                    'description': plugin_config.get('description', ''),
                    'enabled': plugin_config.get('enabled', False),
                    'status': 'unavailable'
                })
        
        return jsonify({
            'success': True,
            'plugins': plugins,
            'timestamp': format_timestamp()
        })
        
    except Exception as e:
        logger.error(f"Error getting plugins: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@routes_bp.route('/api/plugins/toggle', methods=['POST'])
@require_session
@handle_api_error
def toggle_plugin():
    """Enable or disable a plugin."""
    try:
        data = request.get_json()
        if not data or 'plugin' not in data:
            return jsonify({
                'success': False,
                'error': 'Plugin name required'
            }), 400
        
        plugin_name = data['plugin']
        enabled = data.get('enabled', True)
        
        if not plugin_manager:
            return jsonify({
                'success': False,
                'error': 'Plugin system not available'
            }), 503
        
        # Toggle plugin
        if enabled:
            success = plugin_manager.enable_plugin(plugin_name)
            action = 'enabled'
        else:
            success = plugin_manager.disable_plugin(plugin_name)
            action = 'disabled'
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Plugin {plugin_name} {action}',
                'plugin': plugin_name,
                'enabled': enabled,
                'timestamp': format_timestamp()
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to {action.rstrip("d")} plugin {plugin_name}'
            }), 400
            
    except Exception as e:
        logger.error(f"Error toggling plugin: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@routes_bp.route('/api/export', methods=['GET'])
@require_session
@handle_api_error
def export_data():
    """Export user data and conversations."""
    try:
        export_type = request.args.get('type', 'conversations')
        format_type = request.args.get('format', 'json')
        
        if not memory_manager:
            return jsonify({
                'success': False,
                'error': 'Memory system not available'
            }), 503
        
        if export_type == 'conversations':
            # Export conversations
            conversations = memory_manager.get_user_conversations(
                session['session_id'], limit=None
            )
            
            export_data = {
                'type': 'conversations',
                'session_id': session['session_id'],
                'export_timestamp': format_timestamp(),
                'conversations': [conv.to_dict() for conv in conversations]
            }
            
        elif export_type == 'preferences':
            # Export user preferences
            preferences = memory_manager.get_user_preferences(session['session_id'])
            
            export_data = {
                'type': 'preferences',
                'session_id': session['session_id'],
                'export_timestamp': format_timestamp(),
                'preferences': [pref.to_dict() for pref in preferences]
            }
            
        elif export_type == 'all':
            # Export everything
            conversations = memory_manager.get_user_conversations(
                session['session_id'], limit=None
            )
            preferences = memory_manager.get_user_preferences(session['session_id'])
            
            export_data = {
                'type': 'complete',
                'session_id': session['session_id'],
                'export_timestamp': format_timestamp(),
                'conversations': [conv.to_dict() for conv in conversations],
                'preferences': [pref.to_dict() for pref in preferences]
            }
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid export type'
            }), 400
        
        return jsonify({
            'success': True,
            'data': export_data,
            'timestamp': format_timestamp()
        })
        
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@routes_bp.route('/api/status', methods=['GET'])
@handle_api_error
def get_status():
    """Get system status and health information."""
    try:
        status = {
            'system': 'DynoAI',
            'version': '1.0.0',
            'status': 'operational',
            'timestamp': format_timestamp(),
            'components': {}
        }
        
        # AI Engine status
        if ai_engine:
            status['components']['ai_engine'] = {
                'status': 'operational',
                'current_model': ai_engine.current_model,
                'available_models': list(AI_MODEL_PRESETS.keys())
            }
        else:
            status['components']['ai_engine'] = {
                'status': 'unavailable',
                'error': 'AI engine not initialized'
            }
        
        # Memory system status
        if memory_manager:
            status['components']['memory'] = {
                'status': 'operational',
                'database_connected': True
            }
        else:
            status['components']['memory'] = {
                'status': 'unavailable',
                'error': 'Memory system not initialized'
            }
        
        # Plugin system status
        if plugin_manager:
            enabled_plugins = [name for name, enabled in plugin_manager.get_plugin_status().items() if enabled]
            status['components']['plugins'] = {
                'status': 'operational',
                'enabled_plugins': enabled_plugins,
                'total_plugins': len(PLUGIN_CONFIGS)
            }
        else:
            status['components']['plugins'] = {
                'status': 'unavailable',
                'error': 'Plugin system not initialized'
            }
        
        # Connection statistics
        connection_stats = get_connection_stats()
        status['connections'] = connection_stats
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'system': 'DynoAI',
            'status': 'error',
            'error': str(e),
            'timestamp': format_timestamp()
        }), 500

# Error handlers
@routes_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'API endpoint not found',
            'timestamp': format_timestamp()
        }), 404
    else:
        return render_template('index.html'), 404

@routes_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    increment_error_stats()
    
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'timestamp': format_timestamp()
        }), 500
    else:
        return "Internal server error", 500

# Cleanup function
def cleanup_routes():
    """Cleanup routes module resources."""
    try:
        # Cleanup connections for this session if exists
        if 'session_id' in session:
            unregister_connection(session['session_id'])
        
        logger.info("Routes module cleaned up successfully")
        
    except Exception as e:
        logger.error(f"Error during routes cleanup: {e}")

# Module initialization check
def is_routes_initialized() -> bool:
    """Check if routes module is properly initialized."""
    return all([
        ai_engine is not None,
        memory_manager is not None,
        plugin_manager is not None,
        config is not None
    ])

# Export the blueprint and initialization function
__all__ = [
    'routes_bp',
    'initialize_routes',
    'cleanup_routes',
    'is_routes_initialized'
]