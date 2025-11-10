"""
Snyk Code Analyzer

Integrates Snyk Code (formerly DeepCode) for AI-powered static code analysis.
Automatically analyzes generated code for security vulnerabilities, code quality issues,
and best practice violations.
"""

import os
import json
import logging
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class SnykIssue:
    """Represents a Snyk Code issue"""
    severity: str
    title: str
    message: str
    file_path: str
    line: int
    rule_id: str
    cwe: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SnykCodeAnalyzer:
    """
    Snyk Code Analyzer for automated security and quality analysis
    
    Usage:
        analyzer = SnykCodeAnalyzer(api_token="your-token", org_id="your-org")
        results = await analyzer.analyze_directory("/path/to/code")
        issues = analyzer.parse_results(results)
    """
    
    def __init__(
        self, 
        api_token: Optional[str] = None,
        org_id: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Snyk Code Analyzer
        
        Args:
            api_token: Snyk API token (defaults to SNYK_TOKEN env var)
            org_id: Snyk organization ID (defaults to SNYK_ORG_ID env var)
            logger: Logger instance
        """
        self.api_token = api_token or os.getenv("SNYK_TOKEN")
        self.org_id = org_id or os.getenv("SNYK_ORG_ID")
        self.logger = logger or self._setup_logger()
        self.base_url = "https://api.snyk.io/v1"
        
        if not self.api_token:
            self.logger.warning("⚠️  SNYK_TOKEN not set - Snyk analysis will be skipped")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup default logger"""
        logger = logging.getLogger("SnykCodeAnalyzer")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        return {
            "Authorization": f"token {self.api_token}",
            "Content-Type": "application/json"
        }
    
    async def analyze_directory(
        self, 
        directory_path: str,
        file_patterns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a directory of code with Snyk Code
        
        Args:
            directory_path: Path to directory to analyze
            file_patterns: Optional list of file patterns to include (e.g., ["*.py", "*.js"])
            
        Returns:
            Analysis results from Snyk API
        """
        if not self.api_token:
            self.logger.warning("🚫 Snyk analysis skipped - no API token configured")
            return {"skipped": True, "reason": "No API token"}
        
        self.logger.info(f"🔍 Starting Snyk Code analysis for: {directory_path}")
        
        try:
            # Collect files to analyze
            files_to_analyze = self._collect_files(directory_path, file_patterns)
            
            if not files_to_analyze:
                self.logger.warning(f"⚠️  No files found to analyze in {directory_path}")
                return {"error": "No files found"}
            
            self.logger.info(f"📁 Found {len(files_to_analyze)} files to analyze")
            
            # Create bundle for analysis
            bundle = self._create_file_bundle(files_to_analyze)
            
            # Send to Snyk Code API
            results = await self._send_to_snyk_api(bundle)
            
            self.logger.info("✅ Snyk Code analysis completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Snyk analysis failed: {str(e)}")
            return {"error": str(e)}
    
    def _collect_files(
        self, 
        directory_path: str, 
        file_patterns: Optional[List[str]] = None
    ) -> List[Path]:
        """Collect files matching patterns"""
        directory = Path(directory_path)
        
        if not directory.exists():
            raise ValueError(f"Directory not found: {directory_path}")
        
        # Default patterns if none provided
        if not file_patterns:
            file_patterns = ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.java", "*.go"]
        
        files = []
        for pattern in file_patterns:
            files.extend(directory.rglob(pattern))
        
        # Filter out common exclusions
        excluded_dirs = {".git", ".venv", "node_modules", "__pycache__", "dist", "build"}
        files = [f for f in files if not any(exc in f.parts for exc in excluded_dirs)]
        
        return files
    
    def _create_file_bundle(self, files: List[Path]) -> Dict[str, Any]:
        """Create file bundle for Snyk API"""
        bundle = {
            "files": {}
        }
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    bundle["files"][str(file_path)] = content
            except Exception as e:
                self.logger.warning(f"⚠️  Could not read {file_path}: {e}")
        
        return bundle
    
    async def _send_to_snyk_api(self, bundle: Dict[str, Any]) -> Dict[str, Any]:
        """Send code bundle to Snyk API for analysis"""
        url = f"{self.base_url}/test/code"
        
        if self.org_id:
            url += f"?org={self.org_id}"
        
        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=bundle,
                timeout=300  # 5 minutes timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Snyk API request failed: {e}")
            raise
    
    def parse_results(self, results: Dict[str, Any]) -> List[SnykIssue]:
        """
        Parse Snyk API results into structured issues
        
        Args:
            results: Raw results from Snyk API
            
        Returns:
            List of SnykIssue objects
        """
        if results.get("skipped") or results.get("error"):
            return []
        
        issues = []
        
        # Parse Snyk response format
        for issue_data in results.get("issues", []):
            try:
                issue = SnykIssue(
                    severity=issue_data.get("severity", "unknown"),
                    title=issue_data.get("title", ""),
                    message=issue_data.get("message", ""),
                    file_path=issue_data.get("filePath", ""),
                    line=issue_data.get("lineNumber", 0),
                    rule_id=issue_data.get("ruleId", ""),
                    cwe=issue_data.get("cwe", [])
                )
                issues.append(issue)
            except Exception as e:
                self.logger.warning(f"⚠️  Could not parse issue: {e}")
        
        return issues
    
    def generate_report(
        self, 
        issues: List[SnykIssue], 
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate human-readable report from issues
        
        Args:
            issues: List of SnykIssue objects
            output_path: Optional path to save report
            
        Returns:
            Report as string
        """
        if not issues:
            report = "✅ No security or quality issues found by Snyk Code!\n"
            self.logger.info(report.strip())
            return report
        
        # Group by severity
        by_severity = {"critical": [], "high": [], "medium": [], "low": []}
        for issue in issues:
            severity = issue.severity.lower()
            if severity in by_severity:
                by_severity[severity].append(issue)
        
        # Build report
        lines = ["=" * 80, "🛡️  Snyk Code Analysis Report", "=" * 80, ""]
        
        lines.append(f"📊 Summary: {len(issues)} issues found")
        lines.append(f"   Critical: {len(by_severity['critical'])}")
        lines.append(f"   High:     {len(by_severity['high'])}")
        lines.append(f"   Medium:   {len(by_severity['medium'])}")
        lines.append(f"   Low:      {len(by_severity['low'])}")
        lines.append("")
        
        # Detail each severity level
        for severity in ["critical", "high", "medium", "low"]:
            if by_severity[severity]:
                lines.append(f"\n{'='*80}")
                lines.append(f"{severity.upper()} SEVERITY ISSUES ({len(by_severity[severity])})")
                lines.append(f"{'='*80}\n")
                
                for i, issue in enumerate(by_severity[severity], 1):
                    lines.append(f"{i}. [{issue.rule_id}] {issue.title}")
                    lines.append(f"   File: {issue.file_path}:{issue.line}")
                    lines.append(f"   {issue.message}")
                    if issue.cwe:
                        lines.append(f"   CWE: {', '.join(issue.cwe)}")
                    lines.append("")
        
        report = "\n".join(lines)
        
        # Save if output path provided
        if output_path:
            Path(output_path).write_text(report, encoding='utf-8')
            self.logger.info(f"📝 Report saved to: {output_path}")
        
        return report
    
    async def analyze_and_report(
        self,
        directory_path: str,
        output_path: Optional[str] = None,
        file_patterns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Convenience method: analyze directory and generate report
        
        Args:
            directory_path: Path to directory to analyze
            output_path: Optional path to save report
            file_patterns: Optional file patterns to include
            
        Returns:
            Dict with results, issues, and report
        """
        results = await self.analyze_directory(directory_path, file_patterns)

        # If the analysis was skipped or failed, reflect that in the report instead of
        # incorrectly reporting "No issues found" due to an empty issues list.
        if results.get("skipped"):
            reason = results.get("reason", "Unknown reason")
            report = f"🚫 Snyk analysis skipped: {reason}\n"
            self.logger.warning(report.strip())
            issues: List[SnykIssue] = []
        elif results.get("error"):
            err = results.get("error")
            report = f"❌ Snyk analysis failed: {err}\n"
            self.logger.error(report.strip())
            issues = []
        else:
            issues = self.parse_results(results)
            report = self.generate_report(issues, output_path)
        
        return {
            "results": results,
            "issues": [issue.to_dict() for issue in issues],
            "report": report,
            "summary": {
                "total_issues": len(issues),
                "critical": len([i for i in issues if i.severity.lower() == "critical"]),
                "high": len([i for i in issues if i.severity.lower() == "high"]),
                "medium": len([i for i in issues if i.severity.lower() == "medium"]),
                "low": len([i for i in issues if i.severity.lower() == "low"]),
            }
        }


# CLI interface for testing
if __name__ == "__main__":
    import sys
    import asyncio
    from pathlib import Path
    
    if len(sys.argv) < 2:
        print("Usage: python snyk_code_analyzer.py <directory_path> [output_report_path]")
        sys.exit(1)
    
    directory = str(Path(sys.argv[1]).expanduser().resolve(strict=False))
    output = sys.argv[2] if len(sys.argv) > 2 else None
    
    analyzer = SnykCodeAnalyzer()
    
    async def run():
        result = await analyzer.analyze_and_report(directory, output)
        print(result["report"])
    
    asyncio.run(run())
