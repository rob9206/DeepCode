# Hello World Project

A modular, extensible "Hello World" program built with Python that demonstrates best practices in software development. This project transforms the simple concept of printing "Hello World" into a comprehensive, configurable greeting system.

## 🌟 Features

- **Customizable Messages**: Create personalized greetings beyond "Hello World"
- **Colored Output**: Support for multiple colors using colorama library
- **Text Styling**: Normal and bright text styles
- **Command-Line Interface**: Rich CLI with multiple options and modes
- **Interactive Mode**: User-friendly interactive greeting creation
- **Demo Mode**: Showcase all available features
- **Banner Creation**: Generate decorative text banners
- **Configuration System**: Flexible settings management
- **Modular Architecture**: Well-organized, extensible codebase
- **Unit Testing**: Comprehensive test suite
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Basic Usage

```bash
# Simple hello world
python main.py

# Custom message
python main.py -m "Greetings from Python!"

# Colored output
python main.py -c blue -s bright

# Interactive mode
python main.py --interactive

# Demo all features
python main.py --demo
```

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone or download the project**:
   ```bash
   git clone <repository-url>
   cd hello_world_project
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the program**:
   ```bash
   python main.py
   ```

### Package Installation

You can also install the project as a package:

```bash
pip install -e .
```

## 🎯 Usage Examples

### Command Line Options

```bash
# Basic greeting
python main.py
# Output: Hello World

# Custom message with color and style
python main.py -m "Welcome!" -c cyan -s bright

# Create a banner
python main.py --banner "HELLO WORLD"

# Include timestamp
python main.py --timestamp

# Quiet mode (just the greeting)
python main.py --quiet

# Get help
python main.py --help

# Show version
python main.py --version
```

### Available Colors

- `green` (default)
- `blue`
- `red`
- `yellow`
- `magenta`
- `cyan`

### Available Styles

- `normal` (default)
- `bright`

### Interactive Mode

```bash
python main.py --interactive
```

Interactive mode allows you to:
- Enter custom messages
- Choose colors and styles
- Create multiple greetings in one session
- Get real-time feedback

### Demo Mode

```bash
python main.py --demo
```

Demo mode showcases:
- Basic greeting functionality
- All available colors
- Different text styles
- Custom message examples
- HelloWorld class usage

## 🏗️ Project Structure

```
hello_world_project/
├── main.py                 # Entry point with CLI interface
├── src/                    # Source code directory
│   ├── __init__.py         # Package initialization
│   ├── greeting.py         # Core greeting functionality
│   └── utils.py           # Utility functions
├── tests/                  # Test directory
│   ├── __init__.py         # Test package initialization
│   └── test_greeting.py    # Unit tests
├── config/                 # Configuration directory
│   └── settings.py         # Configuration settings
├── requirements.txt        # Project dependencies
├── setup.py               # Package setup configuration
├── .gitignore             # Git ignore file
└── README.md              # This file
```

## 🔧 Configuration

The project supports configuration through:

### Environment Variables

```bash
export HELLO_WORLD_MESSAGE="Custom Default Message"
export HELLO_WORLD_COLOR="blue"
export HELLO_WORLD_STYLE="bright"
export HELLO_WORLD_DEBUG="true"
```

### Configuration File

Settings can be customized in `config/settings.py`:

```python
# Default settings
DEFAULT_MESSAGE = "Hello World"
DEFAULT_COLOR = "green"
DEFAULT_STYLE = "normal"

# Available options
AVAILABLE_COLORS = ["green", "blue", "red", "yellow", "magenta", "cyan"]
AVAILABLE_STYLES = ["normal", "bright"]
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_greeting.py

# Run with coverage
python -m pytest tests/ --cov=src
```

## 📚 API Reference

### HelloWorld Class

```python
from src.greeting import HelloWorld

# Create instance
hw = HelloWorld("Custom message", color="blue", style="bright")

# Print greeting
hw.print_greeting()

# Get formatted message
formatted = hw.get_colored_message()

# Update properties
hw.set_message("New message")
hw.set_color("red")
hw.set_style("normal")
```

### Convenience Functions

```python
from src.greeting import print_greeting, get_greeting

# Quick greeting
print_greeting("Hello!", color="cyan", style="bright")

# Get plain message
message = get_greeting("Hello World")
```

### Utility Functions

```python
from src.utils import create_banner, format_message, get_timestamp

# Create banner
banner = create_banner("WELCOME", width=50)

# Format message
formatted = format_message("Hello", prefix=">>> ", width=20, align="center")

# Get timestamp
timestamp = get_timestamp("%Y-%m-%d %H:%M:%S")
```

## 🎨 Customization

### Adding New Colors

1. Update `AVAILABLE_COLORS` in `config/settings.py`
2. Add color mapping in `src/greeting.py`
3. Update CLI choices in `main.py`

### Adding New Styles

1. Update `AVAILABLE_STYLES` in `config/settings.py`
2. Add style mapping in `src/greeting.py`
3. Update CLI choices in `main.py`

### Custom Message Formats

Extend the `format_message` function in `src/utils.py` to add new formatting options.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`python -m pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Run tests
python -m pytest tests/ -v

# Check code style (if using flake8)
flake8 src/ tests/

# Run the demo
python main.py --demo
```

## 📋 Requirements

- **Python**: 3.8+
- **colorama**: >=0.4.6 (for colored terminal output)
- **pytest**: >=7.0.0 (for testing, development only)

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure you're running from the project root directory
   - Check that all dependencies are installed: `pip install -r requirements.txt`

2. **Colors Not Working**:
   - Install colorama: `pip install colorama>=0.4.6`
   - Some terminals may not support colors

3. **Permission Errors**:
   - On Unix systems, you may need to make main.py executable: `chmod +x main.py`

### Getting Help

- Check the help message: `python main.py --help`
- Run the demo to see all features: `python main.py --demo`
- Check the test suite for usage examples: `python -m pytest tests/ -v`

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Built with Python's standard library
- Uses [colorama](https://pypi.org/project/colorama/) for cross-platform colored terminal output
- Inspired by the classic "Hello World" programming tradition

## 📈 Version History

- **v1.0.0**: Initial release with full feature set
  - Core greeting functionality
  - Command-line interface
  - Interactive and demo modes
  - Configuration system
  - Unit tests
  - Comprehensive documentation

## 🔮 Future Enhancements

- [ ] Support for more text styles (italic, underline)
- [ ] Configuration file support (JSON/YAML)
- [ ] Internationalization (i18n) support
- [ ] Plugin system for custom greeting formats
- [ ] Web interface
- [ ] ASCII art integration
- [ ] Sound effects (optional)
- [ ] Logging system
- [ ] Performance metrics

---

**Happy Greeting!** 🎉

For more information, questions, or suggestions, please open an issue or contact the development team.