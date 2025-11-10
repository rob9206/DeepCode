#!/bin/bash
# DeepCode Setup Script
# This script automates the setup of DeepCode for local development and testing

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Print banner
print_banner() {
    cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🧬 DeepCode Setup Script                                                 ║
║                                                                              ║
║    Setting up your local DeepCode environment...                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python() {
    log_info "Checking Python version..."
    
    if ! command_exists python3; then
        log_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    log_success "Python $PYTHON_VERSION found"
    
    # Check if version is >= 3.8
    if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
        log_error "Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
}

# Check Node.js (optional but recommended)
check_nodejs() {
    log_info "Checking Node.js installation (optional)..."
    
    if command_exists node; then
        NODE_VERSION=$(node --version)
        log_success "Node.js $NODE_VERSION found"
        
        if ! command_exists npx; then
            log_warning "npx not found. Installing..."
            npm install -g npx || log_warning "Could not install npx globally. Some MCP servers may not work."
        else
            log_success "npx found"
        fi
    else
        log_warning "Node.js not found. Some MCP servers (brave, filesystem) will not work."
        log_warning "Install Node.js from https://nodejs.org/ to enable all features."
    fi
}

# Create virtual environment
create_venv() {
    log_info "Creating Python virtual environment..."
    
    if [ -d ".venv" ]; then
        log_warning "Virtual environment already exists. Skipping creation."
    else
        python3 -m venv .venv
        log_success "Virtual environment created"
    fi
}

# Install Python dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip
    
    # Install requirements
    log_info "Installing packages from requirements.txt..."
    pip install -r requirements.txt
    
    log_success "Python dependencies installed"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    source .venv/bin/activate
    
    python3 << EOF
import sys
missing_modules = []
modules_to_check = {
    'streamlit': 'Streamlit web UI',
    'anthropic': 'Anthropic API',
    'openai': 'OpenAI API',
    'mcp': 'MCP Agent',
    'aiohttp': 'Async HTTP',
}

for module, description in modules_to_check.items():
    try:
        __import__(module)
        print(f"✅ {description}")
    except ImportError:
        print(f"❌ {description} - MISSING")
        missing_modules.append(module)

if missing_modules:
    print(f"\n❌ Some modules are missing: {', '.join(missing_modules)}")
    sys.exit(1)
else:
    print("\n✅ All required modules are installed!")
    sys.exit(0)
EOF
    
    if [ $? -eq 0 ]; then
        log_success "Installation verification passed"
    else
        log_error "Installation verification failed"
        exit 1
    fi
}

# Check environment variables
check_env_vars() {
    log_info "Checking environment variables..."
    
    local missing_vars=()
    
    if [ -z "$OPENAI_API_KEY" ]; then
        missing_vars+=("OPENAI_API_KEY")
    fi
    
    if [ -z "$OPENAI_BASE_URL" ]; then
        log_warning "OPENAI_BASE_URL not set. Will use default OpenAI endpoint."
    fi
    
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        missing_vars+=("ANTHROPIC_API_KEY")
    fi
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_warning "Missing environment variables: ${missing_vars[*]}"
        log_warning "Please set these variables before running DeepCode:"
        for var in "${missing_vars[@]}"; do
            echo "  export $var=\"your-key-here\""
        done
        echo ""
    else
        log_success "All required environment variables are set"
    fi
    
    # Optional variables
    if [ -z "$BRAVE_API_KEY" ] && [ -z "$BOCHA_API_KEY" ]; then
        log_warning "No search API key set (BRAVE_API_KEY or BOCHA_API_KEY)"
        log_warning "Web search features will not be available"
    fi
}

# Print usage instructions
print_usage() {
    cat << EOF

╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🎉 Setup Complete!                                                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

To start using DeepCode:

1. Activate the virtual environment:
   ${GREEN}source .venv/bin/activate${NC}

2. Set your API keys (if not already set):
   ${YELLOW}export OPENAI_API_KEY="your-key-here"
   export OPENAI_BASE_URL="https://api.openai.com/v1"
   export ANTHROPIC_API_KEY="your-key-here"${NC}

3. Launch the Web UI:
   ${BLUE}streamlit run ui/streamlit_app.py${NC}
   
   Then open: ${GREEN}http://localhost:8501${NC}

4. Or use the CLI:
   ${BLUE}python cli/main_cli.py --help${NC}
   ${BLUE}python cli/main_cli.py --chat "Your request here"${NC}

For more information, see:
   - SETUP_VERIFICATION_REPORT.md
   - README.md

EOF
}

# Main execution
main() {
    print_banner
    
    # Check prerequisites
    check_python
    check_nodejs
    
    # Setup environment
    create_venv
    install_dependencies
    verify_installation
    
    # Check configuration
    check_env_vars
    
    # Print usage
    print_usage
}

# Run main function
main "$@"
