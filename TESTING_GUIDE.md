# DeepCode Testing Guide

This guide provides comprehensive testing procedures for validating DeepCode installation and functionality.

## Table of Contents

1. [Pre-Installation Testing](#pre-installation-testing)
2. [Post-Installation Testing](#post-installation-testing)
3. [Web UI Testing](#web-ui-testing)
4. [CLI Testing](#cli-testing)
5. [Integration Testing](#integration-testing)
6. [Troubleshooting Tests](#troubleshooting-tests)

## Pre-Installation Testing

Before installing DeepCode, verify your environment meets the requirements.

### Check Python Version

```bash
python3 --version
# Expected: Python 3.8.0 or higher (3.13+ recommended)
```

### Check Node.js (Optional)

```bash
node --version
npx --version
# Expected: Node.js 16+ (optional but recommended for full features)
```

### Check Git

```bash
git --version
# Expected: git version 2.0+
```

## Post-Installation Testing

After running `./setup_deepcode.sh` or manual installation, validate the setup.

### Run Automated Test Suite

```bash
# Activate virtual environment
source .venv/bin/activate

# Run test suite
python test_setup.py
```

**Expected Output:**
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🧪 DeepCode Setup Test                                                   ║
║                                                                              ║
║    Testing your DeepCode installation...                                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Testing: Python version... ✅ PASS (Python 3.12.3)

================================================================================
Testing Required Python Modules
================================================================================

Testing: Async file operations (aiofiles)... ✅ PASS
Testing: Async HTTP client (aiohttp)... ✅ PASS
Testing: Anthropic API (anthropic)... ✅ PASS
Testing: OpenAI API (openai)... ✅ PASS
Testing: Streamlit web UI (streamlit)... ✅ PASS
Testing: MCP Agent framework (mcp)... ✅ PASS
Testing: Nested asyncio support (nest_asyncio)... ✅ PASS
Testing: Document processing (docling)... ✅ PASS

================================================================================
Testing Configuration Files
================================================================================

Testing: MCP agent configuration (mcp_agent.config.yaml)... ✅ PASS
Testing: API credentials (mcp_agent.secrets.yaml)... ✅ PASS
Testing: Python dependencies (requirements.txt)... ✅ PASS
Testing: CLI entry point (cli/main_cli.py)... ✅ PASS
Testing: Web UI entry point (ui/streamlit_app.py)... ✅ PASS

================================================================================
Testing Environment Variables
================================================================================

Testing: OpenAI API key (OPENAI_API_KEY)... ✅ SET (sk-proj-ab...)
Testing: Anthropic API key (ANTHROPIC_API_KEY)... ✅ SET (sk-ant-api...)

ℹ️  Optional environment variables:
  ✓ OpenAI base URL (OPENAI_BASE_URL): https://ap...
  ✓ Brave Search API key (BRAVE_API_KEY): BSApE23...
  ✗ Bocha Search API key (BOCHA_API_KEY): Not set

...

🎉 All tests passed! DeepCode is ready to use.
```

### Manual Module Testing

```bash
# Test imports manually
python3 << EOF
import streamlit
import anthropic
import openai
import mcp
print("✅ All critical modules imported successfully!")
EOF
```

## Web UI Testing

### Test 1: Launch Web UI

```bash
source .venv/bin/activate
streamlit run ui/streamlit_app.py
```

**Expected Output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.x:8501
```

**Verification Checklist:**
- [ ] Browser opens automatically or can be opened manually
- [ ] Page loads without errors (check browser console)
- [ ] DeepCode logo/header is visible
- [ ] Input text area is functional
- [ ] Sidebar displays properly
- [ ] No Python errors in terminal

### Test 2: Simple Text Input

1. Open http://localhost:8501
2. In the text input, enter:
   ```
   Create a simple Python function to add two numbers
   ```
3. Submit the request

**Expected Behavior:**
- Request is processed
- Loading indicator appears
- Response is displayed
- No unhandled exceptions

### Test 3: Text2Web Generation

1. In the web UI, enter:
   ```
   Text2Web: Create a minimal landing page with:
   - Header with site name
   - Hero section with title and description
   - Call-to-action button
   - Footer with copyright
   Use simple CSS or Tailwind
   ```
2. Submit and wait for generation

**Expected Behavior:**
- HTML/CSS files are generated
- Preview is available (if supported)
- Files can be downloaded
- Code is syntactically correct

### Test 4: Error Handling

1. Submit an empty request
2. Submit a very long request (>10,000 chars)
3. Submit a request with special characters

**Expected Behavior:**
- Appropriate error messages
- No application crashes
- Graceful degradation

## CLI Testing

### Test 1: CLI Help

```bash
source .venv/bin/activate
python cli/main_cli.py --help
```

**Expected Output:**
```
usage: main_cli.py [-h] [--file FILE] [--url URL] [--chat CHAT] ...

DeepCode CLI - Open-Source Code Agent by Data Intelligence Lab @ HKU

optional arguments:
  -h, --help            show this help message and exit
  --file FILE, -f FILE  Process a specific file (PDF, DOCX, TXT, etc.)
  --url URL, -u URL     Process a research paper from URL
  --chat CHAT, -t CHAT  Process coding requirements via chat input
  ...
```

### Test 2: Interactive Mode

```bash
python cli/main_cli.py
```

**Expected Output:**
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🧬 DeepCode - Open-Source Code Agent                                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

🔍 Checking environment...
✅ Python 3.12.3 - OK
✅ Async IO support - OK
✅ Path handling - OK
✅ Type hints - OK
✅ Environment check passed

🎮 Starting interactive mode...
```

**Verification:**
- [ ] Banner displays correctly
- [ ] Environment checks pass
- [ ] Interactive prompt appears
- [ ] Can enter commands
- [ ] Can exit gracefully (Ctrl+C or exit command)

### Test 3: Direct Chat Mode

```bash
python cli/main_cli.py --chat "Generate a Python function to calculate factorial using recursion"
```

**Expected Behavior:**
- Banner and environment check
- "Starting direct processing mode..." message
- Agent initialization
- Code generation
- Success message
- Exit code 0

**Verification Checklist:**
- [ ] Command executes without errors
- [ ] Agent processes the request
- [ ] Output is generated
- [ ] Process exits cleanly

### Test 4: File Processing

Create a test file:
```bash
echo "Test document content for processing" > test_input.txt
```

Run CLI:
```bash
python cli/main_cli.py --file test_input.txt
```

**Expected Behavior:**
- File is read successfully
- Content is processed
- Appropriate action is taken based on content
- No file access errors

### Test 5: Optimized Mode

```bash
python cli/main_cli.py --optimized --chat "Create a simple REST API endpoint"
```

**Expected Output:**
```
⚡ Optimized mode enabled - indexing disabled
```

**Verification:**
- [ ] Faster processing (no indexing overhead)
- [ ] Still produces valid output
- [ ] Appropriate mode indicator

### Test 6: Document Segmentation

```bash
python cli/main_cli.py --disable-segmentation --chat "Test with segmentation disabled"
```

**Expected Output:**
```
📄 Document segmentation disabled - using traditional processing
```

**Verification:**
- [ ] Segmentation mode is respected
- [ ] Processing completes successfully
- [ ] Output quality is acceptable

## Integration Testing

### Test 1: Full Paper2Code Workflow

If you have a research paper PDF:

```bash
python cli/main_cli.py --file research_paper.pdf
```

**Expected Behavior:**
1. PDF is downloaded/read
2. Document is processed (possibly segmented)
3. Code is extracted or reproduced
4. Implementation is generated
5. Output is saved to appropriate directory

**Verification:**
- [ ] PDF processing completes
- [ ] Code is generated
- [ ] Output directory is created
- [ ] Files are syntactically valid

### Test 2: Web UI + CLI Parallel

Terminal 1:
```bash
streamlit run ui/streamlit_app.py
```

Terminal 2:
```bash
python cli/main_cli.py --chat "Test parallel execution"
```

**Expected Behavior:**
- Both can run simultaneously
- No port conflicts
- No resource conflicts
- Both function correctly

### Test 3: Search Integration

If BRAVE_API_KEY or BOCHA_API_KEY is set:

```bash
python cli/main_cli.py --chat "Search for the latest Python best practices for async programming and generate a sample"
```

**Expected Behavior:**
- Search API is called
- Results are retrieved
- Information is incorporated into response
- No API errors

## Troubleshooting Tests

### Test: Verify API Keys

```bash
# Test OpenAI API
python3 << EOF
import os
from openai import OpenAI

api_key = os.environ.get('OPENAI_API_KEY')
base_url = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')

if not api_key:
    print("❌ OPENAI_API_KEY not set")
else:
    print(f"✅ OPENAI_API_KEY is set (starts with: {api_key[:10]}...)")
    print(f"✅ OPENAI_BASE_URL: {base_url}")
EOF
```

```bash
# Test Anthropic API
python3 << EOF
import os
from anthropic import Anthropic

api_key = os.environ.get('ANTHROPIC_API_KEY')

if not api_key:
    print("❌ ANTHROPIC_API_KEY not set")
else:
    print(f"✅ ANTHROPIC_API_KEY is set (starts with: {api_key[:10]}...)")
EOF
```

### Test: Network Connectivity

```bash
# Test PyPI access
ping -c 3 pypi.org

# Test API endpoints
curl -I https://api.openai.com/v1/models
curl -I https://api.anthropic.com/v1/messages
```

### Test: Port Availability

```bash
# Check if port 8501 is available
lsof -ti:8501 || echo "Port 8501 is available"

# Check if port is in use
netstat -tuln | grep 8501
```

### Test: File Permissions

```bash
# Check executable permissions
ls -l setup_deepcode.sh test_setup.py cli/main_cli.py

# Check write permissions for logs
test -w . && echo "✅ Can write to current directory" || echo "❌ Cannot write to current directory"
```

## Performance Testing

### Test: Startup Time

```bash
time python cli/main_cli.py --help
# Expected: < 2 seconds
```

### Test: Simple Request Time

```bash
time python cli/main_cli.py --chat "Print hello world"
# Expected: Varies based on API response time
```

### Test: Memory Usage

```bash
# Monitor memory during execution
/usr/bin/time -v python cli/main_cli.py --chat "Simple test"
# Check Maximum resident set size
```

## Success Criteria

A successful DeepCode installation should meet these criteria:

### Required ✅
- [ ] All Python dependencies install without errors
- [ ] Environment variables are set correctly
- [ ] Configuration files exist and are valid
- [ ] Web UI launches and is accessible
- [ ] CLI executes without errors
- [ ] Simple requests are processed successfully
- [ ] No unhandled exceptions during normal operation

### Recommended ✅
- [ ] Node.js dependencies installed (for full MCP server support)
- [ ] Search API keys configured
- [ ] Document segmentation works correctly
- [ ] Both optimized and comprehensive modes work
- [ ] Parallel execution (Web UI + CLI) works

### Optional ✅
- [ ] Custom model configurations work
- [ ] All MCP servers initialize successfully
- [ ] Performance meets expectations
- [ ] Output quality is satisfactory

## Reporting Issues

If tests fail, gather this information:

1. **Environment:**
   ```bash
   python --version
   node --version
   pip list | head -20
   ```

2. **Configuration:**
   ```bash
   # Redact sensitive data!
   cat mcp_agent.config.yaml
   ```

3. **Error Messages:**
   - Full terminal output
   - Browser console errors (for Web UI)
   - Log files in `logs/` directory

4. **System Information:**
   ```bash
   uname -a
   cat /etc/os-release
   ```

5. **Test Results:**
   ```bash
   python test_setup.py > test_results.txt 2>&1
   ```

Submit issues to: https://github.com/rob9206/DeepCode/issues

## Next Steps

After successful testing:

1. ✅ Read the full documentation
2. ✅ Explore example projects
3. ✅ Try more complex tasks
4. ✅ Customize configuration for your needs
5. ✅ Join the community (Discord/WeChat)
6. ✅ Contribute improvements

---

**Happy Testing! 🧪**
