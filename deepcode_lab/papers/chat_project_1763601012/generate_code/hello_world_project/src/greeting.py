"""
Greeting Module - Core Hello World Functionality

This module provides the main greeting functionality for the Hello World project.
It includes a HelloWorld class and utility functions for printing and getting greetings.
"""

import sys
from typing import Optional, Dict, Any
try:
    from colorama import Fore, Style, init
    # Initialize colorama for cross-platform colored output
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Fallback color constants
    class Fore:
        GREEN = ""
        BLUE = ""
        RED = ""
        YELLOW = ""
        MAGENTA = ""
        CYAN = ""
    
    class Style:
        BRIGHT = ""
        RESET_ALL = ""


class HelloWorld:
    """
    A configurable Hello World class that supports different greeting styles and colors.
    """
    
    def __init__(self, message: str = "Hello World", color: str = "green", style: str = "normal"):
        """
        Initialize HelloWorld instance.
        
        Args:
            message (str): The greeting message to display
            color (str): Color for the output (green, blue, red, yellow, magenta, cyan)
            style (str): Style for the output (normal, bright)
        """
        self.message = message
        self.color = color.lower()
        self.style = style.lower()
        
        # Color mapping
        self.color_map = {
            "green": Fore.GREEN,
            "blue": Fore.BLUE,
            "red": Fore.RED,
            "yellow": Fore.YELLOW,
            "magenta": Fore.MAGENTA,
            "cyan": Fore.CYAN,
        }
        
        # Style mapping
        self.style_map = {
            "normal": "",
            "bright": Style.BRIGHT,
        }
    
    def get_colored_message(self) -> str:
        """
        Get the greeting message with color and style formatting.
        
        Returns:
            str: Formatted greeting message
        """
        if not COLORAMA_AVAILABLE:
            return self.message
        
        color_code = self.color_map.get(self.color, "")
        style_code = self.style_map.get(self.style, "")
        
        return f"{style_code}{color_code}{self.message}{Style.RESET_ALL}"
    
    def print_greeting(self, file=None) -> None:
        """
        Print the greeting message to the specified file or stdout.
        
        Args:
            file: File object to write to (defaults to sys.stdout)
        """
        if file is None:
            file = sys.stdout
        
        print(self.get_colored_message(), file=file)
    
    def get_greeting(self) -> str:
        """
        Get the plain greeting message without formatting.
        
        Returns:
            str: Plain greeting message
        """
        return self.message
    
    def set_message(self, message: str) -> None:
        """
        Update the greeting message.
        
        Args:
            message (str): New greeting message
        """
        self.message = message
    
    def set_color(self, color: str) -> None:
        """
        Update the color for the greeting.
        
        Args:
            color (str): New color name
        """
        self.color = color.lower()
    
    def set_style(self, style: str) -> None:
        """
        Update the style for the greeting.
        
        Args:
            style (str): New style name
        """
        self.style = style.lower()


# Convenience functions for quick usage
def print_greeting(message: str = "Hello World", 
                  color: str = "green", 
                  style: str = "normal",
                  file=None) -> None:
    """
    Print a greeting message with optional color and style.
    
    Args:
        message (str): The greeting message to display
        color (str): Color for the output
        style (str): Style for the output
        file: File object to write to (defaults to sys.stdout)
    """
    hello = HelloWorld(message, color, style)
    hello.print_greeting(file)


def get_greeting(message: str = "Hello World") -> str:
    """
    Get a plain greeting message.
    
    Args:
        message (str): The greeting message
        
    Returns:
        str: The greeting message
    """
    hello = HelloWorld(message)
    return hello.get_greeting()


def get_available_colors() -> list:
    """
    Get list of available colors.
    
    Returns:
        list: Available color names
    """
    return ["green", "blue", "red", "yellow", "magenta", "cyan"]


def get_available_styles() -> list:
    """
    Get list of available styles.
    
    Returns:
        list: Available style names
    """
    return ["normal", "bright"]


# Demo function for testing
def demo() -> None:
    """
    Demonstrate different greeting styles and colors.
    """
    print("=== Hello World Demo ===")
    print()
    
    # Basic greeting
    print("1. Basic greeting:")
    print_greeting()
    print()
    
    # Different colors
    print("2. Different colors:")
    colors = get_available_colors()
    for color in colors:
        print_greeting(f"Hello World in {color}!", color=color)
    print()
    
    # Different styles
    print("3. Different styles:")
    print_greeting("Hello World - Normal Style", style="normal")
    print_greeting("Hello World - Bright Style", style="bright")
    print()
    
    # Custom messages
    print("4. Custom messages:")
    custom_messages = [
        "Greetings from Python!",
        "Welcome to the Hello World Project!",
        "Bonjour le monde!",
        "¡Hola mundo!"
    ]
    
    for i, msg in enumerate(custom_messages):
        color = colors[i % len(colors)]
        print_greeting(msg, color=color)
    print()
    
    # Using HelloWorld class
    print("5. Using HelloWorld class:")
    hw = HelloWorld("Hello from the class!", color="cyan", style="bright")
    hw.print_greeting()
    
    # Updating message
    hw.set_message("Updated message!")
    hw.set_color("magenta")
    hw.print_greeting()


if __name__ == "__main__":
    # Run demo if script is executed directly
    demo()