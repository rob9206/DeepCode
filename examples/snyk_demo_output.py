"""
Demo: Snyk Integration Output

This script demonstrates what the Snyk integration output looks like
when issues are found (using simulated data for demonstration).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.snyk_code_analyzer import SnykCodeAnalyzer, SnykIssue


def demo_with_issues():
    """Demonstrate output when issues are found"""
    
    # Create analyzer
    analyzer = SnykCodeAnalyzer()
    
    # Simulate some security issues (what would come from Snyk API)
    simulated_issues = [
        SnykIssue(
            severity="critical",
            title="SQL Injection Vulnerability",
            message="User input is used in SQL query without sanitization. This could allow attackers to execute arbitrary SQL commands.",
            file_path="src/database.py",
            line=45,
            rule_id="python/sql-injection",
            cwe=["CWE-89"]
        ),
        SnykIssue(
            severity="high",
            title="Hardcoded Secret Detected",
            message="API key appears to be hardcoded in source code. Store secrets in environment variables instead.",
            file_path="src/config.py",
            line=12,
            rule_id="python/hardcoded-secret",
            cwe=["CWE-798"]
        ),
        SnykIssue(
            severity="high",
            title="Path Traversal Vulnerability",
            message="File path is constructed using user input without validation. This could allow access to unauthorized files.",
            file_path="src/file_handler.py",
            line=78,
            rule_id="python/path-traversal",
            cwe=["CWE-22"]
        ),
        SnykIssue(
            severity="medium",
            title="Insecure Random Number Generation",
            message="Using 'random' module for security-sensitive operations. Use 'secrets' module instead.",
            file_path="src/auth.py",
            line=34,
            rule_id="python/insecure-random",
            cwe=["CWE-338"]
        ),
        SnykIssue(
            severity="medium",
            title="Missing Input Validation",
            message="User input is not validated before processing. Add input validation to prevent injection attacks.",
            file_path="src/api.py",
            line=56,
            rule_id="python/missing-validation",
            cwe=["CWE-20"]
        ),
        SnykIssue(
            severity="low",
            title="Debug Mode Enabled",
            message="Debug mode is enabled in production code. This could expose sensitive information.",
            file_path="src/app.py",
            line=8,
            rule_id="python/debug-enabled",
            cwe=["CWE-489"]
        ),
    ]
    
    # Generate report
    report = analyzer.generate_report(simulated_issues)
    
    print("\n" + "="*80)
    print("DEMO: Snyk Code Analysis with Findings")
    print("="*80)
    print("\nThis demonstrates what the output looks like when Snyk finds issues:")
    print(report)
    
    # Show summary statistics
    summary = {
        "total_issues": len(simulated_issues),
        "critical": len([i for i in simulated_issues if i.severity == "critical"]),
        "high": len([i for i in simulated_issues if i.severity == "high"]),
        "medium": len([i for i in simulated_issues if i.severity == "medium"]),
        "low": len([i for i in simulated_issues if i.severity == "low"]),
    }
    
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print(f"\n📊 Total Issues Found: {summary['total_issues']}")
    print(f"   🔴 Critical: {summary['critical']}")
    print(f"   🟠 High:     {summary['high']}")
    print(f"   🟡 Medium:   {summary['medium']}")
    print(f"   🟢 Low:      {summary['low']}")
    
    # Quality gate check
    print("\n" + "="*80)
    print("QUALITY GATE CHECK")
    print("="*80)
    
    if summary['critical'] > 0:
        print("\n❌ FAILED: Critical security issues must be fixed before deployment!")
    elif summary['high'] > 0:
        print("\n⚠️  WARNING: High severity issues found - review before deployment")
    elif summary['medium'] > 0:
        print("\n⚠️  ADVISORY: Medium severity issues found - consider fixing")
    else:
        print("\n✅ PASSED: No critical or high severity issues found")
    
    print("\n💡 Next Steps:")
    print("   1. Review each issue in detail")
    print("   2. Fix critical and high severity issues")
    print("   3. Run analysis again to verify fixes")
    print("   4. Consider adding automated checks to CI/CD pipeline")
    
    print("\n" + "="*80)
    print("📚 Resources:")
    print("   • Snyk Documentation: https://docs.snyk.io/")
    print("   • CWE Database: https://cwe.mitre.org/")
    print("   • Integration Guide: docs/SNYK_INTEGRATION.md")
    print("="*80 + "\n")


if __name__ == "__main__":
    demo_with_issues()
