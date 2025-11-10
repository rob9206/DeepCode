"""
Snyk Integration Setup Script

Quick setup for Snyk Code security analysis integration.
"""

import os
import sys
from pathlib import Path


def check_snyk_token():
    """Check if Snyk token is configured"""
    token = os.getenv("SNYK_TOKEN")
    if token:
        print("✅ SNYK_TOKEN is set")
        return True
    else:
        print("⚠️  SNYK_TOKEN is not set")
        return False


def setup_env_file():
    """Create or update .env file with Snyk configuration"""
    env_file = Path(".env")
    
    if env_file.exists():
        print(f"📄 Found existing {env_file}")
        content = env_file.read_text()
    else:
        print(f"📝 Creating new {env_file}")
        content = ""
    
    if "SNYK_TOKEN" not in content:
        print("\n💡 You'll need a Snyk API token from: https://app.snyk.io/account")
        token = input("Enter your Snyk API token (or press Enter to skip): ").strip()
        
        if token:
            content += f"\n# Snyk Code Integration\nSNYK_TOKEN={token}\n"
            
            org_id = input("Enter your Snyk Organization ID (optional, press Enter to skip): ").strip()
            if org_id:
                content += f"SNYK_ORG_ID={org_id}\n"
            
            env_file.write_text(content)
            print(f"✅ Saved configuration to {env_file}")
            print("\n⚠️  Important: Add .env to your .gitignore to keep tokens secure!")
        else:
            print("⏭️  Skipped token setup - you can set SNYK_TOKEN environment variable manually")
    else:
        print("✅ SNYK_TOKEN already configured in .env")


def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n🔍 Checking dependencies...")
    
    required = ["requests", "httpx", "aiohttp"]
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
            print(f"   ✅ {pkg}")
        except ImportError:
            print(f"   ❌ {pkg} (missing)")
            missing.append(pkg)
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


def test_integration():
    """Test the integration"""
    print("\n🧪 Testing Snyk integration...")
    
    try:
        from tools.snyk_code_analyzer import SnykCodeAnalyzer
        
        analyzer = SnykCodeAnalyzer()
        print("✅ SnykCodeAnalyzer loaded successfully")
        
        if analyzer.api_token:
            print("✅ API token configured")
        else:
            print("⚠️  API token not configured - analysis will be skipped")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading integration: {e}")
        return False


def show_next_steps():
    """Show next steps for user"""
    print("\n" + "="*80)
    print("🎉 Setup Complete!")
    print("="*80)
    print("\n📚 Next Steps:\n")
    print("1. Set your Snyk API token:")
    print("   • Get token from: https://app.snyk.io/account")
    print("   • Set environment variable: export SNYK_TOKEN='your-token'")
    print("   • Or add to .env file\n")
    print("2. Run an example:")
    print("   python examples/snyk_integration_example.py\n")
    print("3. Analyze your code:")
    print("   python tools/snyk_code_analyzer.py ./your_directory\n")
    print("4. Set up GitHub Actions:")
    print("   • Add SNYK_TOKEN to GitHub Secrets")
    print("   • Workflow is already configured in .github/workflows/snyk-security.yml\n")
    print("5. Read the documentation:")
    print("   docs/SNYK_INTEGRATION.md\n")
    print("="*80)


def main():
    """Main setup function"""
    print("🛡️  Snyk Code Integration Setup")
    print("="*80 + "\n")
    
    # Check if we're in the right directory
    if not Path("tools").exists() or not Path("requirements.txt").exists():
        print("❌ Error: Please run this script from the DeepCode root directory")
        sys.exit(1)
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    if not deps_ok:
        print("\n❌ Please install dependencies first: pip install -r requirements.txt")
        return
    
    # Check for token
    has_token = check_snyk_token()
    
    if not has_token:
        response = input("\nWould you like to set up a .env file with your Snyk token? (y/n): ").strip().lower()
        if response == 'y':
            setup_env_file()
    
    # Test integration
    test_ok = test_integration()
    
    if test_ok:
        show_next_steps()
    else:
        print("\n❌ Setup encountered errors. Please check the output above.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
