"""Select the roles to test with Molecule."""

import hashlib
import logging
import os
import subprocess
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger(__name__)

ROLES_DIR = "roles"
BASE_REF = "origin/master"
LOCK_FILE = "uv.lock"
# Changes below these paths can affect every role.
SHARED_INFRA_PREFIXES = ("group_vars/", "inventory/", "playbooks/")
SHARED_INFRA_FILES = frozenset({"ansible.cfg", "requirements.yml", "pyproject.toml"})
# A lock file change tests a rotating sample of at least this many buckets.
LOCK_MIN_BUCKET_COUNT = 5


@dataclass(frozen=True)
class SelectionOptions:
    """Tunables shared by all selection strategies."""

    bucket_count: int
    bucket_index: int | None
    max_roles: int
    critical_roles_file: str
    seed: str | None


def to_role_path(value: str | Path) -> Path:
    """Map a role name or repository-relative path to the path of the role."""
    path = Path(value)
    return path if len(path.parts) > 1 else Path(ROLES_DIR) / path


def role_of(path: Path) -> Path | None:
    """Return the role directory a repository-relative path belongs to."""
    if len(path.parts) < 2 or path.parts[0] != ROLES_DIR:
        return None
    return Path(*path.parts[:2])


def unique_roles(paths: Iterable[Path]) -> list[Path]:
    """Reduce paths to the sorted, unique roles they belong to."""
    return sorted({role for path in paths if (role := role_of(path))})


def get_all_roles(root_dir: Path) -> list[Path]:
    """Get all roles from the roles directory."""
    return sorted(
        Path(ROLES_DIR) / entry.name
        for entry in (root_dir / ROLES_DIR).iterdir()
        if entry.is_dir() and not entry.name.startswith(".")
    )


def get_changed_files(root_dir: Path) -> list[str]:
    """Get the list of files changed in the current branch."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{BASE_REF}...HEAD"],
            check=True,
            cwd=root_dir,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        logger.warning("Failed to collect changed files via git diff: %s", exc)
        return []
    return [line for line in result.stdout.splitlines() if line]


def get_changed_roles(root_dir: Path, changed_files: list[str]) -> list[Path]:
    """Get the existing roles containing changed files."""
    valid_roles = set(get_all_roles(root_dir))
    return [
        role
        for role in unique_roles(Path(file) for file in changed_files)
        if role in valid_roles
    ]


def resolve_requested_roles(root_dir: Path, requested_roles: list[str]) -> list[Path]:
    """Resolve explicitly requested roles to repository-relative role paths."""
    resolved_roles = unique_roles(to_role_path(role) for role in requested_roles)
    valid_roles = set(get_all_roles(root_dir))
    invalid_roles = [role for role in resolved_roles if role not in valid_roles]
    if invalid_roles:
        names = ", ".join(role.as_posix() for role in invalid_roles)
        raise ValueError(f"Unknown role(s): {names}")
    return resolved_roles


def load_critical_roles(root_dir: Path, critical_roles_file: str) -> list[Path]:
    """Load critical roles from a config file."""
    file_path = root_dir / critical_roles_file
    if not file_path.exists():
        return []

    valid_roles = set(get_all_roles(root_dir))
    critical_roles: list[Path] = []
    for raw_line in file_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        role = to_role_path(line)
        if role in valid_roles:
            critical_roles.append(role)
        else:
            logger.warning("Ignoring unknown critical role: %s", line)
    return critical_roles


def has_shared_infra_changes(changed_files: list[str]) -> bool:
    """Detect changes that can impact many roles."""
    return any(
        file.startswith(SHARED_INFRA_PREFIXES) or file in SHARED_INFRA_FILES
        for file in changed_files
    )


def has_lock_file_change(changed_files: list[str]) -> bool:
    """Detect changes of the dependency lock file."""
    return any(file.endswith(LOCK_FILE) for file in changed_files)


def limit_roles(roles: list[Path], max_roles: int) -> list[Path]:
    """Limit amount of tested roles in resource-constrained contexts."""
    ordered = sorted(roles)
    return ordered[:max_roles] if max_roles > 0 else ordered


def get_bucket_index(bucket_count: int, provided: int | None) -> int:
    """Compute a valid bucket index."""
    if bucket_count <= 0:
        return 0
    if provided is not None:
        return provided % bucket_count
    day_of_year = datetime.now(UTC).timetuple().tm_yday
    return (day_of_year - 1) % bucket_count


def select_bucket_roles(
    roles: list[Path],
    bucket_count: int,
    bucket_index: int | None,
    seed: str | None,
) -> list[Path]:
    """Select roles by deterministic hash bucket."""
    if bucket_count <= 1:
        return sorted(roles)

    selected_bucket = get_bucket_index(bucket_count, bucket_index)
    effective_seed = (
        seed or os.environ.get("GITHUB_SHA") or datetime.now(UTC).strftime("%Y-%m-%d")
    )

    def bucket_of(role: Path) -> int:
        digest = hashlib.sha256(f"{effective_seed}:{role.as_posix()}".encode())
        return int(digest.hexdigest(), 16) % bucket_count

    return [role for role in sorted(roles) if bucket_of(role) == selected_bucket]


def select_pr_roles(
    root_dir: Path, changed_files: list[str], options: SelectionOptions
) -> list[Path]:
    """Select roles for pull request runs."""
    if has_lock_file_change(changed_files):
        logger.info(
            "%s changed, selecting critical roles plus rotating sample", LOCK_FILE
        )
        sampled = select_bucket_roles(
            get_all_roles(root_dir),
            bucket_count=max(LOCK_MIN_BUCKET_COUNT, options.bucket_count),
            bucket_index=options.bucket_index,
            seed=options.seed,
        )
        critical_roles = load_critical_roles(root_dir, options.critical_roles_file)
        return unique_roles(critical_roles + sampled)

    changed_roles = get_changed_roles(root_dir, changed_files)
    if has_shared_infra_changes(changed_files):
        logger.info("Shared infra changed, including critical smoke roles")
        changed_roles += load_critical_roles(root_dir, options.critical_roles_file)
    return limit_roles(unique_roles(changed_roles), options.max_roles)


def select_lock_roles(
    root_dir: Path, changed_files: list[str], options: SelectionOptions
) -> list[Path]:
    """Select roles as if the lock file changed, e.g. to simulate a dependency update."""
    return select_pr_roles(root_dir, [*changed_files, LOCK_FILE], options)


def select_schedule_roles(
    root_dir: Path, _changed_files: list[str], options: SelectionOptions
) -> list[Path]:
    """Select roles for scheduled/workflow_dispatch runs, ignoring changed files."""
    return select_bucket_roles(
        get_all_roles(root_dir),
        bucket_count=options.bucket_count,
        bucket_index=options.bucket_index,
        seed=options.seed,
    )


Strategy = Callable[[Path, list[str], SelectionOptions], list[Path]]

STRATEGIES: dict[str, Strategy] = {
    "pr": select_pr_roles,
    "lock": select_lock_roles,
    "schedule": select_schedule_roles,
}
# Strategies whose selection depends on the changed files.
CHANGE_BASED_STRATEGIES = frozenset({"pr", "lock"})
