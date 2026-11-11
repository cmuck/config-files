"""Helpers shared by the command line tools of this repository."""

import subprocess
from pathlib import Path


def get_root_dir() -> Path:
    """Get the root directory of the Git repository."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    )
    return Path(result.stdout.strip())
