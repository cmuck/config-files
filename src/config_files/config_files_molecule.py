#!/usr/bin/env python3

import argparse
import hashlib
import logging
import os
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def get_parser() -> argparse.ArgumentParser:
    """Get CLI parser for molecule helper."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "changed_files",
        nargs="*",
        help="Optional changed file paths (e.g. from CI changed-files action)",
    )
    parser.add_argument(
        "-a",
        "--all-roles",
        action="store_true",
        help="Test all roles regardless of changed files",
    )
    parser.add_argument(
        "--strategy",
        choices=["auto", "pr", "schedule", "lock"],
        default="auto",
        help="Role selection strategy",
    )
    parser.add_argument(
        "--bucket-count",
        type=int,
        default=7,
        help="Number of buckets for round-robin selection",
    )
    parser.add_argument(
        "--bucket-index",
        type=int,
        default=None,
        help="Selected bucket index (0-based)",
    )
    parser.add_argument(
        "--max-roles",
        type=int,
        default=12,
        help="Maximum number of roles to test for strategy=pr",
    )
    parser.add_argument(
        "--critical-roles-file",
        default=".github/molecule-critical-roles.txt",
        help="Path to critical roles list",
    )
    parser.add_argument(
        "--seed",
        default=None,
        help="Optional bucket seed for deterministic selection",
    )
    return parser


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
    try:
        changed = (
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
        return [file for file in changed if file]
    except subprocess.CalledProcessError as exc:
        logger.warning("Failed to collect changed files via git diff: %s", exc)
        return []


def get_all_roles(root_dir: Path) -> list[Path]:
    """Get all roles from the roles directory."""
    roles_dir = root_dir / "roles"
    return [Path("roles") / d.name for d in roles_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]


def get_changed_roles(changed_files: List[str]) -> List[Path]:
    """Add roles that have changed files."""
    return [Path(f) for f in changed_files if f.startswith("roles/")]


def handle_uv(changed_files: List[str]) -> bool:
    """Handle uv.lock files."""
    return any(file.endswith("uv.lock") for file in changed_files)


def get_bucket_index(bucket_count: int, provided: int | None) -> int:
    """Compute a valid bucket index."""
    if bucket_count <= 0:
        return 0
    if provided is not None:
        return provided % bucket_count
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    return (day_of_year - 1) % bucket_count


def select_bucket_roles(
    roles: List[Path],
    bucket_count: int,
    bucket_index: int | None,
    seed: str | None,
) -> List[Path]:
    """Select roles by deterministic hash bucket."""
    if not roles:
        return []
    if bucket_count <= 1:
        return sorted(roles)

    selected_bucket = get_bucket_index(bucket_count, bucket_index)
    effective_seed = seed or os.environ.get("GITHUB_SHA") or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    selected: List[Path] = []
    for role in sorted(roles):
        role_hash = hashlib.sha256(f"{effective_seed}:{role.as_posix()}".encode()).hexdigest()
        role_bucket = int(role_hash, 16) % bucket_count
        if role_bucket == selected_bucket:
            selected.append(role)
    return selected


def load_critical_roles(root_dir: Path, critical_roles_file: str) -> List[Path]:
    """Load critical roles from a config file."""
    file_path = root_dir / critical_roles_file
    if not file_path.exists():
        return []

    valid_roles = set(get_all_roles(root_dir))
    critical_roles: List[Path] = []
    for raw_line in file_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        role = Path(line)
        if len(role.parts) == 1:
            role = Path("roles") / line
        if role in valid_roles:
            critical_roles.append(role)
    return critical_roles


def has_shared_infra_changes(changed_files: List[str]) -> bool:
    """Detect changes that can impact many roles."""
    shared_prefixes = (
        "group_vars/",
        "inventory/",
        "playbooks/",
    )
    shared_files = {
        "ansible.cfg",
        "requirements.yml",
        "pyproject.toml",
    }
    return any(
        file.startswith(shared_prefixes) or file in shared_files
        for file in changed_files
    )


def limit_roles(roles: List[Path], max_roles: int) -> List[Path]:
    """Limit amount of tested roles in resource-constrained contexts."""
    if max_roles <= 0:
        return roles
    return sorted(roles)[:max_roles]


def select_pr_roles(
    root_dir: Path,
    changed_files: List[str],
    bucket_count: int,
    bucket_index: int | None,
    max_roles: int,
    critical_roles_file: str,
    seed: str | None,
) -> List[Path]:
    """Select roles for pull request runs."""
    changed_roles = filter_duplicates(get_changed_roles(changed_files))
    if handle_uv(changed_files):
        logger.info("uv.lock changed, selecting critical roles plus rotating sample")
        critical_roles = load_critical_roles(root_dir, critical_roles_file)
        sampled = select_bucket_roles(
            get_all_roles(root_dir),
            bucket_count=max(5, bucket_count),
            bucket_index=bucket_index,
            seed=seed,
        )
        return filter_duplicates(critical_roles + sampled)

    if has_shared_infra_changes(changed_files):
        logger.info("Shared infra changed, including critical smoke roles")
        critical_roles = load_critical_roles(root_dir, critical_roles_file)
        changed_roles = filter_duplicates(changed_roles + critical_roles)

    return limit_roles(changed_roles, max_roles)


def select_schedule_roles(
    root_dir: Path,
    bucket_count: int,
    bucket_index: int | None,
    seed: str | None,
) -> List[Path]:
    """Select roles for scheduled/workflow_dispatch runs."""
    return select_bucket_roles(
        get_all_roles(root_dir),
        bucket_count=bucket_count,
        bucket_index=bucket_index,
        seed=seed,
    )


def determine_strategy(parsed_arguments: argparse.Namespace) -> str:
    """Resolve effective strategy."""
    if parsed_arguments.strategy != "auto":
        return parsed_arguments.strategy

    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    if event_name == "pull_request":
        return "pr"
    if event_name in ["schedule", "workflow_dispatch"]:
        return "schedule"
    return "pr"


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
    env = os.environ.copy()
    # molecule-plugins/docker expects task results to include `invocation`.
    env.setdefault("ANSIBLE_INJECT_INVOCATION", "True")
    subprocess.run(
        shlex.split(molecule_test_cmd), check=True, cwd=str(test_role), env=env
    )


def main() -> None:
    """Main function to execute the script."""
    parsed_arguments = get_parser().parse_args()
    root_dir = get_root_dir()

    test_roles: List[Path] = []
    changed_files: List[str] = []

    if parsed_arguments.changed_files:
        changed_files = [file for file in parsed_arguments.changed_files if file]

    strategy = determine_strategy(parsed_arguments)

    if strategy in ["pr", "lock"] and not changed_files:
        changed_files = get_changed_files(root_dir)
    logger.info("Selection strategy: %s", strategy)
    logger.info("Changed files: %s", changed_files)

    if parsed_arguments.all_roles:
        logger.info("--all-roles enabled, testing all roles")
        test_roles = get_all_roles(root_dir)
    elif strategy == "schedule":
        test_roles = select_schedule_roles(
            root_dir=root_dir,
            bucket_count=parsed_arguments.bucket_count,
            bucket_index=parsed_arguments.bucket_index,
            seed=parsed_arguments.seed,
        )
    elif strategy == "lock":
        test_roles = select_pr_roles(
            root_dir=root_dir,
            changed_files=changed_files + ["uv.lock"],
            bucket_count=parsed_arguments.bucket_count,
            bucket_index=parsed_arguments.bucket_index,
            max_roles=parsed_arguments.max_roles,
            critical_roles_file=parsed_arguments.critical_roles_file,
            seed=parsed_arguments.seed,
        )
    elif strategy == "pr":
        test_roles = select_pr_roles(
            root_dir=root_dir,
            changed_files=changed_files,
            bucket_count=parsed_arguments.bucket_count,
            bucket_index=parsed_arguments.bucket_index,
            max_roles=parsed_arguments.max_roles,
            critical_roles_file=parsed_arguments.critical_roles_file,
            seed=parsed_arguments.seed,
        )
    else:
        logger.info("No strategy matched, fallback to local changed roles")
        test_roles = handle_local_run(changed_files=changed_files)

    logger.info("Test roles: %s", test_roles)

    unique_test_roles = filter_duplicates(test_roles)

    logger.info("Unique test roles: %s", unique_test_roles)

    total_roles = len(unique_test_roles)
    if total_roles == 0:
        logger.info("No roles to test. Exiting.")
        return

    logger.info("Will execute %d role(s)", total_roles)

    executed = 0
    for role in unique_test_roles:
        logger.info("Testing role: %s (%d of %d)", role, executed + 1, total_roles)
        run_molecule(root_dir / role)
        executed += 1
        remaining = total_roles - executed
        logger.info(
            "Progress: executed=%d, remaining=%d, total=%d",
            executed,
            remaining,
            total_roles,
        )


if __name__ == "__main__":
    main()
