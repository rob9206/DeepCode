# DynoAI + Snyk Code Integration Guide

This guide explains how to integrate Snyk Code (formerly DeepCode) security analysis with your DynoAI/DeepCode project.

## 🎯 Overview

The integration provides:
- **Automated security scanning** of generated code
- **Real-time vulnerability detection** in CI/CD pipeline
- **Quality gate enforcement** before deployment
- **Detailed security reports** with actionable recommendations

## 📋 Prerequisites

1. **Snyk Account**: Sign up at [snyk.io](https://snyk.io/)
2. **API Token**: Get your token from [Snyk Account Settings](https://app.snyk.io/account)
3. **Organization ID** (optional): Find in Snyk organization settings

## 🚀 Quick Start

### 1. Set Environment Variables

```bash
# Windows PowerShell
$env:SNYK_TOKEN="your-snyk-api-token-here"
$env:SNYK_ORG_ID="your-org-id-here"  # Optional

# Linux/macOS
export SNYK_TOKEN="your-snyk-api-token-here"
export SNYK_ORG_ID="your-org-id-here"  # Optional
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Test the Integration

```bash
# Analyze a directory
python tools/snyk_code_analyzer.py ./deepcode_lab

# Or use the workflow
python workflows/snyk_integration_workflow.py ./deepcode_lab
```

## 🔧 Configuration

### Option A: Environment Variables (Recommended)

Set `SNYK_TOKEN` and optionally `SNYK_ORG_ID` in your environment.

### Option B: MCP Agent Config

Edit `mcp_agent.config.yaml`:

```yaml
mcp:
  servers:
    snyk-code-analyzer:
      env:
        SNYK_TOKEN: 'your-token-here'
        SNYK_ORG_ID: 'your-org-id'  # Optional
```

### Option C: Secrets File

Edit `mcp_agent.secrets.yaml`:

```yaml
snyk:
  api_token: 'your-snyk-api-token'
  org_id: 'your-org-id'  # Optional
```

## 🤖 GitHub Actions Setup

The integration includes automated CI/CD scanning via GitHub Actions.

### 1. Add Secrets to GitHub

Go to your repository → Settings → Secrets and variables → Actions:

- Add `SNYK_TOKEN`: Your Snyk API token
- Add `SNYK_ORG_ID`: Your Snyk organization ID (optional)

### 2. Enable Workflow

The workflow at `.github/workflows/snyk-security.yml` will automatically:
- Run on every push to `main` or `develop`
- Scan pull requests
- Upload results to GitHub Security tab
- Comment on PRs with findings

### 3. Manual Trigger

You can also trigger manually:
1. Go to Actions tab
2. Select "Snyk Code Security Scan"
3. Click "Run workflow"

## 📊 Usage Examples

### Basic Analysis

```python
from tools.snyk_code_analyzer import SnykCodeAnalyzer
import asyncio

async def analyze():
    analyzer = SnykCodeAnalyzer()
    results = await analyzer.analyze_and_report(
        directory_path="./deepcode_lab",
        output_path="./reports/snyk_report.txt"
    )
    
    print(f"Found {results['summary']['total_issues']} issues")
    print(results['report'])

asyncio.run(analyze())
```

### Integration with Code Generation

```python
from workflows.snyk_integration_workflow import integrate_with_code_generation

async def generate_and_analyze():
    # After code generation...
    generation_results = {...}  # Your generation results
    
    # Run security analysis
    combined_results = await integrate_with_code_generation(
        workspace_dir="./deepcode_lab",
        generation_results=generation_results
    )
    
    if not combined_results['quality_passed']:
        print("⚠️ Critical security issues found!")
    
    return combined_results

asyncio.run(generate_and_analyze())
```

### Quality Gate Validation

```python
from workflows.snyk_integration_workflow import SnykIntegrationWorkflow

async def validate():
    workflow = SnykIntegrationWorkflow()
    
    # Fail if high or critical issues found
    passed = await workflow.validate_code_quality(
        workspace_dir="./deepcode_lab",
        fail_on_severity="high"
    )
    
    if not passed:
        print("❌ Code quality check failed")
        exit(1)
    
    print("✅ Code quality check passed")

asyncio.run(validate())
```

## 🔍 Understanding Results

### Severity Levels

- **Critical** 🔴: Must fix immediately
- **High** 🟠: Fix before deployment
- **Medium** 🟡: Fix in next sprint
- **Low** 🟢: Consider fixing

### Common Issue Types

- **SQL Injection**: Unsanitized database queries
- **XSS**: Cross-site scripting vulnerabilities
- **Path Traversal**: Unsafe file path handling
- **Hardcoded Secrets**: API keys or passwords in code
- **Insecure Dependencies**: Vulnerable libraries

## 🛠️ Advanced Configuration

### Custom File Patterns

```python
analyzer = SnykCodeAnalyzer()
results = await analyzer.analyze_directory(
    directory_path="./my_project",
    file_patterns=["*.py", "*.js", "*.ts", "*.java"]
)
```

### Organization-Specific Settings

```python
analyzer = SnykCodeAnalyzer(
    api_token="your-token",
    org_id="your-org-id"
)
```

### Custom Report Format

```python
issues = analyzer.parse_results(results)
report = analyzer.generate_report(
    issues=issues,
    output_path="./custom_report.txt"
)
```

## 🔄 CI/CD Integration Examples

### Jenkins

```groovy
pipeline {
    agent any
    environment {
        SNYK_TOKEN = credentials('snyk-token')
    }
    stages {
        stage('Security Scan') {
            steps {
                sh 'python tools/snyk_code_analyzer.py ./src'
            }
        }
    }
}
```

### GitLab CI

```yaml
snyk_scan:
  stage: test
  script:
    - pip install -r requirements.txt
    - python tools/snyk_code_analyzer.py ./src
  artifacts:
    paths:
      - snyk-report.txt
```

### Azure Pipelines

```yaml
- task: PythonScript@0
  inputs:
    scriptSource: 'filePath'
    scriptPath: 'tools/snyk_code_analyzer.py'
    arguments: './src'
  env:
    SNYK_TOKEN: $(SNYK_TOKEN)
```

## 📚 Additional Resources

- [Snyk Code Documentation](https://docs.snyk.io/scan-using-snyk/snyk-code)
- [Snyk API Reference](https://snyk.docs.apiary.io/)
- [Snyk CLI Documentation](https://docs.snyk.io/snyk-cli)
- [DynoAI Documentation](https://github.com/HKUDS/DeepCode)

## 🐛 Troubleshooting

### "SNYK_TOKEN not set"

Ensure your token is set in environment variables or config files.

```bash
# Check if set
echo $SNYK_TOKEN  # Linux/macOS
echo $env:SNYK_TOKEN  # Windows PowerShell
```

### "401 Unauthorized"

Your token may be invalid or expired. Generate a new one from Snyk account settings.

### "No files found to analyze"

Check that your directory contains Python files and isn't excluded (`.venv`, `node_modules`, etc.).

### Rate Limiting

Snyk API has rate limits. Space out your requests or contact Snyk support for higher limits.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This integration follows the same license as the DeepCode project.
