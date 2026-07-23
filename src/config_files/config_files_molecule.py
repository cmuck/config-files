#!/usr/bin/env python3

import argparse
import contextlib
import hashlib
import ipaddress
import logging
import os
import shlex
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator, List
from urllib.parse import urlparse

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

PROXY_ENV_NAMES = (
    "http_proxy",
    "https_proxy",
    "no_proxy",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "NO_PROXY",
)
LOCAL_PROXY_HOSTS = {"localhost"}


def proxy_environment_value(env: dict[str, str], name: str) -> str | None:
    """Return a proxy environment value independent of variable casing."""
    return env.get(name) or env.get(name.upper()) or env.get(name.lower())


def is_local_proxy_url(proxy_url: str) -> bool:
    """Check whether a proxy URL points at the local host."""
    value = proxy_url.strip()
    if not value:
        return False

    parsed_url = urlparse(value)
    if not parsed_url.hostname and "://" not in value:
        parsed_url = urlparse(f"http://{value}")

    hostname = parsed_url.hostname
    if not hostname:
        return False

    if hostname.lower() in LOCAL_PROXY_HOSTS:
        return True

    try:
        return ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        return False


def has_local_proxy(env: dict[str, str]) -> bool:
    """Check whether the current environment uses a loopback proxy."""
    return any(
        is_local_proxy_url(proxy_url)
        for proxy_url in (
            proxy_environment_value(env, "http_proxy"),
            proxy_environment_value(env, "https_proxy"),
        )
        if proxy_url
    )


def normalize_proxy_environment(env: dict[str, str]) -> dict[str, str]:
    """Set both upper- and lower-case proxy variables for Molecule interpolation."""
    proxy_env = env.copy()
    for name in ("http_proxy", "https_proxy", "no_proxy"):
        value = proxy_environment_value(env, name)
        if value:
            proxy_env[name] = value
            proxy_env[name.upper()] = value
    return proxy_env


def add_proxy_to_molecule_config(config: dict[str, Any]) -> dict[str, Any]:
    """Add local proxy Docker options to a Molecule config."""
    proxy_values = {name: f"${{{name}}}" for name in PROXY_ENV_NAMES}
    for platform in config.get("platforms", []):
        platform["network_mode"] = "host"
        platform["buildargs"] = proxy_values
        platform["env"] = proxy_values
    return config


@contextlib.contextmanager
def molecule_scenario(
    test_role: Path, env: dict[str, str]
) -> Generator[tuple[str, dict[str, str]]]:
    """Yield a Molecule scenario name and environment for this run."""
    if not has_local_proxy(env):
        yield "default", env
        return

    source_scenario = test_role / "molecule" / "default"
    generated_scenario = Path(
        tempfile.mkdtemp(prefix="cf_molecule_", dir=source_scenario.parent)
    )
    try:
        shutil.copytree(
            source_scenario, generated_scenario, symlinks=True, dirs_exist_ok=True
        )
        generated_config_file = generated_scenario / "molecule.yml"
        molecule_config = yaml.safe_load(generated_config_file.read_text())
        if generated_config_file.is_symlink():
            generated_config_file.unlink()
        generated_config_file.write_text(
            yaml.safe_dump(
                add_proxy_to_molecule_config(molecule_config),
                explicit_start=True,
                sort_keys=False,
            ),
        )
        logger.info(
            "Local proxy detected, using generated Molecule scenario: %s",
            generated_scenario.name,
        )
        yield generated_scenario.name, normalize_proxy_environment(env)
    finally:
        shutil.rmtree(generated_scenario, ignore_errors=True)


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
        "-r",
        "--role",
        "--roles",
        action="append",
        nargs="+",
        default=[],
        dest="roles",
        help="Role name or path to test. Can be passed multiple times.",
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
    return [
        Path("roles") / d.name
        for d in roles_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ]


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
    effective_seed = (
        seed
        or os.environ.get("GITHUB_SHA")
        or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    )

    selected: List[Path] = []
    for role in sorted(roles):
        role_hash = hashlib.sha256(
            f"{effective_seed}:{role.as_posix()}".encode()
        ).hexdigest()
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


def resolve_requested_roles(
    root_dir: Path, requested_roles: List[List[str]]
) -> List[Path]:
    """Resolve explicitly requested roles to repository-relative role paths."""
    role_paths: List[Path] = []
    for role_group in requested_roles:
        for role in role_group:
            role_path = Path(role)
            if len(role_path.parts) == 1:
                role_path = Path("roles") / role_path
            role_paths.append(role_path)

    valid_roles = set(get_all_roles(root_dir))
    resolved_roles = filter_duplicates(role_paths)
    invalid_roles = [role for role in resolved_roles if role not in valid_roles]
    if invalid_roles:
        invalid_role_names = ", ".join(
            role.as_posix() for role in sorted(invalid_roles)
        )
        raise ValueError(f"Unknown role(s): {invalid_role_names}")

    return resolved_roles


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
    env = os.environ.copy()
    # molecule-plugins/docker expects task results to include `invocation`.
    env.setdefault("ANSIBLE_INJECT_INVOCATION", "True")
    with molecule_scenario(test_role, env) as (scenario_name, molecule_env):
        molecule_test_cmd = f"molecule test --scenario-name {scenario_name}"
        subprocess.run(
            shlex.split(molecule_test_cmd),
            check=True,
            cwd=str(test_role),
            env=molecule_env,
        )


def main() -> None:
    """Main function to execute the script."""
    parser = get_parser()
    parsed_arguments = parser.parse_args()
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

    if parsed_arguments.roles:
        try:
            test_roles = resolve_requested_roles(root_dir, parsed_arguments.roles)
        except ValueError as exc:
            parser.error(str(exc))
        logger.info("Explicit roles selected: %s", test_roles)
    elif parsed_arguments.all_roles:
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
