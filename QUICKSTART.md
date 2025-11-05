# DeepCode Quick Start Guide

Get DeepCode up and running in minutes!

## Prerequisites

- **Python 3.8+** (3.13 recommended)
- **Git**
- **pip** or **uv**
- **Node.js** (optional, for some MCP servers)

## API Keys Required

Before starting, obtain these API keys:

1. **OpenAI-compatible API key** (required)
   - Get from OpenAI, or use compatible providers (e.g., OpenRouter, Together AI)
   
2. **Anthropic API key** (required)
   - Get from https://console.anthropic.com/

3. **Search API key** (optional)
   - Brave Search: https://brave.com/search/api/
   - OR Bocha Search: Contact provider

## Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/rob9206/DeepCode.git
cd DeepCode

# Run setup script
./setup_deepcode.sh

# Follow the on-screen instructions
```

## Manual Setup

### 1. Clone and Enter Directory

```bash
git clone https://github.com/rob9206/DeepCode.git
cd DeepCode
```

### 2. Create Virtual Environment

Choose one method:

**Using pip:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Using uv (faster):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python=3.13
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 3. Set Environment Variables

Create a `.env` file or export variables:

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="https://api.openai.com/v1"
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional: For web search
export BRAVE_API_KEY="..."
# OR
export BOCHA_API_KEY="..."
```

### 4. Configure Secrets (Already Done)

The `mcp_agent.secrets.yaml` file is already configured to read from environment variables. No manual editing needed!

## Launch Methods

### Method 1: Web UI (Recommended for Beginners)

```bash
streamlit run ui/streamlit_app.py
```

Then open your browser to: **http://localhost:8501**

### Method 2: CLI (For Advanced Users)

**Interactive mode:**
```bash
python cli/main_cli.py
```

**Direct task execution:**
```bash
python cli/main_cli.py --chat "Create a Flask /health endpoint"
```

**Process a paper:**
```bash
python cli/main_cli.py --file paper.pdf
```

**Process from URL:**
```bash
python cli/main_cli.py --url https://arxiv.org/pdf/2301.xxxxx.pdf
```

## Quick Test Examples

### Test 1: Simple Code Generation (CLI)

```bash
python cli/main_cli.py --chat "Generate a Python function to calculate the Fibonacci sequence up to n terms"
```

### Test 2: Web Development (Web UI)

1. Open http://localhost:8501
2. Enter this prompt:
   ```
   Text2Web: Create a minimal responsive homepage with:
   - A header with navigation
   - A hero section with a call-to-action
   - A features section
   - A footer
   Use Tailwind CSS or simple CSS
   ```
3. Wait for generation and review output

### Test 3: Backend Development (CLI)

```bash
python cli/main_cli.py --chat "Create a REST API with FastAPI that has endpoints for CRUD operations on a 'users' resource"
```

## CLI Options

```bash
python cli/main_cli.py [OPTIONS]

Options:
  --file, -f PATH              Process a file (PDF, DOCX, TXT, etc.)
  --url, -u URL                Process paper from URL
  --chat, -t TEXT              Direct chat input
  --optimized, -o              Skip indexing for faster processing
  --disable-segmentation       Disable document segmentation
  --segmentation-threshold N   Set segmentation threshold (default: 50000)
  --verbose, -v                Enable verbose output
  --help                       Show help message
```

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8501
lsof -ti:8501 | xargs kill -9

# Or use different port
streamlit run ui/streamlit_app.py --server.port 8502
```

### Import Errors

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### API Key Errors

```bash
# Verify environment variables are set
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Check secrets file
cat mcp_agent.secrets.yaml
```

### Network Issues During Installation

```bash
# Increase timeout
pip install --timeout=300 -r requirements.txt

# Use alternative mirror (if in China)
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

## Configuration

### Change Default Model

Edit `mcp_agent.config.yaml`:

```yaml
openai:
  default_model: gpt-4  # or any OpenAI-compatible model
```

### Disable Search Features

Edit `mcp_agent.config.yaml`:

```yaml
default_search_server: null  # Disable search
```

### Adjust Document Segmentation

```yaml
document_segmentation:
  enabled: true
  size_threshold_chars: 50000  # Adjust threshold
```

Or use CLI flag:
```bash
python cli/main_cli.py --segmentation-threshold 30000
```

## Project Structure

```
DeepCode/
├── cli/                    # Command-line interface
│   ├── main_cli.py        # CLI entry point
│   └── ...
├── ui/                     # Web interface
│   ├── streamlit_app.py   # Web UI entry point
│   └── ...
├── tools/                  # MCP server tools
├── workflows/              # Agent workflows
├── mcp_agent.config.yaml   # Main configuration
├── mcp_agent.secrets.yaml  # API credentials
├── requirements.txt        # Python dependencies
└── setup_deepcode.sh       # Automated setup script
```

## Next Steps

1. **Explore Examples:** Check the `examples/` directory for sample projects
2. **Read Documentation:** See `SETUP_VERIFICATION_REPORT.md` for detailed info
3. **Join Community:** Visit the Discord or WeChat group (see README.md)
4. **Contribute:** Submit issues or PRs on GitHub

## Getting Help

- **Documentation:** See README.md and SETUP_VERIFICATION_REPORT.md
- **Issues:** https://github.com/rob9206/DeepCode/issues
- **Upstream Repo:** https://github.com/HKUDS/DeepCode
- **Discord:** https://discord.gg/yF2MmDJyGJ

## Security Notes

⚠️ **Important:**
- Never commit API keys to version control
- Keep `.env` files private
- Use minimum required API permissions
- Review generated code before execution in production

---

**Happy Coding with DeepCode! 🚀**
