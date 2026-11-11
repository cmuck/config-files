#!/usr/bin/env python3
"""Run Molecule for a selection of roles."""

import argparse
import logging
import os
import subprocess
from pathlib import Path

from config_files.molecule_proxy import molecule_scenario
from config_files.molecule_roles import (
    CHANGE_BASED_STRATEGIES,
    STRATEGIES,
    SelectionOptions,
    get_all_roles,
    get_changed_files,
    resolve_requested_roles,
)
from config_files.repository import get_root_dir

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
        "-r",
        "--role",
        "--roles",
        action="extend",
        nargs="+",
        default=[],
        dest="roles",
        help="Role name or path to test. Can be passed multiple times.",
    )
    parser.add_argument(
        "--strategy",
        choices=["auto", *STRATEGIES],
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


def determine_strategy(requested: str) -> str:
    """Resolve the effective strategy, derived from the GitHub event if not given."""
    if requested != "auto":
        return requested

    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    if event_name in ("schedule", "workflow_dispatch"):
        return "schedule"
    return "pr"


def select_roles(
    root_dir: Path,
    parsed_arguments: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> list[Path]:
    """Select the roles to test: explicit roles, all roles, or by strategy."""
    if parsed_arguments.roles:
        try:
            roles = resolve_requested_roles(root_dir, parsed_arguments.roles)
        except ValueError as exc:
            parser.error(str(exc))
        logger.info("Explicit roles selected: %s", roles)
        return roles

    if parsed_arguments.all_roles:
        logger.info("--all-roles enabled, testing all roles")
        return get_all_roles(root_dir)

    strategy = determine_strategy(parsed_arguments.strategy)
    changed_files = [file for file in parsed_arguments.changed_files if file]
    if strategy in CHANGE_BASED_STRATEGIES and not changed_files:
        changed_files = get_changed_files(root_dir)
    logger.info("Selection strategy: %s", strategy)
    logger.info("Changed files: %s", changed_files)

    options = SelectionOptions(
        bucket_count=parsed_arguments.bucket_count,
        bucket_index=parsed_arguments.bucket_index,
        max_roles=parsed_arguments.max_roles,
        critical_roles_file=parsed_arguments.critical_roles_file,
        seed=parsed_arguments.seed,
    )
    return STRATEGIES[strategy](root_dir, changed_files, options)


def run_molecule(test_role: Path) -> None:
    """Run the molecule test command for the given role."""
    env = os.environ.copy()
    # molecule-plugins/docker expects task results to include `invocation`.
    env.setdefault("ANSIBLE_INJECT_INVOCATION", "True")
    with molecule_scenario(test_role, env) as (scenario_name, molecule_env):
        subprocess.run(
            ["molecule", "test", "--scenario-name", scenario_name],
            check=True,
            cwd=test_role,
            env=molecule_env,
        )


def main() -> None:
    """Select roles and run Molecule for each of them."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    parser = get_parser()
    parsed_arguments = parser.parse_args()
    root_dir = get_root_dir()

    test_roles = select_roles(root_dir, parsed_arguments, parser)
    total_roles = len(test_roles)
    logger.info("Test roles: %s", test_roles)
    if total_roles == 0:
        logger.info("No roles to test. Exiting.")
        return

    logger.info("Will execute %d role(s)", total_roles)
    for executed, role in enumerate(test_roles, start=1):
        logger.info("Testing role: %s (%d of %d)", role, executed, total_roles)
        run_molecule(root_dir / role)
        logger.info(
            "Progress: executed=%d, remaining=%d, total=%d",
            executed,
            total_roles - executed,
            total_roles,
        )


if __name__ == "__main__":
    main()
