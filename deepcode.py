#!/usr/bin/env python3
"""
DeepCode - AI Research Engine Launcher

Next-Generation AI Research Automation Platform
Transform research papers into working code automatically
Provides a lightweight cross-platform CLI for launching the Streamlit UI and
running paper test workflows.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Tuple

# Fix UTF-8 encoding for Windows console at the very start
if sys.platform == 'win32':
    # Attempt to set UTF-8 encoding
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


    # Always wrap print on Windows to catch any remaining UnicodeEncodeError

    _original_print = print

    def print(*args, **kwargs):
        try:
            _original_print(*args, **kwargs)
        except UnicodeEncodeError:
            # Fallback: encode with errors='replace'
            safe_args = []
            for arg in args:
                if isinstance(arg, str):
                    # Replace unencodable characters
                    encoding = sys.stdout.encoding or 'ascii'
                    safe_args.append(arg.encode(encoding, errors='replace').decode(encoding))
                else:
                    safe_args.append(arg)
            try:
                _original_print(*safe_args, **kwargs)
            except Exception:
                # If it still fails, purely ascii fallback
                ascii_args = [
                    str(a).encode('ascii', errors='replace').decode('ascii') 
                    for a in args
                ]
                _original_print(*ascii_args, **kwargs)

    import builtins
    builtins.print = print


def print_banner() -> None:
    """Display a simple ASCII banner."""
    banner = (
        "\n"
        "##############################################################\n"
        "# DeepCode - AI Research Engine                              #\n"
        "# Transform research papers into working code automatically  #\n"
        "##############################################################\n"
    )
    print(banner)


def check_dependencies() -> bool:
    """Check required Python packages and optional system tools."""
    print("Checking Python dependencies...")

    required_modules: Iterable[Tuple[str, str]] = (
        ("streamlit", "streamlit>=1.28.0"),
        ("yaml", "pyyaml"),
        ("asyncio", "asyncio"),
    )
    optional_modules: Iterable[Tuple[str, str]] = (("reportlab", "reportlab"),)

    missing_required = []
    missing_optional = []

    for module_name, install_name in required_modules:
        if importlib.util.find_spec(module_name) is None:
            missing_required.append(install_name)
            print(f"  - missing {install_name}")
        else:
            print(f"  - found {module_name}")

    for module_name, install_name in optional_modules:
        if importlib.util.find_spec(module_name) is None:
            missing_optional.append(install_name)
            print(f"  - optional dependency missing: {install_name}")
        else:
            print(f"  - optional dependency available: {module_name}")

    libreoffice_cmd = shutil.which("libreoffice") or shutil.which("soffice")
    if libreoffice_cmd:
        print(f"Found LibreOffice executable: {libreoffice_cmd}")
    else:
        print(
            "LibreOffice not detected. Office document conversions will be skipped."
        )

    if missing_required:
        print("\nInstall missing dependencies with:")
        print(f"  pip install {' '.join(missing_required)}")
        return False

    if missing_optional:
        print(
            "\nOptional dependencies missing. Some features may be limited until they "
            "are installed."
        )

    return True


def cleanup_cache(root: Path) -> None:
    """Remove __pycache__ directories and .pyc files under *root*."""
    print("\nCleaning Python cache artifacts...")
    removed_dirs = 0
    removed_files = 0

    for dir_path in root.rglob("__pycache__"):
        try:
            shutil.rmtree(dir_path)
            removed_dirs += 1
        except Exception as exc:  # pragma: no cover - best effort cleanup
            print(f"  could not delete {dir_path}: {exc}")

    for file_path in root.rglob("*.pyc"):
        try:
            file_path.unlink()
            removed_files += 1
        except Exception as exc:  # pragma: no cover - best effort cleanup
            print(f"  could not delete {file_path}: {exc}")

    print(f"Removed {removed_dirs} __pycache__ directories and {removed_files} .pyc files.")


def launch_paper_test(paper_name: str, fast_mode: bool) -> None:
    """Launch the paper test workflow."""
    print(f"\nLaunching paper test workflow for '{paper_name}'")
    print(f"Fast mode: {'enabled' if fast_mode else 'disabled'}")

    cmd = [sys.executable, "test_paper.py", paper_name]
    if fast_mode:
        cmd.append("--fast")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"Paper test workflow failed: {exc}")
        sys.exit(exc.returncode)

    print("Paper test workflow finished successfully.")
    print("Generated artifacts can be found under deepcode_lab/papers/")
    print("Next steps:")
    print("  1. Install MCP dependencies: pip install -r requirements.txt")
    print(
        "  2. Run the full pipeline: "
        f"python -m workflows.paper_test_engine --paper {paper_name}"
        + (" --fast" if fast_mode else "")
    )


def launch_streamlit(app_path: Path) -> None:
    """Launch the Streamlit UI."""
    print(f"Starting Streamlit app at {app_path}")
    print("🌐 Starting DeepCode web interface...")
    print("🚀 Launching on http://localhost:8503")
    print("=" * 70)
    print("💡 Tip: Keep this terminal open while using the application")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 70)
    
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        "8503",
        "--server.address",
        "localhost",
        "--browser.gatherUsageStats",
        "false",
        "--theme.base",
        "dark",
        "--theme.primaryColor",
        "#3b82f6",
        "--theme.backgroundColor",
        "#0f1419",
        "--theme.secondaryBackgroundColor",
        "#1e293b",
    ]

    # Set UTF-8 encoding for subprocess
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONLEGACYWINDOWSSTDIO"] = "utf-8"

    try:
        subprocess.run(cmd, check=True, env=env)
    except KeyboardInterrupt:
        print("\n\n🛑 DeepCode server stopped by user")
        print("Thank you for using DeepCode! 🧬")
    except subprocess.CalledProcessError as exc:
        print(f"\n❌ Failed to launch Streamlit: {exc}")
        print("Please check if Streamlit is properly installed.")
        sys.exit(exc.returncode)


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="DeepCode launcher",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command")

    test_parser = subparsers.add_parser(
        "test", help="Run the paper test workflow"
    )
    test_parser.add_argument("paper", help="Paper identifier, e.g. 'rice'")
    test_parser.add_argument(
        "--fast",
        "-f",
        action="store_true",
        help="Skip long-running steps when preparing the test",
    )

    return parser


def main(argv: Iterable[str] | None = None) -> None:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parent

    if args.command == "test":
        print_banner()
        launch_paper_test(args.paper, args.fast)
        return

    print_banner()

    if not check_dependencies():
        print("\nInstall the missing dependencies and try again.")
        sys.exit(1)

    streamlit_app = project_root / "ui" / "streamlit_app.py"
    if not streamlit_app.exists():
        print(f"Streamlit app not found at {streamlit_app}")
        sys.exit(1)

    launch_streamlit(streamlit_app)
    cleanup_cache(project_root)


if __name__ == "__main__":
    main()
