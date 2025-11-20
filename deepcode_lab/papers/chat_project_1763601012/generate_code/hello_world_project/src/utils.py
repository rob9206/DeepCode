"""
Utility Module - Helper Functions for Hello World Project

This module provides utility functions for message formatting, timestamps,
and other helper functionality used throughout the Hello World project.
"""

import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any, Union


def format_message(message: str, 
                  prefix: str = "", 
                  suffix: str = "", 
                  width: Optional[int] = None,
                  align: str = "left",
                  fill_char: str = " ") -> str:
    """
    Format a message with optional prefix, suffix, and alignment.
    
    Args:
        message (str): The message to format
        prefix (str): Text to add before the message
        suffix (str): Text to add after the message
        width (int, optional): Total width for alignment (None for no padding)
        align (str): Alignment type ('left', 'right', 'center')
        fill_char (str): Character to use for padding
        
    Returns:
        str: Formatted message
    """
    # Combine prefix, message, and suffix
    full_message = f"{prefix}{message}{suffix}"
    
    # Apply alignment if width is specified
    if width is not None and width > len(full_message):
        if align.lower() == "center":
            full_message = full_message.center(width, fill_char)
        elif align.lower() == "right":
            full_message = full_message.rjust(width, fill_char)
        else:  # default to left
            full_message = full_message.ljust(width, fill_char)
    
    return full_message


def get_timestamp(format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Get current timestamp as formatted string.
    
    Args:
        format_string (str): strftime format string
        
    Returns:
        str: Formatted timestamp
    """
    return datetime.now().strftime(format_string)


def get_system_info() -> Dict[str, Any]:
    """
    Get basic system information.
    
    Returns:
        dict: System information including platform, Python version, etc.
    """
    import platform
    
    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
    }


def create_banner(text: str, 
                 char: str = "=", 
                 width: int = 50,
                 padding: int = 2) -> str:
    """
    Create a banner around text.
    
    Args:
        text (str): Text to put in banner
        char (str): Character to use for banner
        width (int): Total width of banner
        padding (int): Padding around text
        
    Returns:
        str: Banner with text
    """
    # Create top and bottom borders
    border = char * width
    
    # Create padded text line
    text_line = format_message(text, width=width-2, align="center")
    text_line = f"{char}{text_line}{char}"
    
    # Create empty padding lines
    empty_line = f"{char}{' ' * (width-2)}{char}"
    
    # Combine all parts
    banner_parts = [border]
    
    # Add padding lines above text
    for _ in range(padding):
        banner_parts.append(empty_line)
    
    # Add text line
    banner_parts.append(text_line)
    
    # Add padding lines below text
    for _ in range(padding):
        banner_parts.append(empty_line)
    
    banner_parts.append(border)
    
    return "\n".join(banner_parts)


def validate_color(color: str) -> bool:
    """
    Validate if a color name is supported.
    
    Args:
        color (str): Color name to validate
        
    Returns:
        bool: True if color is valid, False otherwise
    """
    valid_colors = ["green", "blue", "red", "yellow", "magenta", "cyan"]
    return color.lower() in valid_colors


def validate_style(style: str) -> bool:
    """
    Validate if a style name is supported.
    
    Args:
        style (str): Style name to validate
        
    Returns:
        bool: True if style is valid, False otherwise
    """
    valid_styles = ["normal", "bright"]
    return style.lower() in valid_styles


def safe_input(prompt: str, default: str = "") -> str:
    """
    Safe input function that handles KeyboardInterrupt gracefully.
    
    Args:
        prompt (str): Input prompt to display
        default (str): Default value if input is interrupted
        
    Returns:
        str: User input or default value
    """
    try:
        return input(prompt).strip()
    except KeyboardInterrupt:
        print(f"\nUsing default value: {default}")
        return default
    except EOFError:
        return default


def clear_screen():
    """
    Clear the terminal screen in a cross-platform way.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def print_separator(char: str = "-", width: int = 50):
    """
    Print a separator line.
    
    Args:
        char (str): Character to use for separator
        width (int): Width of separator
    """
    print(char * width)


def get_terminal_width() -> int:
    """
    Get the width of the terminal.
    
    Returns:
        int: Terminal width in characters (default 80 if cannot determine)
    """
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80  # Default fallback


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length with optional suffix.
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length including suffix
        suffix (str): Suffix to add when truncating
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    if len(suffix) >= max_length:
        return suffix[:max_length]
    
    return text[:max_length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def is_interactive() -> bool:
    """
    Check if the script is running in an interactive environment.
    
    Returns:
        bool: True if interactive, False otherwise
    """
    return hasattr(sys, 'ps1') or sys.stdin.isatty()


def get_user_confirmation(prompt: str = "Continue? (y/n): ") -> bool:
    """
    Get user confirmation with y/n prompt.
    
    Args:
        prompt (str): Confirmation prompt
        
    Returns:
        bool: True if user confirms, False otherwise
    """
    if not is_interactive():
        return True  # Auto-confirm in non-interactive mode
    
    while True:
        try:
            response = input(prompt).strip().lower()
            if response in ['y', 'yes', '1', 'true']:
                return True
            elif response in ['n', 'no', '0', 'false']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return False
        except EOFError:
            return False


# Demo function for testing utilities
def demo_utils() -> None:
    """
    Demonstrate utility functions.
    """
    print("=== Utility Functions Demo ===")
    print()
    
    # Message formatting
    print("1. Message Formatting:")
    msg = "Hello World"
    print(f"Original: '{msg}'")
    print(f"With prefix: '{format_message(msg, prefix='>>> ')}'")
    print(f"With suffix: '{format_message(msg, suffix=' <<<')}'")
    print(f"Centered (30): '{format_message(msg, width=30, align='center')}'")
    print(f"Right aligned: '{format_message(msg, width=30, align='right')}'")
    print()
    
    # Timestamp
    print("2. Timestamp:")
    print(f"Current time: {get_timestamp()}")
    print(f"Date only: {get_timestamp('%Y-%m-%d')}")
    print(f"Time only: {get_timestamp('%H:%M:%S')}")
    print()
    
    # Banner
    print("3. Banner:")
    print(create_banner("HELLO WORLD", width=40))
    print()
    
    # System info
    print("4. System Information:")
    info = get_system_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    print()
    
    # Validation
    print("5. Validation:")
    print(f"'green' is valid color: {validate_color('green')}")
    print(f"'purple' is valid color: {validate_color('purple')}")
    print(f"'bright' is valid style: {validate_style('bright')}")
    print(f"'italic' is valid style: {validate_style('italic')}")
    print()
    
    # Text utilities
    print("6. Text Utilities:")
    long_text = "This is a very long text that needs to be truncated"
    print(f"Original: {long_text}")
    print(f"Truncated (20): {truncate_text(long_text, 20)}")
    print()
    
    # File size formatting
    print("7. File Size Formatting:")
    sizes = [0, 512, 1024, 1048576, 1073741824]
    for size in sizes:
        print(f"{size} bytes = {format_file_size(size)}")
    print()
    
    # Terminal info
    print("8. Terminal Information:")
    print(f"Terminal width: {get_terminal_width()} characters")
    print(f"Interactive mode: {is_interactive()}")


if __name__ == "__main__":
    # Run demo if script is executed directly
    demo_utils()