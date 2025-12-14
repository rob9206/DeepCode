# 🛡️ Snyk Code Security Integration

Add this section to the main README.md to document the new Snyk integration.

---

## Security Analysis with Snyk Code

DeepCode now integrates with **Snyk Code** (formerly DeepCode) for automated security and quality analysis of generated code.

### Features

- 🔍 **Automated vulnerability scanning** for generated code
- 🚨 **Real-time security alerts** on potential issues
- ✅ **Quality gate validation** before deployment
- 📊 **Detailed security reports** with recommendations
- 🤖 **CI/CD integration** via GitHub Actions

### Quick Setup

1. **Get Snyk API Token**
   - Sign up at [snyk.io](https://snyk.io/)
   - Get token from [Account Settings](https://app.snyk.io/account)

2. **Configure Token**
   ```bash
   # Set environment variable
   export SNYK_TOKEN="your-snyk-api-token"
   
   # Or run setup script
   python setup_snyk_integration.py
   ```

3. **Analyze Your Code**
   ```bash
   # Analyze a directory
   python tools/snyk_code_analyzer.py ./deepcode_lab
   
   # Run examples
   python examples/snyk_integration_example.py
   ```

### Usage in Python

```python
from tools.snyk_code_analyzer import SnykCodeAnalyzer
import asyncio

async def analyze():
    analyzer = SnykCodeAnalyzer()
    results = await analyzer.analyze_and_report(
        directory_path="./my_project",
        output_path="./security_report.txt"
    )
    print(f"Found {results['summary']['total_issues']} issues")

asyncio.run(analyze())
```

### GitHub Actions

Security scanning runs automatically on every push and PR. Results appear in:
- GitHub Security tab (Code Scanning Alerts)
- PR comments
- Workflow artifacts

To enable:
1. Add `SNYK_TOKEN` to GitHub Secrets (Settings → Secrets → Actions)
2. Workflow is already configured in `.github/workflows/snyk-security.yml`

### Documentation

- **Full Guide**: [`docs/SNYK_INTEGRATION.md`](docs/SNYK_INTEGRATION.md)
- **Summary**: [`SNYK_INTEGRATION_SUMMARY.md`](SNYK_INTEGRATION_SUMMARY.md)
- **Examples**: [`examples/snyk_integration_example.py`](examples/snyk_integration_example.py)

### Quality Gates

Enforce code quality standards:

```python
from workflows.snyk_integration_workflow import SnykIntegrationWorkflow

workflow = SnykIntegrationWorkflow()
passed = await workflow.validate_code_quality(
    workspace_dir="./src",
    fail_on_severity="high"  # Fail on high or critical issues
)
```

### Files Added

- `tools/snyk_code_analyzer.py` - Core integration module
- `workflows/snyk_integration_workflow.py` - Workflow integration
- `.github/workflows/snyk-security.yml` - CI/CD automation
- `docs/SNYK_INTEGRATION.md` - Complete documentation
- `examples/snyk_integration_example.py` - Usage examples
- `setup_snyk_integration.py` - Setup script

---

## Original README content continues below...
