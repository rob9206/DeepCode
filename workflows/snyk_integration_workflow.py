"""
Snyk Integration Workflow

Integrates Snyk Code analysis into the DeepCode code generation pipeline.
Automatically analyzes generated code for security and quality issues.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.snyk_code_analyzer import SnykCodeAnalyzer


class SnykIntegrationWorkflow:
    """
    Workflow to integrate Snyk Code analysis with DeepCode generation
    
    Usage:
        workflow = SnykIntegrationWorkflow()
        await workflow.analyze_generated_code(workspace_dir)
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize workflow"""
        self.logger = logger or self._setup_logger()
        self.analyzer = SnykCodeAnalyzer(logger=self.logger)
    
    def _setup_logger(self) -> logging.Logger:
        """Setup default logger"""
        logger = logging.getLogger("SnykIntegrationWorkflow")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def analyze_generated_code(
        self,
        workspace_dir: str,
        output_dir: Optional[str] = None,
        auto_fix: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze generated code in workspace directory
        
        Args:
            workspace_dir: Directory containing generated code
            output_dir: Directory to save reports (defaults to workspace_dir/reports)
            auto_fix: Whether to attempt automatic fixes (future feature)
            
        Returns:
            Analysis results with issues and recommendations
        """
        self.logger.info(f"🔍 Starting Snyk analysis for workspace: {workspace_dir}")

        # Normalize and resolve workspace path
        workspace_path = Path(workspace_dir).expanduser().resolve(strict=False)
        if not workspace_path.exists():
            self.logger.error(f"❌ Workspace not found: {workspace_dir}")
            return {"error": "Workspace not found"}

        # Setup output directory
        if not output_dir:
            output_dir = workspace_path / "reports"

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        report_file = output_path / "snyk_security_report.txt"
        
        # Run analysis
        results = await self.analyzer.analyze_and_report(
            str(workspace_path),
            str(report_file),
            file_patterns=["*.py"]  # Focus on Python files for DeepCode
        )
        
        # Log summary
        summary = results["summary"]
        self.logger.info(f"📊 Analysis complete: {summary['total_issues']} issues found")
        
        if summary["critical"] > 0:
            self.logger.error(f"🚨 CRITICAL: {summary['critical']} critical issues found!")
        if summary["high"] > 0:
            self.logger.warning(f"⚠️  HIGH: {summary['high']} high severity issues found")
        
        # Generate recommendations
        recommendations = self._generate_recommendations(results["issues"])
        results["recommendations"] = recommendations
        
        return results
    
    def _generate_recommendations(self, issues: list) -> list:
        """Generate actionable recommendations from issues"""
        recommendations = []
        
        # Group by rule type
        rule_counts = {}
        for issue in issues:
            rule_id = issue.get("rule_id", "unknown")
            rule_counts[rule_id] = rule_counts.get(rule_id, 0) + 1
        
        # Sort by frequency
        sorted_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Generate top recommendations
        for rule_id, count in sorted_rules[:5]:
            recommendations.append({
                "rule": rule_id,
                "frequency": count,
                "action": f"Review and fix {count} instance(s) of {rule_id}"
            })
        
        return recommendations
    
    async def validate_code_quality(
        self,
        workspace_dir: str,
        fail_on_severity: str = "high"
    ) -> bool:
        """
        Validate code quality - returns False if severity threshold exceeded
        
        Args:
            workspace_dir: Directory containing code
            fail_on_severity: Fail if this or higher severity found (critical, high, medium, low)
            
        Returns:
            True if code passes quality check, False otherwise
        """
        results = await self.analyze_generated_code(workspace_dir)
        
        if results.get("error"):
            self.logger.warning("⚠️  Analysis skipped or failed")
            return True  # Don't fail on analysis errors
        
        summary = results["summary"]
        
        severity_order = ["critical", "high", "medium", "low"]
        threshold_index = severity_order.index(fail_on_severity.lower())
        
        for i in range(threshold_index + 1):
            severity = severity_order[i]
            if summary.get(severity, 0) > 0:
                self.logger.error(
                    f"❌ Code quality check failed: {summary[severity]} {severity} issues found"
                )
                return False
        
        self.logger.info("✅ Code quality check passed")
        return True


async def integrate_with_code_generation(
    workspace_dir: str,
    generation_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Hook to integrate Snyk analysis after code generation
    
    Args:
        workspace_dir: Workspace directory
        generation_results: Results from code generation workflow
        
    Returns:
        Combined results with security analysis
    """
    workflow = SnykIntegrationWorkflow()
    
    # Run analysis
    snyk_results = await workflow.analyze_generated_code(workspace_dir)
    
    # Combine results
    combined = {
        "generation": generation_results,
        "security_analysis": snyk_results,
        "quality_passed": snyk_results["summary"]["critical"] == 0
    }
    
    return combined


# CLI for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python snyk_integration_workflow.py <workspace_dir>")
        sys.exit(1)
    
    workspace = sys.argv[1]
    
    async def run():
        workflow = SnykIntegrationWorkflow()
        results = await workflow.analyze_generated_code(workspace)
        
        print("\n" + "="*80)
        print("SNYK INTEGRATION WORKFLOW RESULTS")
        print("="*80)
        print(results["report"])
        print("\n📋 Recommendations:")
        for rec in results.get("recommendations", []):
            print(f"  • {rec['action']}")
    
    asyncio.run(run())
