"""
Configuration settings for DynoAI application.
Manages environment variables, API keys, and application settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class with common settings."""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    # AI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    MAX_TOKENS = int(os.environ.get('MAX_TOKENS', '2000'))
    TEMPERATURE = float(os.environ.get('TEMPERATURE', '0.7'))
    
    # Local AI Model Configuration (optional)
    USE_LOCAL_MODEL = os.environ.get('USE_LOCAL_MODEL', 'False').lower() in ['true', '1', 'yes']
    LOCAL_MODEL_PATH = os.environ.get('LOCAL_MODEL_PATH', 'data/models/')
    LOCAL_MODEL_NAME = os.environ.get('LOCAL_MODEL_NAME', 'microsoft/DialoGPT-medium')
    
    # Database Configuration
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'data/conversations/dynoai.db')
    CONVERSATION_HISTORY_LIMIT = int(os.environ.get('CONVERSATION_HISTORY_LIMIT', '50'))
    
    # WebSocket Configuration
    SOCKETIO_ASYNC_MODE = os.environ.get('SOCKETIO_ASYNC_MODE', 'threading')
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.environ.get('SOCKETIO_CORS_ALLOWED_ORIGINS', '*')
    
    # File Storage Configuration
    DATA_DIR = os.environ.get('DATA_DIR', 'data')
    CONVERSATIONS_DIR = os.path.join(DATA_DIR, 'conversations')
    MODELS_DIR = os.path.join(DATA_DIR, 'models')
    
    # Plugin Configuration
    PLUGINS_ENABLED = os.environ.get('PLUGINS_ENABLED', 'True').lower() in ['true', '1', 'yes']
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
    SEARCH_API_KEY = os.environ.get('SEARCH_API_KEY')
    
    # Memory Configuration
    MEMORY_ENABLED = os.environ.get('MEMORY_ENABLED', 'True').lower() in ['true', '1', 'yes']
    MEMORY_CONTEXT_WINDOW = int(os.environ.get('MEMORY_CONTEXT_WINDOW', '10'))
    MEMORY_SUMMARY_THRESHOLD = int(os.environ.get('MEMORY_SUMMARY_THRESHOLD', '20'))
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'True').lower() in ['true', '1', 'yes']
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', '30'))
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'dynoai.log')
    
    @classmethod
    def init_app(cls, app):
        """Initialize application with configuration."""
        # Create necessary directories
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.CONVERSATIONS_DIR, exist_ok=True)
        os.makedirs(cls.MODELS_DIR, exist_ok=True)
        
        # Validate required configuration
        if not cls.OPENAI_API_KEY and not cls.USE_LOCAL_MODEL:
            print("WARNING: No OpenAI API key found and local model not enabled. AI functionality may not work.")
        
        # Set Flask app configuration
        app.config.from_object(cls)


class DevelopmentConfig(Config):
    """Development configuration with debug enabled."""
    DEBUG = True
    SECRET_KEY = 'dev-secret-key'


class ProductionConfig(Config):
    """Production configuration with security settings."""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Production-specific settings
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.environ.get('SOCKETIO_CORS_ALLOWED_ORIGINS', 'https://yourdomain.com')
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Production-specific initialization
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set in production environment")


class TestingConfig(Config):
    """Testing configuration for unit tests."""
    TESTING = True
    DEBUG = True
    DATABASE_PATH = ':memory:'  # Use in-memory database for tests
    PLUGINS_ENABLED = False
    MEMORY_ENABLED = False


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration class based on environment."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])


# AI Model Configuration Presets
AI_MODEL_PRESETS = {
    'creative': {
        'temperature': 0.9,
        'max_tokens': 2500,
        'model': 'gpt-3.5-turbo'
    },
    'balanced': {
        'temperature': 0.7,
        'max_tokens': 2000,
        'model': 'gpt-3.5-turbo'
    },
    'precise': {
        'temperature': 0.3,
        'max_tokens': 1500,
        'model': 'gpt-3.5-turbo'
    },
    'gpt4': {
        'temperature': 0.7,
        'max_tokens': 3000,
        'model': 'gpt-4'
    }
}


# Plugin Configuration
PLUGIN_CONFIGS = {
    'weather': {
        'enabled': True,
        'api_endpoint': 'https://api.openweathermap.org/data/2.5/weather',
        'requires_api_key': True
    },
    'calculator': {
        'enabled': True,
        'safe_mode': True,
        'requires_api_key': False
    },
    'web_search': {
        'enabled': True,
        'api_endpoint': 'https://api.bing.microsoft.com/v7.0/search',
        'requires_api_key': True
    },
    'memory_assistant': {
        'enabled': True,
        'auto_summarize': True,
        'requires_api_key': False
    }
}