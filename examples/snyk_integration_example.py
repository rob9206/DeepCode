"""
Example: Using Snyk Code Analysis with DeepCode

This example demonstrates how to integrate Snyk security analysis
into your DeepCode workflow.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.snyk_code_analyzer import SnykCodeAnalyzer
from workflows.snyk_integration_workflow import SnykIntegrationWorkflow


async def example_basic_analysis():
    """Example 1: Basic code analysis"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Snyk Code Analysis")
    print("="*80 + "\n")
    
    analyzer = SnykCodeAnalyzer()
    
    # Analyze the tools directory
    results = await analyzer.analyze_and_report(
        directory_path="./tools",
        output_path="./snyk_example_report.txt",
        file_patterns=["*.py"]
    )
    
    print(f"📊 Analysis Summary:")
    print(f"   Total Issues: {results['summary']['total_issues']}")
    print(f"   Critical: {results['summary']['critical']}")
    print(f"   High: {results['summary']['high']}")
    print(f"   Medium: {results['summary']['medium']}")
    print(f"   Low: {results['summary']['low']}")
    
    if results['summary']['total_issues'] == 0:
        print("\n✅ No issues found - code looks good!")
    else:
        print(f"\n📝 Full report saved to: snyk_example_report.txt")


async def example_workflow_integration():
    """Example 2: Integration with workflow"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Workflow Integration")
    print("="*80 + "\n")
    
    workflow = SnykIntegrationWorkflow()
    
    # Analyze workspace with recommendations
    results = await workflow.analyze_generated_code(
        workspace_dir="./workflows",
        output_dir="./reports"
    )
    
    print("📋 Top Recommendations:")
    for i, rec in enumerate(results.get("recommendations", [])[:3], 1):
        print(f"   {i}. {rec['action']}")


async def example_quality_gate():
    """Example 3: Quality gate validation"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Quality Gate Validation")
    print("="*80 + "\n")
    
    workflow = SnykIntegrationWorkflow()
    
    # Check if code passes quality standards
    passed = await workflow.validate_code_quality(
        workspace_dir="./utils",
        fail_on_severity="high"
    )
    
    if passed:
        print("✅ Code passed quality gate - safe to deploy")
    else:
        print("❌ Code failed quality gate - fix issues before deploying")
    
    return passed


async def example_custom_analysis():
    """Example 4: Custom analysis with specific patterns"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Custom File Pattern Analysis")
    print("="*80 + "\n")
    
    analyzer = SnykCodeAnalyzer()
    
    # Analyze only specific file types
    results = await analyzer.analyze_directory(
        directory_path="./",
        file_patterns=["*.py", "*.yaml", "*.yml"]
    )
    
    # Parse and display issues
    issues = analyzer.parse_results(results)
    
    if issues:
        print(f"Found {len(issues)} issues across configuration and Python files:")
        
        # Group by file
        by_file = {}
        for issue in issues:
            file = issue.file_path
            if file not in by_file:
                by_file[file] = []
            by_file[file].append(issue)
        
        for file, file_issues in list(by_file.items())[:5]:  # Show first 5 files
            print(f"\n📄 {file}: {len(file_issues)} issue(s)")
            for issue in file_issues[:2]:  # Show first 2 issues per file
                print(f"   • [{issue.severity}] {issue.title}")
    else:
        print("✅ No issues found in configuration files")


async def run_all_examples():
    """Run all examples"""
    print("\n" + "🛡️ "*20)
    print("Snyk Code Integration Examples")
    print("🛡️ "*20 + "\n")
    
    print("💡 Note: These examples require SNYK_TOKEN environment variable")
    print("   If not set, analysis will be skipped gracefully.\n")
    
    try:
        # Run examples
        await example_basic_analysis()
        await example_workflow_integration()
        await example_quality_gate()
        await example_custom_analysis()
        
        print("\n" + "="*80)
        print("✅ All examples completed!")
        print("="*80 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check if running in async-friendly environment
    try:
        asyncio.run(run_all_examples())
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            # We're in a notebook or async environment
            import nest_asyncio
            nest_asyncio.apply()
            asyncio.get_event_loop().run_until_complete(run_all_examples())
        else:
            raise
