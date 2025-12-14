"""
DeepCode - AI Research Engine

Streamlit Web Interface Main Application File
"""

import os
import sys

# Fix UTF-8 encoding for Windows console at the very start
if sys.platform == 'win32':
    # Attempt to set UTF-8 encoding
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

    # Always wrap print on Windows to catch any remaining UnicodeEncodeError
    _original_print = print
    def print(*args, **kwargs):
        try:
            _original_print(*args, **kwargs)
        except UnicodeEncodeError:
            # Fallback: encode with errors='replace'
            safe_args = []
            for arg in args:
                if isinstance(arg, str):
                    # Replace unencodable characters
                    encoding = sys.stdout.encoding or 'ascii'
                    safe_args.append(arg.encode(encoding, errors='replace').decode(encoding))
                else:
                    safe_args.append(arg)
            try:
                _original_print(*safe_args, **kwargs)
            except Exception:
                # If it still fails, purely ascii fallback
                ascii_args = [
                    str(a).encode('ascii', errors='replace').decode('ascii') 
                    for a in args
                ]
                _original_print(*ascii_args, **kwargs)

    import builtins
    builtins.print = print

# Disable .pyc file generation
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

# Apply nest_asyncio early to support nested event loops
import nest_asyncio
nest_asyncio.apply()

# Add parent directory to path for module imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import UI modules
from ui.layout import main_layout


def main():
    """
    Main function - Streamlit application entry

    All UI logic has been modularized into ui/ folder
    """
    # Run main layout
    sidebar_info = main_layout()

    # Additional global logic can be added here if needed

    return sidebar_info


if __name__ == "__main__":
    main()
