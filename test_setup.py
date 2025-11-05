#!/usr/bin/env python3
"""
DeepCode Setup Test Script
Tests the DeepCode installation and configuration without running full agent tasks
"""

import sys
import os
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}")
    print(f"{text}")
    print(f"{'='*80}{Colors.ENDC}\n")

def print_test(name):
    print(f"{Colors.OKCYAN}Testing:{Colors.ENDC} {name}...", end=" ")

def print_success(message="✅ PASS"):
    print(f"{Colors.OKGREEN}{message}{Colors.ENDC}")

def print_fail(message="❌ FAIL"):
    print(f"{Colors.FAIL}{message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")

def test_python_version():
    """Test Python version"""
    print_test("Python version")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"✅ PASS (Python {version.major}.{version.minor}.{version.micro})")
        return True
    else:
        print_fail(f"❌ FAIL (Python {version.major}.{version.minor} < 3.8)")
        return False

def test_required_modules():
    """Test required Python modules"""
    print_header("Testing Required Python Modules")
    
    modules = {
        'aiofiles': 'Async file operations',
        'aiohttp': 'Async HTTP client',
        'anthropic': 'Anthropic API',
        'openai': 'OpenAI API',
        'streamlit': 'Streamlit web UI',
        'mcp': 'MCP Agent framework',
        'nest_asyncio': 'Nested asyncio support',
        'docling': 'Document processing',
    }
    
    all_passed = True
    for module, description in modules.items():
        print_test(f"{description} ({module})")
        try:
            __import__(module)
            print_success()
        except ImportError:
            print_fail()
            all_passed = False
    
    return all_passed

def test_config_files():
    """Test configuration files exist"""
    print_header("Testing Configuration Files")
    
    required_files = {
        'mcp_agent.config.yaml': 'MCP agent configuration',
        'mcp_agent.secrets.yaml': 'API credentials',
        'requirements.txt': 'Python dependencies',
        'cli/main_cli.py': 'CLI entry point',
        'ui/streamlit_app.py': 'Web UI entry point',
    }
    
    all_passed = True
    for file_path, description in required_files.items():
        print_test(f"{description} ({file_path})")
        if Path(file_path).exists():
            print_success()
        else:
            print_fail()
            all_passed = False
    
    return all_passed

def test_environment_variables():
    """Test environment variables"""
    print_header("Testing Environment Variables")
    
    required_vars = {
        'OPENAI_API_KEY': 'OpenAI API key',
        'ANTHROPIC_API_KEY': 'Anthropic API key',
    }
    
    optional_vars = {
        'OPENAI_BASE_URL': 'OpenAI base URL',
        'BRAVE_API_KEY': 'Brave Search API key',
        'BOCHA_API_KEY': 'Bocha Search API key',
    }
    
    # Test required variables
    all_required = True
    for var, description in required_vars.items():
        print_test(f"{description} ({var})")
        value = os.environ.get(var)
        if value:
            # Mask the key for security
            masked = value[:10] + "..." if len(value) > 10 else "***"
            print_success(f"✅ SET ({masked})")
        else:
            print_fail("❌ NOT SET")
            all_required = False
    
    # Test optional variables
    print()
    print_info("Optional environment variables:")
    for var, description in optional_vars.items():
        value = os.environ.get(var)
        if value:
            masked = value[:10] + "..." if len(value) > 10 else "***"
            print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {description} ({var}): {masked}")
        else:
            print(f"  {Colors.WARNING}✗{Colors.ENDC} {description} ({var}): Not set")
    
    return all_required

def test_secrets_file():
    """Test secrets file configuration"""
    print_header("Testing Secrets File Configuration")
    
    print_test("mcp_agent.secrets.yaml format")
    try:
        import yaml
        with open('mcp_agent.secrets.yaml', 'r') as f:
            secrets = yaml.safe_load(f)
        
        # Check structure
        if 'openai' in secrets and 'anthropic' in secrets:
            print_success()
            
            # Check if placeholders are used
            print_test("Environment variable placeholders")
            openai_key = secrets.get('openai', {}).get('api_key', '')
            anthropic_key = secrets.get('anthropic', {}).get('api_key', '')
            
            if '${' in str(openai_key) and '${' in str(anthropic_key):
                print_success("✅ Using env vars")
                return True
            else:
                print_warning("⚠️  Not using env var placeholders")
                print_info("Consider using ${OPENAI_API_KEY} format for security")
                return True
        else:
            print_fail()
            return False
            
    except ImportError:
        print_warning("⚠️  PyYAML not installed, skipping YAML validation")
        return True
    except Exception as e:
        print_fail(f"❌ Error: {e}")
        return False

def test_cli_imports():
    """Test CLI can be imported"""
    print_header("Testing CLI Imports")
    
    print_test("CLI module imports")
    try:
        # Add parent directory to path
        sys.path.insert(0, str(Path(__file__).parent))
        
        from cli.cli_app import CLIApp
        print_success()
        return True
    except ImportError as e:
        print_fail(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print_fail(f"❌ Error: {e}")
        return False

def test_ui_imports():
    """Test UI can be imported"""
    print_header("Testing UI Imports")
    
    print_test("UI module imports")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        
        from ui.layout import main_layout
        print_success()
        return True
    except ImportError as e:
        print_fail(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print_fail(f"❌ Error: {e}")
        return False

def test_tools_directory():
    """Test tools directory"""
    print_header("Testing MCP Tools")
    
    tools_dir = Path('tools')
    if not tools_dir.exists():
        print_fail("Tools directory not found")
        return False
    
    tool_files = [
        'code_implementation_server.py',
        'code_reference_indexer.py',
        'command_executor.py',
        'document_segmentation_server.py',
        'pdf_downloader.py',
        'git_command.py',
    ]
    
    all_passed = True
    for tool_file in tool_files:
        print_test(f"Tool: {tool_file}")
        if (tools_dir / tool_file).exists():
            print_success()
        else:
            print_fail()
            all_passed = False
    
    return all_passed

def print_summary(results):
    """Print test summary"""
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"Total tests: {total}")
    print(f"{Colors.OKGREEN}Passed: {passed}{Colors.ENDC}")
    if failed > 0:
        print(f"{Colors.FAIL}Failed: {failed}{Colors.ENDC}")
    
    print()
    for test_name, result in results.items():
        status = f"{Colors.OKGREEN}✓{Colors.ENDC}" if result else f"{Colors.FAIL}✗{Colors.ENDC}"
        print(f"{status} {test_name}")
    
    print()
    if all(results.values()):
        print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 All tests passed! DeepCode is ready to use.{Colors.ENDC}")
        print()
        print_info("Next steps:")
        print("  1. Launch web UI: streamlit run ui/streamlit_app.py")
        print("  2. Or use CLI: python cli/main_cli.py --help")
        return True
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}❌ Some tests failed. Please fix the issues above.{Colors.ENDC}")
        print()
        print_info("Common fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Set environment variables: export OPENAI_API_KEY=...")
        print("  - Check configuration files exist")
        return False

def main():
    """Main test function"""
    print(f"""
{Colors.HEADER}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🧪 DeepCode Setup Test                                                   ║
║                                                                              ║
║    Testing your DeepCode installation...                                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.ENDC}
""")
    
    # Run all tests
    results = {
        'Python version': test_python_version(),
        'Required modules': test_required_modules(),
        'Configuration files': test_config_files(),
        'Environment variables': test_environment_variables(),
        'Secrets file': test_secrets_file(),
        'CLI imports': test_cli_imports(),
        'UI imports': test_ui_imports(),
        'MCP tools': test_tools_directory(),
    }
    
    # Print summary
    success = print_summary(results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
