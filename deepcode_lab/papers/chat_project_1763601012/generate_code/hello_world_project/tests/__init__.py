"""
Test Package - Hello World Project Tests

This package contains unit tests for the Hello World project.
It includes tests for the greeting functionality, utility functions,
and overall project integration.
"""

# Test package version
__version__ = "1.0.0"

# Import test modules for easier access
try:
    from .test_greeting import *
except ImportError:
    # Handle case where test_greeting module is not yet available
    pass

# Test configuration constants
TEST_MESSAGES = [
    "Hello World",
    "Greetings!",
    "Welcome to Python!",
    "Bonjour le monde!",
    "¡Hola mundo!",
    "Guten Tag Welt!",
    "こんにちは世界",
    "Привет мир",
]

TEST_COLORS = ["green", "blue", "red", "yellow", "magenta", "cyan"]
TEST_STYLES = ["normal", "bright"]

# Test utility functions
def get_test_messages():
    """Get list of test messages for testing."""
    return TEST_MESSAGES.copy()

def get_test_colors():
    """Get list of test colors for testing."""
    return TEST_COLORS.copy()

def get_test_styles():
    """Get list of test styles for testing."""
    return TEST_STYLES.copy()