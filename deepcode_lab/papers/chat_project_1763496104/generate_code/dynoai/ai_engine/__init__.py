"""
AI Engine Package - DynoAI Application

This package provides the core AI functionality for the DynoAI application,
including conversation handling, persona management, and prompt engineering.

Main Components:
- ChatHandler: Manages AI conversations and API interactions
- PersonaManager: Handles AI personality profiles and behaviors
- PromptTemplates: Provides structured prompts for different AI personas

Usage:
    from ai_engine import ChatHandler, PersonaManager
    
    # Initialize chat handler
    chat_handler = ChatHandler()
    
    # Get available personas
    persona_manager = PersonaManager()
    personas = persona_manager.get_available_personas()
"""

from .chat_handler import ChatHandler
from .persona_manager import PersonaManager
from .prompt_templates import PromptTemplates

# Package version
__version__ = "1.0.0"

# Package metadata
__author__ = "DynoAI Team"
__description__ = "AI Engine for Dynamic AI Assistant Application"

# Public API exports
__all__ = [
    'ChatHandler',
    'PersonaManager', 
    'PromptTemplates',
    'get_default_chat_handler',
    'get_persona_manager',
    'initialize_ai_engine'
]

# Global instances for easy access
_chat_handler_instance = None
_persona_manager_instance = None

def get_default_chat_handler():
    """
    Get the default ChatHandler instance (singleton pattern).
    
    Returns:
        ChatHandler: The default chat handler instance
    """
    global _chat_handler_instance
    if _chat_handler_instance is None:
        _chat_handler_instance = ChatHandler()
    return _chat_handler_instance

def get_persona_manager():
    """
    Get the PersonaManager instance (singleton pattern).
    
    Returns:
        PersonaManager: The persona manager instance
    """
    global _persona_manager_instance
    if _persona_manager_instance is None:
        _persona_manager_instance = PersonaManager()
    return _persona_manager_instance

def initialize_ai_engine(config=None):
    """
    Initialize the AI engine with optional configuration.
    
    Args:
        config: Optional configuration object
        
    Returns:
        dict: Initialization status and component info
    """
    try:
        # Initialize components
        chat_handler = get_default_chat_handler()
        persona_manager = get_persona_manager()
        
        # Validate configuration if provided
        if config:
            chat_handler.update_config(config)
        
        return {
            'status': 'success',
            'message': 'AI Engine initialized successfully',
            'components': {
                'chat_handler': True,
                'persona_manager': True,
                'prompt_templates': True
            },
            'available_personas': persona_manager.get_available_personas(),
            'ai_providers': chat_handler.get_available_providers()
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'AI Engine initialization failed: {str(e)}',
            'components': {
                'chat_handler': False,
                'persona_manager': False,
                'prompt_templates': False
            }
        }

def reset_ai_engine():
    """
    Reset all AI engine instances (useful for testing).
    """
    global _chat_handler_instance, _persona_manager_instance
    _chat_handler_instance = None
    _persona_manager_instance = None

# Package-level configuration
AI_ENGINE_CONFIG = {
    'default_provider': 'openai',
    'max_retries': 3,
    'timeout': 30,
    'streaming_enabled': True,
    'conversation_history_limit': 100
}

# Error classes for the AI engine
class AIEngineError(Exception):
    """Base exception for AI Engine errors."""
    pass

class ChatHandlerError(AIEngineError):
    """Exception raised by ChatHandler operations."""
    pass

class PersonaManagerError(AIEngineError):
    """Exception raised by PersonaManager operations."""
    pass

class PromptTemplateError(AIEngineError):
    """Exception raised by PromptTemplate operations."""
    pass

# Utility functions
def get_engine_info():
    """
    Get information about the AI engine package.
    
    Returns:
        dict: Package information
    """
    return {
        'name': 'DynoAI AI Engine',
        'version': __version__,
        'author': __author__,
        'description': __description__,
        'components': __all__,
        'config': AI_ENGINE_CONFIG
    }

def validate_ai_providers():
    """
    Validate that required AI providers are available.
    
    Returns:
        dict: Validation results for each provider
    """
    results = {}
    
    try:
        import openai
        results['openai'] = {
            'available': True,
            'version': openai.__version__
        }
    except ImportError:
        results['openai'] = {
            'available': False,
            'error': 'OpenAI package not installed'
        }
    
    try:
        import anthropic
        results['anthropic'] = {
            'available': True,
            'version': anthropic.__version__
        }
    except ImportError:
        results['anthropic'] = {
            'available': False,
            'error': 'Anthropic package not installed (optional)'
        }
    
    return results

# Initialize logging for the AI engine
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler if no handlers exist
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

logger.info("AI Engine package loaded successfully")