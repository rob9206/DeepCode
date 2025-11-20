"""
Configuration Settings for Hello World Project

This module contains configuration settings and constants used throughout
the Hello World project. It provides default values and customizable options.
"""

import os
from typing import Dict, Any, List

# Project Information
PROJECT_NAME = "Hello World Project"
PROJECT_VERSION = "1.0.0"
PROJECT_DESCRIPTION = "A modular greeting system with customizable colors and styles"
PROJECT_AUTHOR = "Hello World Team"

# Default Greeting Settings
DEFAULT_MESSAGE = "Hello World"
DEFAULT_COLOR = "green"
DEFAULT_STYLE = "normal"

# Available Options
AVAILABLE_COLORS = [
    "green", "blue", "red", "yellow", "magenta", "cyan"
]

AVAILABLE_STYLES = [
    "normal", "bright"
]

# Color Codes (for reference and validation)
COLOR_CODES = {
    "green": "\033[92m",
    "blue": "\033[94m", 
    "red": "\033[91m",
    "yellow": "\033[93m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
}

# Style Codes
STYLE_CODES = {
    "normal": "",
    "bright": "\033[1m",
    "reset": "\033[0m"
}

# CLI Configuration
CLI_CONFIG = {
    "prog_name": "hello_world",
    "description": f"{PROJECT_NAME} - {PROJECT_DESCRIPTION}",
    "version": PROJECT_VERSION,
    "epilog": """
Examples:
  python main.py                           # Basic hello world
  python main.py -m "Greetings!"          # Custom message
  python main.py -c blue -s bright        # Blue bright text
  python main.py --demo                    # Run demonstration
  python main.py --interactive             # Interactive mode
  python main.py --banner "WELCOME"       # Create a banner
    """
}

# Banner Configuration
BANNER_CONFIG = {
    "default_width": 60,
    "border_char": "=",
    "padding": 2,
    "center_text": True
}

# Interactive Mode Configuration
INTERACTIVE_CONFIG = {
    "welcome_message": "Welcome to the Hello World Interactive Mode!",
    "instructions": "You can customize your greeting message, color, and style.",
    "quit_commands": ["quit", "exit", "q"],
    "separator_char": "=",
    "separator_length": 50
}

# Demo Configuration
DEMO_CONFIG = {
    "title": "=== Hello World Demo ===",
    "custom_messages": [
        "Greetings from Python!",
        "Welcome to the Hello World Project!",
        "Bonjour le monde!",
        "¡Hola mundo!",
        "Hallo Welt!",
        "こんにちは世界！"
    ]
}

# File and Directory Configuration
FILE_CONFIG = {
    "log_directory": "logs",
    "output_directory": "output",
    "config_file": "config.ini",
    "default_encoding": "utf-8"
}

# Environment Variables
ENV_CONFIG = {
    "color_env_var": "HELLO_WORLD_COLOR",
    "style_env_var": "HELLO_WORLD_STYLE", 
    "message_env_var": "HELLO_WORLD_MESSAGE",
    "debug_env_var": "HELLO_WORLD_DEBUG"
}

# Testing Configuration
TEST_CONFIG = {
    "test_messages": [
        "Hello World",
        "Test Message",
        "Greetings!",
        "",  # Empty message test
        "A very long message that should still work properly with all formatting options"
    ],
    "test_colors": AVAILABLE_COLORS,
    "test_styles": AVAILABLE_STYLES
}

# Validation Rules
VALIDATION_RULES = {
    "max_message_length": 1000,
    "min_message_length": 0,
    "allowed_characters": None,  # None means all characters allowed
    "strip_whitespace": True
}


class Settings:
    """
    Settings class that provides access to configuration values
    and allows for runtime configuration updates.
    """
    
    def __init__(self):
        """Initialize settings with default values."""
        self.message = DEFAULT_MESSAGE
        self.color = DEFAULT_COLOR
        self.style = DEFAULT_STYLE
        self.debug = self._get_env_bool(ENV_CONFIG["debug_env_var"], False)
        
        # Load environment overrides
        self._load_from_environment()
    
    def _get_env_bool(self, env_var: str, default: bool) -> bool:
        """Get boolean value from environment variable."""
        value = os.getenv(env_var, "").lower()
        if value in ("true", "1", "yes", "on"):
            return True
        elif value in ("false", "0", "no", "off"):
            return False
        return default
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        # Override with environment variables if set
        env_message = os.getenv(ENV_CONFIG["message_env_var"])
        if env_message:
            self.message = env_message
        
        env_color = os.getenv(ENV_CONFIG["color_env_var"])
        if env_color and env_color.lower() in AVAILABLE_COLORS:
            self.color = env_color.lower()
        
        env_style = os.getenv(ENV_CONFIG["style_env_var"])
        if env_style and env_style.lower() in AVAILABLE_STYLES:
            self.style = env_style.lower()
    
    def validate_color(self, color: str) -> bool:
        """Validate if color is available."""
        return color.lower() in AVAILABLE_COLORS
    
    def validate_style(self, style: str) -> bool:
        """Validate if style is available."""
        return style.lower() in AVAILABLE_STYLES
    
    def validate_message(self, message: str) -> bool:
        """Validate message according to validation rules."""
        if not isinstance(message, str):
            return False
        
        length = len(message)
        if length < VALIDATION_RULES["min_message_length"]:
            return False
        if length > VALIDATION_RULES["max_message_length"]:
            return False
        
        return True
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get current configuration as dictionary."""
        return {
            "message": self.message,
            "color": self.color,
            "style": self.style,
            "debug": self.debug,
            "available_colors": AVAILABLE_COLORS,
            "available_styles": AVAILABLE_STYLES
        }
    
    def update_config(self, **kwargs):
        """Update configuration with provided keyword arguments."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key == "color" and not self.validate_color(value):
                    raise ValueError(f"Invalid color: {value}")
                elif key == "style" and not self.validate_style(value):
                    raise ValueError(f"Invalid style: {value}")
                elif key == "message" and not self.validate_message(value):
                    raise ValueError(f"Invalid message: {value}")
                
                setattr(self, key, value)


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def reset_settings():
    """Reset settings to default values."""
    global settings
    settings = Settings()


def load_config_from_file(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a file (placeholder for future implementation).
    
    Args:
        config_path (str): Path to configuration file
        
    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    # This is a placeholder for future file-based configuration
    # Could be implemented to read from JSON, YAML, or INI files
    if os.path.exists(config_path):
        # Implementation would go here
        pass
    
    return {}


def save_config_to_file(config_path: str, config: Dict[str, Any]) -> bool:
    """
    Save configuration to a file (placeholder for future implementation).
    
    Args:
        config_path (str): Path to save configuration
        config (Dict[str, Any]): Configuration to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    # This is a placeholder for future file-based configuration
    # Could be implemented to write to JSON, YAML, or INI files
    try:
        # Implementation would go here
        return True
    except Exception:
        return False


# Utility functions for configuration access
def get_default_message() -> str:
    """Get the default greeting message."""
    return DEFAULT_MESSAGE


def get_available_colors() -> List[str]:
    """Get list of available colors."""
    return AVAILABLE_COLORS.copy()


def get_available_styles() -> List[str]:
    """Get list of available styles."""
    return AVAILABLE_STYLES.copy()


def get_project_info() -> Dict[str, str]:
    """Get project information."""
    return {
        "name": PROJECT_NAME,
        "version": PROJECT_VERSION,
        "description": PROJECT_DESCRIPTION,
        "author": PROJECT_AUTHOR
    }


if __name__ == "__main__":
    # Demo the configuration system
    print(f"=== {PROJECT_NAME} Configuration ===")
    print(f"Version: {PROJECT_VERSION}")
    print(f"Description: {PROJECT_DESCRIPTION}")
    print()
    
    print("Current Settings:")
    config = settings.get_config_dict()
    for key, value in config.items():
        print(f"  {key}: {value}")
    print()
    
    print("Available Colors:", get_available_colors())
    print("Available Styles:", get_available_styles())