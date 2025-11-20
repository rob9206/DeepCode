#!/usr/bin/env python3
"""
Setup script for Hello World Project

This setup.py file allows the Hello World Project to be installed as a Python package
using pip install. It includes all necessary metadata, dependencies, and entry points.
"""

from setuptools import setup, find_packages
import os
import sys

# Read the contents of README file
def read_long_description():
    """Read the long description from README.md file."""
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "A modular greeting system with customizable colors and styles"

# Read requirements from requirements.txt
def read_requirements():
    """Read requirements from requirements.txt file."""
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
            return requirements
    except FileNotFoundError:
        return ["colorama>=0.4.6"]

# Get version from config/settings.py
def get_version():
    """Get version from config/settings.py."""
    try:
        # Add the project directory to Python path temporarily
        project_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_dir)
        
        from config.settings import PROJECT_VERSION
        return PROJECT_VERSION
    except ImportError:
        return "1.0.0"
    finally:
        # Remove the project directory from Python path
        if project_dir in sys.path:
            sys.path.remove(project_dir)

# Project metadata
PACKAGE_NAME = "hello-world-project"
VERSION = get_version()
AUTHOR = "Hello World Team"
AUTHOR_EMAIL = "hello@world.example"
DESCRIPTION = "A modular greeting system with customizable colors and styles"
LONG_DESCRIPTION = read_long_description()
URL = "https://github.com/hello-world-team/hello-world-project"
REQUIREMENTS = read_requirements()

# Development requirements (for testing and development)
DEV_REQUIREMENTS = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=0.991",
]

# Documentation requirements
DOC_REQUIREMENTS = [
    "sphinx>=5.0.0",
    "sphinx-rtd-theme>=1.0.0",
]

# All extra requirements
EXTRA_REQUIREMENTS = {
    "dev": DEV_REQUIREMENTS,
    "docs": DOC_REQUIREMENTS,
    "all": DEV_REQUIREMENTS + DOC_REQUIREMENTS,
}

# Classifiers for PyPI
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Shells",
    "Topic :: Terminals",
    "Topic :: Utilities",
]

# Keywords for PyPI
KEYWORDS = [
    "hello-world",
    "greeting",
    "cli",
    "terminal",
    "colors",
    "console",
    "python",
    "beginner",
    "example",
]

setup(
    # Basic package information
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=URL,
    
    # Package discovery
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    
    # Requirements
    python_requires=">=3.8",
    install_requires=REQUIREMENTS,
    extras_require=EXTRA_REQUIREMENTS,
    
    # Entry points for command-line scripts
    entry_points={
        "console_scripts": [
            "hello-world=main:main",
            "hw=main:simple_hello_world",
            "hello=main:simple_hello_world",
        ],
    },
    
    # Package data
    package_data={
        "": ["*.txt", "*.md", "*.rst", "*.cfg", "*.ini"],
        "config": ["*.py"],
    },
    
    # Metadata for PyPI
    classifiers=CLASSIFIERS,
    keywords=" ".join(KEYWORDS),
    license="MIT",
    platforms=["any"],
    
    # Project URLs
    project_urls={
        "Bug Reports": f"{URL}/issues",
        "Source": URL,
        "Documentation": f"{URL}/docs",
        "Changelog": f"{URL}/blob/main/CHANGELOG.md",
    },
    
    # Additional options
    zip_safe=False,
    test_suite="tests",
    
    # Custom commands can be added here
    cmdclass={},
    
    # Options for different build tools
    options={
        "build_scripts": {
            "executable": "/usr/bin/env python3",
        },
    },
)

# Custom setup functions
def print_setup_info():
    """Print setup information."""
    print(f"Setting up {PACKAGE_NAME} v{VERSION}")
    print(f"Description: {DESCRIPTION}")
    print(f"Author: {AUTHOR}")
    print(f"Python requires: >=3.8")
    print(f"Dependencies: {', '.join(REQUIREMENTS)}")
    print()

def validate_setup():
    """Validate setup configuration."""
    errors = []
    
    # Check if required files exist
    required_files = ["README.md", "requirements.txt"]
    for file in required_files:
        if not os.path.exists(file):
            errors.append(f"Missing required file: {file}")
    
    # Check if source directories exist
    required_dirs = ["src", "config"]
    for dir in required_dirs:
        if not os.path.exists(dir):
            errors.append(f"Missing required directory: {dir}")
    
    # Check Python version
    if sys.version_info < (3, 8):
        errors.append("Python 3.8 or higher is required")
    
    if errors:
        print("Setup validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True

# Run validation and info if this script is executed directly
if __name__ == "__main__":
    print("=" * 60)
    print_setup_info()
    
    if validate_setup():
        print("✅ Setup validation passed!")
        print()
        print("To install this package:")
        print("  pip install .")
        print()
        print("To install in development mode:")
        print("  pip install -e .")
        print()
        print("To install with development dependencies:")
        print("  pip install -e .[dev]")
        print()
        print("To build distribution packages:")
        print("  python setup.py sdist bdist_wheel")
        print()
        print("To upload to PyPI (after building):")
        print("  twine upload dist/*")
    else:
        print("❌ Setup validation failed!")
        sys.exit(1)
    
    print("=" * 60)