"""
Configuration settings for DynoAI platform.
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
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///data/conversations.db'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AI Model API Keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    
    # Local Model Configuration (Ollama)
    OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_DEFAULT_MODEL = os.environ.get('OLLAMA_DEFAULT_MODEL', 'llama2')
    
    # Default AI Parameters
    DEFAULT_TEMPERATURE = float(os.environ.get('DEFAULT_TEMPERATURE', '0.7'))
    DEFAULT_MAX_TOKENS = int(os.environ.get('DEFAULT_MAX_TOKENS', '2048'))
    DEFAULT_MODEL = os.environ.get('DEFAULT_MODEL', 'gpt-3.5-turbo')
    
    # Conversation Settings
    MAX_CONVERSATION_HISTORY = int(os.environ.get('MAX_CONVERSATION_HISTORY', '50'))
    CONVERSATION_CONTEXT_WINDOW = int(os.environ.get('CONVERSATION_CONTEXT_WINDOW', '10'))
    
    # Plugin Configuration
    PLUGINS_ENABLED = os.environ.get('PLUGINS_ENABLED', 'true').lower() == 'true'
    WEB_SEARCH_ENABLED = os.environ.get('WEB_SEARCH_ENABLED', 'true').lower() == 'true'
    CODE_EXECUTION_ENABLED = os.environ.get('CODE_EXECUTION_ENABLED', 'false').lower() == 'true'
    
    # Web Search Configuration
    SEARCH_API_KEY = os.environ.get('SEARCH_API_KEY')  # For services like SerpAPI
    SEARCH_ENGINE_ID = os.environ.get('SEARCH_ENGINE_ID')  # For Google Custom Search
    
    # Security Settings
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', '60'))
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', '3600'))  # 1 hour in seconds
    
    # File Upload Settings
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'dynoai.log')
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        # Create necessary directories
        os.makedirs('data', exist_ok=True)
        os.makedirs('uploads', exist_ok=True)
        os.makedirs('logs', exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration with debug settings."""
    DEBUG = True
    TESTING = False
    
    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/conversations_dev.db'
    
    # Enable all plugins for development
    PLUGINS_ENABLED = True
    WEB_SEARCH_ENABLED = True
    CODE_EXECUTION_ENABLED = True


class ProductionConfig(Config):
    """Production configuration with security settings."""
    DEBUG = False
    TESTING = False
    
    # Use environment variables for production database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///data/conversations_prod.db'
    
    # Stricter security settings
    RATE_LIMIT_PER_MINUTE = 30
    SESSION_TIMEOUT = 1800  # 30 minutes
    
    # Disable code execution in production by default
    CODE_EXECUTION_ENABLED = False


class TestingConfig(Config):
    """Testing configuration for unit tests."""
    TESTING = True
    DEBUG = True
    
    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable external API calls during testing
    WEB_SEARCH_ENABLED = False
    CODE_EXECUTION_ENABLED = False
    
    # Use mock API keys for testing
    OPENAI_API_KEY = 'test-openai-key'
    ANTHROPIC_API_KEY = 'test-anthropic-key'


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
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(config_name, config['default'])


# Model configuration mappings
MODEL_CONFIGS = {
    'openai': {
        'gpt-4': {
            'max_tokens': 8192,
            'temperature_range': (0.0, 2.0),
            'supports_functions': True
        },
        'gpt-3.5-turbo': {
            'max_tokens': 4096,
            'temperature_range': (0.0, 2.0),
            'supports_functions': True
        },
        'gpt-3.5-turbo-16k': {
            'max_tokens': 16384,
            'temperature_range': (0.0, 2.0),
            'supports_functions': True
        }
    },
    'anthropic': {
        'claude-3-opus': {
            'max_tokens': 4096,
            'temperature_range': (0.0, 1.0),
            'supports_functions': False
        },
        'claude-3-sonnet': {
            'max_tokens': 4096,
            'temperature_range': (0.0, 1.0),
            'supports_functions': False
        },
        'claude-instant': {
            'max_tokens': 4096,
            'temperature_range': (0.0, 1.0),
            'supports_functions': False
        }
    },
    'local': {
        'llama2': {
            'max_tokens': 2048,
            'temperature_range': (0.0, 1.0),
            'supports_functions': False
        },
        'codellama': {
            'max_tokens': 2048,
            'temperature_range': (0.0, 1.0),
            'supports_functions': False
        },
        'mistral': {
            'max_tokens': 2048,
            'temperature_range': (0.0, 1.0),
            'supports_functions': False
        }
    }
}


def get_model_config(provider, model_name):
    """Get configuration for a specific model."""
    return MODEL_CONFIGS.get(provider, {}).get(model_name, {
        'max_tokens': 2048,
        'temperature_range': (0.0, 1.0),
        'supports_functions': False
    })


def validate_api_keys():
    """Validate that required API keys are present."""
    config_obj = get_config()()
    
    missing_keys = []
    
    if not config_obj.OPENAI_API_KEY:
        missing_keys.append('OPENAI_API_KEY')
    
    if not config_obj.ANTHROPIC_API_KEY:
        missing_keys.append('ANTHROPIC_API_KEY')
    
    return missing_keys


def create_env_template():
    """Create a template .env file with all configuration options."""
    template = """# DynoAI Configuration Template
# Copy this file to .env and fill in your values

# Flask Configuration
SECRET_KEY=your-secret-key-here
DEBUG=true
FLASK_ENV=development

# Database Configuration
DATABASE_URL=sqlite:///data/conversations.db

# AI Model API Keys
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Local Model Configuration (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama2

# Default AI Parameters
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=2048
DEFAULT_MODEL=gpt-3.5-turbo

# Conversation Settings
MAX_CONVERSATION_HISTORY=50
CONVERSATION_CONTEXT_WINDOW=10

# Plugin Configuration
PLUGINS_ENABLED=true
WEB_SEARCH_ENABLED=true
CODE_EXECUTION_ENABLED=false

# Web Search Configuration
SEARCH_API_KEY=your-search-api-key-here
SEARCH_ENGINE_ID=your-search-engine-id-here

# Security Settings
RATE_LIMIT_PER_MINUTE=60
SESSION_TIMEOUT=3600

# File Upload Settings
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=dynoai.log
"""
    
    return template