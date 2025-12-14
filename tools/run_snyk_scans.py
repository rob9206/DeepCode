#!/usr/bin/env python3
"""
Run Snyk OSS (dependency) and Code (SAST) scans via Snyk CLI and save reports.

- Finds the Snyk CLI on Windows (prefers %AppData%\\npm\\snyk.cmd) or PATH
- Optionally authenticates using SNYK_TOKEN if provided
- Saves human-readable and machine-readable outputs under reports/

Usage (Windows PowerShell):
    C:\\DynoAI\\DeepCode\\.venv\\Scripts\\python.exe tools\\run_snyk_scans.py

Options:
  --project-root PATH       Project root to scan (default: repo root of this script)
  --reports-dir PATH        Directory to write reports (default: reports)
  --skip-oss                Skip dependency scan
  --skip-code               Skip code scan
  --strict                  Exit non-zero if open issues are found
  --dry-run                 Show what would run without executing scans

Outputs:
  reports/snyk_oss.txt
  reports/snyk_oss.json
  reports/snyk_code.txt
  reports/snyk_code.sarif
"""
from __future__ import annotations

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
import argparse
from typing import Optional, List


def is_windows() -> bool:
    return os.name == "nt"


def find_snyk_cli() -> Optional[Path]:
    # 1) Respect explicit override
    override = os.environ.get("SNYK_BIN")
    if override:
        p = Path(override)
        if p.exists():
            return p

    # 2) Windows common locations
    if is_windows():
        appdata_bin = Path(os.environ.get("AppData", "")) / "npm" / ("snyk.cmd")
        if appdata_bin.exists():
            return appdata_bin
        # Fallback to PATH
        exe = shutil.which("snyk.cmd") or shutil.which("snyk")
        if exe:
            return Path(exe)
    else:
        exe = shutil.which("snyk")
        if exe:
            return Path(exe)

    return None


def run(
    args: List[str],
    cwd: Optional[Path] = None,
    env: Optional[dict] = None,
    capture: bool = True,
) -> subprocess.CompletedProcess:
    # Merge Node.js path into environment so npm-installed binaries can find 'node'
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    # Ensure Node.js is on PATH for this subprocess
    node_dir = str(Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "nodejs")
    if node_dir not in merged_env.get("PATH", ""):
        merged_env["PATH"] = f"{node_dir};{merged_env.get('PATH', '')}"
    
    proc = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        env=merged_env,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
        shell=False,
        check=False,
    )
    return proc


def ensure_reports_dir(d: Path) -> None:
    d.mkdir(parents=True, exist_ok=True)


def authenticate_if_needed(snyk_bin: Path) -> None:
    token = os.environ.get("SNYK_TOKEN")
    if not token:
        return
    # Non-interactive auth using provided token is idempotent
    run([str(snyk_bin), "auth", token])


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Snyk CLI scans and write reports")
    parser.add_argument("--project-root", default=str(Path(__file__).resolve().parents[1]), help="Root path to scan")
    parser.add_argument("--reports-dir", default="reports", help="Where to write outputs")
    parser.add_argument("--skip-oss", action="store_true", help="Skip Snyk Open Source (dependency) scan")
    parser.add_argument("--skip-code", action="store_true", help="Skip Snyk Code (SAST) scan")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any open issues are found")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing")

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    reports_dir = Path(args.reports_dir).resolve()

    snyk_bin = find_snyk_cli()
    if not snyk_bin:
        print("❌ Snyk CLI not found. Install it first (npm i -g snyk).", file=sys.stderr)
        return 2

    print(f"Using Snyk CLI: {snyk_bin}")

    if args.dry_run:
        print("--dry-run: Skipping authentication and scans")
        print(f"Would auth with token? {'yes' if os.environ.get('SNYK_TOKEN') else 'no'}")
        print(f"Project root: {project_root}")
        print(f"Reports dir: {reports_dir}")
        return 0

    authenticate_if_needed(snyk_bin)
    ensure_reports_dir(reports_dir)

    overall_exit_code = 0

    # 1) OSS (dependency) scan
    if not args.skip_oss:
        print("\n=== Snyk Open Source (dependencies) ===")
        req = project_root / "requirements.txt"
        if not req.exists():
            print(f"⚠️  requirements.txt not found at {req}, skipping OSS scan")
        else:
            oss_txt = reports_dir / "snyk_oss.txt"
            oss_json = reports_dir / "snyk_oss.json"

            # Prefer JSON file output for machine parsing while printing human text
            cmd = [
                str(snyk_bin),
                "test",
                f"--file={req}",
                "--package-manager=pip",
                "--strict-out-of-sync=false",
                f"--json-file-output={oss_json}",
            ]
            print("Running:", " ".join(cmd))
            res = run(cmd, cwd=project_root)
            if res.stdout:
                oss_txt.write_text(res.stdout, encoding="utf-8")
            print(res.stdout or "")

            try:
                data = json.loads(oss_json.read_text(encoding="utf-8"))
                vulns = len(data.get("issues", {}).get("vulnerabilities", []))
                print(f"OSS summary: {vulns} vulnerabilities reported")
                if args.strict and vulns > 0:
                    overall_exit_code = max(overall_exit_code, 1)
            except Exception as e:
                print(f"⚠️  Could not parse OSS JSON output: {e}")

    # 2) Code (SAST) scan
    if not args.skip_code:
        print("\n=== Snyk Code (SAST) ===")
        code_txt = reports_dir / "snyk_code.txt"
        code_sarif = reports_dir / "snyk_code.sarif"

        cmd = [
            str(snyk_bin),
            "code",
            "test",
            f"--sarif-file-output={code_sarif}",
        ]
        print("Running:", " ".join(cmd))
        res = run(cmd, cwd=project_root)
        if res.stdout:
            code_txt.write_text(res.stdout, encoding="utf-8")
        print(res.stdout or "")

        # Try to infer open issues count from sarif (optional)
        try:
            sarif = json.loads(code_sarif.read_text(encoding="utf-8"))
            results = sarif.get("runs", [{}])[0].get("results", [])
            open_issues = len(results)
            print(f"Code summary: {open_issues} issues reported")
            if args.strict and open_issues > 0:
                overall_exit_code = max(overall_exit_code, 1)
        except Exception as e:
            print(f"⚠️  Could not parse SARIF: {e}")

    if args.strict and overall_exit_code != 0:
        print("❌ Failing due to findings (strict mode)")

    print(f"\nReports written to: {reports_dir}")
    return overall_exit_code


if __name__ == "__main__":
    raise SystemExit(main())
