"""
Path safety helpers to prevent path traversal and normalize user-provided paths.

These helpers should be used when resolving paths that originate from untrusted
inputs (e.g., CLI arguments, tool parameters, or server requests).
"""
from __future__ import annotations

from pathlib import Path
from typing import Union


def normalize_path(p: Union[str, Path]) -> Path:
    """Return an absolute, normalized path without resolving symlinks strictly.

    Using resolve(strict=False) ensures '..' segments are collapsed while not
    requiring the path to exist.
    """
    return Path(p).expanduser().resolve(strict=False)


def assert_within_base(base: Union[str, Path], target: Union[str, Path]) -> Path:
    """Ensure target is within base directory; return absolute target path.

    Raises ValueError if the target escapes the base directory.
    """
    base_path = normalize_path(base)
    target_path = normalize_path(target)
    try:
        _ = target_path.relative_to(base_path)
    except ValueError:
        raise ValueError(f"Path {target_path} is outside of base directory {base_path}")
    return target_path


def safe_join(base: Union[str, Path], *parts: Union[str, Path]) -> Path:
    """Join parts to base and ensure the final path stays within base.

    Returns the absolute normalized path or raises ValueError if traversal detected.
    """
    candidate = Path(base)
    for part in parts:
        candidate = candidate / str(part)
    return assert_within_base(base, candidate)
