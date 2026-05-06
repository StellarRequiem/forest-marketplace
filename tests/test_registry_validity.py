"""Asserts the v0.1 registry passes `tools/verify-manifest.py`.

This is the canonical CI gate: if any entry drifts from the schema in
`docs/manifest-schema.md`, this test fails and the PR is blocked.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
VERIFY_SCRIPT = REPO_ROOT / "tools" / "verify-manifest.py"


def test_registry_passes_verify_manifest():
    """Run verify-manifest.py as a subprocess and expect exit 0."""
    result = subprocess.run(
        [sys.executable, str(VERIFY_SCRIPT)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"verify-manifest.py exited {result.returncode}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
