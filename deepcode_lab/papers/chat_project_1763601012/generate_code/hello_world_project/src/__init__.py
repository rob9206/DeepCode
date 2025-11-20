"""
Hello World Project - Source Package

A simple yet extensible hello world implementation with modular architecture.
This package provides greeting functionality with customizable messages and output formats.
"""

__version__ = "1.0.0"
__author__ = "Hello World Project"
__description__ = "A modular hello world implementation"

# Import main functionality for easy access
from .greeting import HelloWorld, print_greeting, get_greeting
from .utils import format_message, get_timestamp

__all__ = [
    "HelloWorld",
    "print_greeting", 
    "get_greeting",
    "format_message",
    "get_timestamp"
]