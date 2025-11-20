"""
Configuration management for DynoAI application.
Loads settings from environment variables and provides configuration classes.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with common settings."""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Server Configuration
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', 5000))
    
    # AI Provider Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    DEFAULT_AI_PROVIDER = os.getenv('DEFAULT_AI_PROVIDER', 'openai')
    
    # AI Model Configuration
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
    DEFAULT_TEMPERATURE = float(os.getenv('DEFAULT_TEMPERATURE', '0.7'))
    DEFAULT_MAX_TOKENS = int(os.getenv('DEFAULT_MAX_TOKENS', '1000'))
    
    # Application Features
    ENABLE_PERSONAS = os.getenv('ENABLE_PERSONAS', 'True').lower() == 'true'
    ENABLE_CONVERSATION_HISTORY = os.getenv('ENABLE_CONVERSATION_HISTORY', 'True').lower() == 'true'
    ENABLE_STREAMING = os.getenv('ENABLE_STREAMING', 'True').lower() == 'true'
    ENABLE_EXPORT = os.getenv('ENABLE_EXPORT', 'True').lower() == 'true'
    
    # Conversation Settings
    MAX_CONVERSATION_HISTORY = int(os.getenv('MAX_CONVERSATION_HISTORY', '50'))
    MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', '4000'))
    
    # UI Configuration
    DEFAULT_THEME = os.getenv('DEFAULT_THEME', 'dark')
    APP_NAME = os.getenv('APP_NAME', 'DynoAI')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    
    # Session Configuration
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '3600'))  # 1 hour
    
    @classmethod
    def validate_config(cls):
        """Validate critical configuration settings."""
        errors = []
        
        # Check for required API keys
        if not cls.OPENAI_API_KEY and not cls.ANTHROPIC_API_KEY:
            errors.append("At least one AI provider API key must be configured (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
        
        # Validate default provider
        if cls.DEFAULT_AI_PROVIDER not in ['openai', 'anthropic']:
            errors.append("DEFAULT_AI_PROVIDER must be either 'openai' or 'anthropic'")
        
        # Check if default provider has API key
        if cls.DEFAULT_AI_PROVIDER == 'openai' and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required when DEFAULT_AI_PROVIDER is 'openai'")
        elif cls.DEFAULT_AI_PROVIDER == 'anthropic' and not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is required when DEFAULT_AI_PROVIDER is 'anthropic'")
        
        # Validate numeric ranges
        if not (0.0 <= cls.DEFAULT_TEMPERATURE <= 2.0):
            errors.append("DEFAULT_TEMPERATURE must be between 0.0 and 2.0")
        
        if cls.DEFAULT_MAX_TOKENS <= 0:
            errors.append("DEFAULT_MAX_TOKENS must be greater than 0")
        
        if cls.MAX_CONVERSATION_HISTORY <= 0:
            errors.append("MAX_CONVERSATION_HISTORY must be greater than 0")
        
        if cls.MAX_MESSAGE_LENGTH <= 0:
            errors.append("MAX_MESSAGE_LENGTH must be greater than 0")
        
        return errors
    
    @classmethod
    def get_ai_config(cls, provider=None):
        """Get AI configuration for specified provider."""
        provider = provider or cls.DEFAULT_AI_PROVIDER
        
        config = {
            'temperature': cls.DEFAULT_TEMPERATURE,
            'max_tokens': cls.DEFAULT_MAX_TOKENS,
        }
        
        if provider == 'openai':
            config.update({
                'api_key': cls.OPENAI_API_KEY,
                'model': cls.OPENAI_MODEL,
                'provider': 'openai'
            })
        elif provider == 'anthropic':
            config.update({
                'api_key': cls.ANTHROPIC_API_KEY,
                'model': cls.ANTHROPIC_MODEL,
                'provider': 'anthropic'
            })
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
        
        return config
    
    @classmethod
    def get_available_providers(cls):
        """Get list of available AI providers based on configured API keys."""
        providers = []
        if cls.OPENAI_API_KEY:
            providers.append('openai')
        if cls.ANTHROPIC_API_KEY:
            providers.append('anthropic')
        return providers


class DevelopmentConfig(Config):
    """Development configuration with debug settings."""
    DEBUG = True
    
    # Override for development
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-unsafe-for-production')


class ProductionConfig(Config):
    """Production configuration with security settings."""
    DEBUG = False
    
    # Ensure secret key is set in production
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    @classmethod
    def validate_config(cls):
        """Additional validation for production."""
        errors = super().validate_config()
        
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            errors.append("SECRET_KEY must be set to a secure value in production")
        
        return errors


class TestingConfig(Config):
    """Testing configuration for unit tests."""
    TESTING = True
    DEBUG = True
    
    # Use test-specific settings
    SECRET_KEY = 'test-secret-key'
    OPENAI_API_KEY = 'test-openai-key'
    ANTHROPIC_API_KEY = 'test-anthropic-key'
    
    # Disable external features for testing
    ENABLE_STREAMING = False
    MAX_CONVERSATION_HISTORY = 10


# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration class based on environment or name."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    return config_map.get(config_name, config_map['default'])


def validate_environment():
    """Validate the current environment configuration."""
    config_class = get_config()
    errors = config_class.validate_config()
    
    if errors:
        print("Configuration Validation Errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("Configuration validation passed.")
    return True


# Export commonly used configuration
current_config = get_config()