#!/usr/bin/env python3
"""
DynoAI - Dynamic AI Assistant Application
Main Flask application with real-time chat interface, persona management, and AI integration.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid

# Import our AI engine components
from config import get_config, validate_environment
from ai_engine.chat_handler import (
    get_default_chat_handler, 
    ChatHandler, 
    MessageRole, 
    ConversationStatus,
    StreamingStatus,
    StreamingResponse
)
from ai_engine.persona_manager import (
    get_default_persona_manager,
    PersonaManager,
    PersonaConfig,
    PersonaType,
    PersonaManagerError
)
from ai_engine.prompt_templates import get_default_prompt_templates, PromptTemplateError

# Initialize Flask app
app = Flask(__name__)
config = get_config()
app.config.from_object(config)

# Initialize SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize AI components
chat_handler = get_default_chat_handler()
persona_manager = get_default_persona_manager()
prompt_templates = get_default_prompt_templates()

# Setup logging
logging.basicConfig(
    level=logging.INFO if not app.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state management
active_conversations: Dict[str, str] = {}  # session_id -> conversation_id
user_sessions: Dict[str, Dict[str, Any]] = {}  # session_id -> user_data


class DynoAIError(Exception):
    """Custom exception for DynoAI application errors."""
    pass


def init_session():
    """Initialize user session with default values."""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session['created_at'] = datetime.now().isoformat()
        session['conversation_count'] = 0
        session['current_persona'] = PersonaType.ASSISTANT.value
        session['theme'] = 'light'
        session['settings'] = {
            'auto_save': True,
            'show_timestamps': True,
            'enable_streaming': True,
            'max_history': 100
        }
        logger.info(f"New session initialized: {session['user_id']}")
    
    return session['user_id']


def get_user_data(user_id: str) -> Dict[str, Any]:
    """Get or create user data."""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'conversations': {},
            'active_persona': PersonaType.ASSISTANT,
            'settings': session.get('settings', {}),
            'usage_stats': {
                'total_messages': 0,
                'total_tokens': 0,
                'conversations_created': 0
            }
        }
    return user_sessions[user_id]


# Flask Routes

@app.route('/')
def index():
    """Main chat interface."""
    user_id = init_session()
    user_data = get_user_data(user_id)
    
    # Get available personas
    try:
        available_personas = persona_manager.get_available_personas()
        current_persona = persona_manager.get_active_persona()
    except PersonaManagerError as e:
        logger.error(f"Error getting personas: {e}")
        available_personas = {}
        current_persona = None
    
    return render_template('index.html',
                         user_id=user_id,
                         available_personas=available_personas,
                         current_persona=current_persona,
                         conversation_count=session.get('conversation_count', 0),
                         theme=session.get('theme', 'light'))


@app.route('/settings')
def settings():
    """Settings and configuration page."""
    user_id = init_session()
    user_data = get_user_data(user_id)
    
    # Get available personas and current configuration
    try:
        available_personas = persona_manager.get_available_personas()
        current_persona = persona_manager.get_active_persona()
        ai_config = config.get_ai_config()
    except (PersonaManagerError, AttributeError) as e:
        logger.error(f"Error getting configuration: {e}")
        available_personas = {}
        current_persona = None
        ai_config = {}
    
    return render_template('settings.html',
                         user_id=user_id,
                         available_personas=available_personas,
                         current_persona=current_persona,
                         ai_config=ai_config,
                         user_settings=session.get('settings', {}),
                         usage_stats=user_data.get('usage_stats', {}))


# API Routes

@app.route('/api/personas', methods=['GET'])
def api_get_personas():
    """Get available AI personas."""
    try:
        personas = persona_manager.get_available_personas()
        current = persona_manager.get_active_persona()
        
        return jsonify({
            'status': 'success',
            'personas': {k: v.to_dict() for k, v in personas.items()},
            'current_persona': current.to_dict() if current else None
        })
    except PersonaManagerError as e:
        logger.error(f"Error getting personas: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/personas/<persona_type>', methods=['POST'])
def api_set_persona(persona_type: str):
    """Set active AI persona."""
    try:
        # Convert string to PersonaType enum
        persona_enum = PersonaType(persona_type.upper())
        persona_manager.set_active_persona(persona_enum)
        session['current_persona'] = persona_type.upper()
        
        return jsonify({
            'status': 'success',
            'message': f'Persona switched to {persona_type}',
            'current_persona': persona_manager.get_active_persona().to_dict()
        })
    except (ValueError, PersonaManagerError) as e:
        logger.error(f"Error setting persona {persona_type}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/conversations', methods=['GET'])
def api_get_conversations():
    """Get user's conversation history."""
    user_id = init_session()
    user_data = get_user_data(user_id)
    
    try:
        conversations = []
        for conv_id, conv_data in user_data.get('conversations', {}).items():
            # Get conversation details from chat handler
            history = chat_handler.get_conversation_history(conv_id)
            if history:
                conversations.append({
                    'id': conv_id,
                    'title': conv_data.get('title', f'Conversation {conv_id[:8]}'),
                    'created_at': conv_data.get('created_at'),
                    'message_count': len(history.get('messages', [])),
                    'persona': conv_data.get('persona', 'assistant'),
                    'status': history.get('status', 'active')
                })
        
        return jsonify({
            'status': 'success',
            'conversations': conversations,
            'total': len(conversations)
        })
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def api_get_conversation(conversation_id: str):
    """Get specific conversation details."""
    user_id = init_session()
    
    try:
        history = chat_handler.get_conversation_history(conversation_id)
        if not history:
            return jsonify({'status': 'error', 'message': 'Conversation not found'}), 404
        
        return jsonify({
            'status': 'success',
            'conversation': history
        })
    except Exception as e:
        logger.error(f"Error getting conversation {conversation_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/conversations/<conversation_id>/export', methods=['GET'])
def api_export_conversation(conversation_id: str):
    """Export conversation to various formats."""
    user_id = init_session()
    export_format = request.args.get('format', 'json')
    
    try:
        exported_data = chat_handler.export_conversation(conversation_id, export_format)
        if not exported_data:
            return jsonify({'status': 'error', 'message': 'Conversation not found'}), 404
        
        return jsonify({
            'status': 'success',
            'format': export_format,
            'data': exported_data
        })
    except Exception as e:
        logger.error(f"Error exporting conversation {conversation_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    """Get or update user settings."""
    user_id = init_session()
    user_data = get_user_data(user_id)
    
    if request.method == 'GET':
        return jsonify({
            'status': 'success',
            'settings': session.get('settings', {}),
            'theme': session.get('theme', 'light'),
            'current_persona': session.get('current_persona', 'ASSISTANT')
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'status': 'error', 'message': 'No data provided'}), 400
            
            # Update settings
            if 'settings' in data:
                session['settings'].update(data['settings'])
            
            if 'theme' in data:
                session['theme'] = data['theme']
            
            if 'persona' in data:
                session['current_persona'] = data['persona']
                # Also update persona manager
                try:
                    persona_enum = PersonaType(data['persona'].upper())
                    persona_manager.set_active_persona(persona_enum)
                except (ValueError, PersonaManagerError) as e:
                    logger.warning(f"Could not set persona {data['persona']}: {e}")
            
            return jsonify({
                'status': 'success',
                'message': 'Settings updated successfully',
                'settings': session.get('settings', {}),
                'theme': session.get('theme', 'light')
            })
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500


# SocketIO Events for Real-time Chat

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    user_id = init_session()
    join_room(user_id)
    logger.info(f"Client connected: {user_id}")
    
    emit('connected', {
        'status': 'success',
        'user_id': user_id,
        'message': 'Connected to DynoAI'
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    user_id = session.get('user_id')
    if user_id:
        leave_room(user_id)
        logger.info(f"Client disconnected: {user_id}")


@socketio.on('start_conversation')
def handle_start_conversation(data):
    """Start a new conversation."""
    user_id = init_session()
    user_data = get_user_data(user_id)
    
    try:
        # Get persona type from data or use current
        persona_type_str = data.get('persona', session.get('current_persona', 'ASSISTANT'))
        persona_type = PersonaType(persona_type_str.upper())
        
        # Create new conversation
        conversation_id = chat_handler.create_conversation(persona_type)
        
        # Store conversation info
        active_conversations[user_id] = conversation_id
        user_data['conversations'][conversation_id] = {
            'title': data.get('title', f'Conversation {len(user_data["conversations"]) + 1}'),
            'created_at': datetime.now().isoformat(),
            'persona': persona_type_str.upper()
        }
        
        # Update session
        session['conversation_count'] = session.get('conversation_count', 0) + 1
        user_data['usage_stats']['conversations_created'] += 1
        
        emit('conversation_started', {
            'status': 'success',
            'conversation_id': conversation_id,
            'persona': persona_type_str.upper(),
            'message': f'New conversation started with {persona_type_str} persona'
        })
        
        logger.info(f"New conversation started: {conversation_id} for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        emit('error', {
            'status': 'error',
            'message': f'Failed to start conversation: {str(e)}'
        })


@socketio.on('send_message')
def handle_send_message(data):
    """Handle incoming chat message with streaming response."""
    user_id = init_session()
    user_data = get_user_data(user_id)
    
    try:
        message = data.get('message', '').strip()
        if not message:
            emit('error', {'status': 'error', 'message': 'Empty message'})
            return
        
        # Get or create conversation
        conversation_id = active_conversations.get(user_id)
        if not conversation_id:
            # Auto-create conversation if none exists
            persona_type_str = session.get('current_persona', 'ASSISTANT')
            persona_type = PersonaType(persona_type_str.upper())
            conversation_id = chat_handler.create_conversation(persona_type)
            active_conversations[user_id] = conversation_id
            user_data['conversations'][conversation_id] = {
                'title': f'Auto-conversation {len(user_data["conversations"]) + 1}',
                'created_at': datetime.now().isoformat(),
                'persona': persona_type_str.upper()
            }
        
        # Check if streaming is enabled
        enable_streaming = session.get('settings', {}).get('enable_streaming', True)
        
        if enable_streaming:
            # Send message with streaming response
            try:
                response_stream = chat_handler.send_message(
                    conversation_id, 
                    message, 
                    stream=True
                )
                
                # Emit message received confirmation
                emit('message_received', {
                    'status': 'success',
                    'conversation_id': conversation_id,
                    'message': message,
                    'streaming': True
                })
                
                # Stream the response
                full_response = ""
                for chunk in response_stream:
                    if isinstance(chunk, StreamingResponse):
                        if chunk.status == StreamingStatus.STREAMING:
                            full_response += chunk.content
                            emit('message_chunk', {
                                'conversation_id': conversation_id,
                                'content': chunk.content,
                                'status': 'streaming'
                            })
                        elif chunk.status == StreamingStatus.COMPLETE:
                            emit('message_complete', {
                                'conversation_id': conversation_id,
                                'full_response': full_response,
                                'tokens_used': chunk.tokens_used,
                                'status': 'complete'
                            })
                            break
                        elif chunk.status == StreamingStatus.ERROR:
                            emit('error', {
                                'status': 'error',
                                'message': f'Streaming error: {chunk.content}'
                            })
                            break
                
                # Update usage stats
                user_data['usage_stats']['total_messages'] += 1
                
            except Exception as e:
                logger.error(f"Error in streaming response: {e}")
                emit('error', {
                    'status': 'error',
                    'message': f'Streaming failed: {str(e)}'
                })
        
        else:
            # Send message without streaming
            try:
                response = chat_handler.send_message(conversation_id, message, stream=False)
                
                emit('message_response', {
                    'status': 'success',
                    'conversation_id': conversation_id,
                    'user_message': message,
                    'ai_response': response,
                    'streaming': False
                })
                
                # Update usage stats
                user_data['usage_stats']['total_messages'] += 1
                
            except Exception as e:
                logger.error(f"Error in non-streaming response: {e}")
                emit('error', {
                    'status': 'error',
                    'message': f'Message failed: {str(e)}'
                })
    
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        emit('error', {
            'status': 'error',
            'message': f'Failed to process message: {str(e)}'
        })


@socketio.on('switch_persona')
def handle_switch_persona(data):
    """Handle persona switching during conversation."""
    user_id = init_session()
    
    try:
        persona_type_str = data.get('persona', 'ASSISTANT')
        persona_type = PersonaType(persona_type_str.upper())
        
        # Get current conversation
        conversation_id = active_conversations.get(user_id)
        if conversation_id:
            # Switch persona for current conversation
            chat_handler.switch_persona(conversation_id, persona_type)
        
        # Update persona manager
        persona_manager.set_active_persona(persona_type)
        session['current_persona'] = persona_type_str.upper()
        
        emit('persona_switched', {
            'status': 'success',
            'persona': persona_type_str.upper(),
            'conversation_id': conversation_id,
            'message': f'Switched to {persona_type_str} persona'
        })
        
        logger.info(f"Persona switched to {persona_type_str} for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error switching persona: {e}")
        emit('error', {
            'status': 'error',
            'message': f'Failed to switch persona: {str(e)}'
        })


@socketio.on('get_conversation_history')
def handle_get_history(data):
    """Get conversation history."""
    user_id = init_session()
    
    try:
        conversation_id = data.get('conversation_id') or active_conversations.get(user_id)
        if not conversation_id:
            emit('error', {'status': 'error', 'message': 'No conversation found'})
            return
        
        history = chat_handler.get_conversation_history(conversation_id)
        if history:
            emit('conversation_history', {
                'status': 'success',
                'conversation_id': conversation_id,
                'history': history
            })
        else:
            emit('error', {'status': 'error', 'message': 'Conversation not found'})
    
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        emit('error', {
            'status': 'error',
            'message': f'Failed to get history: {str(e)}'
        })


# Error Handlers

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('base.html', 
                         error_message="Page not found",
                         error_code=404), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return render_template('base.html',
                         error_message="Internal server error",
                         error_code=500), 500


@app.errorhandler(DynoAIError)
def handle_dynoai_error(error):
    """Handle custom DynoAI errors."""
    logger.error(f"DynoAI error: {error}")
    return jsonify({
        'status': 'error',
        'message': str(error)
    }), 400


# Application Initialization

def create_app(config_name=None):
    """Application factory function."""
    app_config = get_config(config_name)
    app.config.from_object(app_config)
    
    # Validate environment
    if not validate_environment():
        logger.error("Environment validation failed")
        raise DynoAIError("Invalid environment configuration")
    
    logger.info(f"DynoAI application created with {config_name or 'default'} configuration")
    return app


if __name__ == '__main__':
    # Validate environment before starting
    if not validate_environment():
        logger.error("Environment validation failed. Please check your configuration.")
        exit(1)
    
    # Log startup information
    logger.info("Starting DynoAI application...")
    logger.info(f"Debug mode: {app.debug}")
    logger.info(f"Configuration: {config.__class__.__name__}")
    
    # Start the application
    try:
        socketio.run(
            app,
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG,
            allow_unsafe_werkzeug=True  # For development only
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        exit(1)