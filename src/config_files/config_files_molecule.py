#!/usr/bin/env python3

import logging
import os
import sys
import shlex
import subprocess
from pathlib import Path
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def get_root_dir() -> Path:
    """Get the root directory of the Git repository."""
    git_root_cmd = "git rev-parse --show-toplevel"
    return Path(
        subprocess.run(
            shlex.split(git_root_cmd), check=True, capture_output=True, text=True
        ).stdout.strip()
    )


def check_github_execution() -> bool:
    """Check if the script is running in a GitHub Actions environment."""
    return bool(os.environ.get("GITHUB_EVENT_NAME"))


def get_changed_files(root_dir: Path) -> List[str]:
    """Get the list of changed files in the current branch."""
    cmd = "git diff --name-only HEAD..origin/master"
    return (
        subprocess.run(
            shlex.split(cmd),
            check=True,
            cwd=str(root_dir),
            capture_output=True,
            text=True,
        )
        .stdout.strip()
        .split("\n")
    )


def get_all_roles(root_dir: Path) -> list[Path]:
    """Get all roles from the roles directory."""
    return [d for d in Path(f"{root_dir}/roles").iterdir() if d.is_dir()]


def get_changed_roles(changed_files: List[str]) -> List[Path]:
    """Add roles that have changed files."""
    return [Path(f) for f in changed_files if "roles/" in f]


def handle_uv(changed_files: List[str]) -> bool:
    """Handle uv.lock files."""
    return any(file.endswith("uv.lock") for file in changed_files)


def handle_github(changed_files: List[str]) -> List[Path]:
    """Handle GitHub-specific execution."""
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    if event_name == "pull_request":
        return get_changed_roles(changed_files)
    if event_name in ["schedule", "workflow_dispatch"]:
        return get_all_roles(get_root_dir())
    return []


def handle_local_run(changed_files: List[str]) -> List[Path]:
    """Handle local execution."""
    return get_changed_roles(changed_files)


def filter_duplicates(roles: List[Path]) -> List[Path]:
    """Remove duplicate roles from the list."""
    unique_roles = set()
    for role in roles:
        if "roles" in role.parts:
            roles_index = role.parts.index("roles")
            result_path = Path(*role.parts[: (roles_index + 2)])
            unique_roles.add(result_path)
    return list(unique_roles)


def run_molecule(test_role: Path) -> None:
    """Run the molecule test command for the given role."""
    molecule_test_cmd = "molecule test"
    subprocess.run(shlex.split(molecule_test_cmd), check=True, cwd=str(test_role))


def main() -> None:
    """Main function to execute the script."""
    test_roles: List[Path] = []

    changed_files = get_changed_files(get_root_dir())
    logger.info("Changed files: %s", changed_files)

    if handle_uv(changed_files=changed_files):
        logger.info("uv.lock file found, testing all roles")
        test_roles = get_all_roles(get_root_dir())
    elif check_github_execution():
        logger.info("Running in GitHub Actions")
        test_roles = handle_github(sys.argv[1:])
    else:
        logger.info("Running locally")
        test_roles = handle_local_run(changed_files=changed_files)

    logger.info("Test roles: %s", test_roles)

    unique_test_roles = filter_duplicates(test_roles)

    logger.info("Unique test roles: %s", unique_test_roles)

    for role in unique_test_roles:
        logger.info("Testing role: %s", role)
        run_molecule(get_root_dir() / role)


if __name__ == "__main__":
    main()
