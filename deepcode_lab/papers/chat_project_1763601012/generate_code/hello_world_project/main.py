#!/usr/bin/env python3
"""
Hello World Project - Main Entry Point

This is the main entry point for the Hello World project.
It provides a command-line interface for running different greeting styles
and demonstrates the project's functionality.
"""

import sys
import argparse
from typing import Optional

# Import our project modules
try:
    from src import HelloWorld, print_greeting, get_greeting
    from src.greeting import get_available_colors, get_available_styles, demo
    from src.utils import (
        create_banner, get_timestamp, format_message, 
        get_user_confirmation, clear_screen, print_separator
    )
except ImportError as e:
    print(f"Error importing project modules: {e}")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)


def create_cli_parser() -> argparse.ArgumentParser:
    """
    Create and configure the command-line argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Hello World Project - A modular greeting system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Basic hello world
  python main.py -m "Greetings!"          # Custom message
  python main.py -c blue -s bright        # Blue bright text
  python main.py --demo                    # Run demonstration
  python main.py --interactive             # Interactive mode
  python main.py --banner "WELCOME"       # Create a banner
        """
    )
    
    # Message options
    parser.add_argument(
        "-m", "--message",
        type=str,
        default="Hello World",
        help="Custom greeting message (default: 'Hello World')"
    )
    
    # Color options
    parser.add_argument(
        "-c", "--color",
        type=str,
        default="green",
        choices=get_available_colors(),
        help="Text color (default: green)"
    )
    
    # Style options
    parser.add_argument(
        "-s", "--style",
        type=str,
        default="normal",
        choices=get_available_styles(),
        help="Text style (default: normal)"
    )
    
    # Mode options
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run the greeting demonstration"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--banner",
        type=str,
        help="Create a banner with the specified text"
    )
    
    # Output options
    parser.add_argument(
        "--timestamp",
        action="store_true",
        help="Include timestamp with the greeting"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress extra output (just print the greeting)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Hello World Project v1.0.0"
    )
    
    return parser


def interactive_mode():
    """
    Run the program in interactive mode, allowing user to customize greetings.
    """
    print(create_banner("INTERACTIVE MODE", width=60))
    print()
    print("Welcome to the Hello World Interactive Mode!")
    print("You can customize your greeting message, color, and style.")
    print("Type 'quit' or 'exit' to leave interactive mode.")
    print()
    
    while True:
        try:
            print_separator("=", 50)
            
            # Get message
            message = input("Enter your message (or 'quit' to exit): ").strip()
            if message.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not message:
                message = "Hello World"
            
            # Get color
            print(f"Available colors: {', '.join(get_available_colors())}")
            color = input("Choose a color (default: green): ").strip().lower()
            if not color or color not in get_available_colors():
                color = "green"
            
            # Get style
            print(f"Available styles: {', '.join(get_available_styles())}")
            style = input("Choose a style (default: normal): ").strip().lower()
            if not style or style not in get_available_styles():
                style = "normal"
            
            # Display the greeting
            print("\nYour greeting:")
            print_greeting(message, color=color, style=style)
            print()
            
            # Ask if user wants to continue
            if not get_user_confirmation("Create another greeting? (y/n): "):
                print("Goodbye!")
                break
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break


def main():
    """
    Main function that handles command-line arguments and executes the appropriate functionality.
    """
    parser = create_cli_parser()
    args = parser.parse_args()
    
    try:
        # Handle special modes first
        if args.demo:
            if not args.quiet:
                print(create_banner("HELLO WORLD DEMO", width=60))
                print()
            demo()
            return
        
        if args.interactive:
            interactive_mode()
            return
        
        if args.banner:
            banner = create_banner(args.banner, width=60)
            print(banner)
            return
        
        # Handle regular greeting
        if not args.quiet:
            print(create_banner("HELLO WORLD PROJECT", width=60))
            print()
        
        # Add timestamp if requested
        if args.timestamp:
            timestamp = get_timestamp()
            if not args.quiet:
                print(f"Generated at: {timestamp}")
                print()
        
        # Print the main greeting
        if not args.quiet:
            print("Your greeting:")
        
        print_greeting(args.message, color=args.color, style=args.style)
        
        if not args.quiet:
            print()
            print("Thank you for using Hello World Project!")
            print("Use --help for more options or --demo for a demonstration.")
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def simple_hello_world():
    """
    Simple function that just prints "Hello World" - the core requirement.
    This can be called directly for the most basic functionality.
    """
    print("Hello World")


if __name__ == "__main__":
    # If no command line arguments are provided, just run simple hello world
    if len(sys.argv) == 1:
        simple_hello_world()
    else:
        main()