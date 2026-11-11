#!/usr/bin/env python3
"""Run a playbook of the playbooks directory with the roles of this repository."""

import argparse
import subprocess
import sys
import tempfile
from collections.abc import Generator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from config_files.repository import get_root_dir

# Repository entries linked next to the playbook so that Ansible finds them
# relative to the playbook, independent of the current working directory.
WORKSPACE_ENTRIES = ("roles", "group_vars", "inventory", "ansible.cfg")
PLAYBOOK_LINK = "playbook.yml"


@dataclass(frozen=True)
class PlaybookOptions:
    """Options of a single playbook execution."""

    playbook: str
    tags: Sequence[str] = ()
    verbose: bool = False
    dry_run: bool = False
    syntax_check: bool = False


def playbook_path(root_dir: Path, playbook: str) -> Path:
    """Get the file of a playbook given by its name."""
    return root_dir / "playbooks" / f"{playbook}.yml"


@contextmanager
def workspace(root_dir: Path, playbook: str) -> Generator[Path]:
    """Yield a temporary directory linking the playbook and everything it needs."""
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        for entry in WORKSPACE_ENTRIES:
            (directory / entry).symlink_to(root_dir / entry)
        (directory / PLAYBOOK_LINK).symlink_to(playbook_path(root_dir, playbook))
        yield directory


def print_tree(directory: Path) -> None:
    """Print the content of the workspace to ease debugging."""
    print(f"Temporary directory created: {directory}")
    print(f"d {directory}")
    for path in sorted(directory.rglob("*")):
        indent = "    " * len(path.relative_to(directory).parts)
        marker = "d" if path.is_dir() else "f"
        target = f" (symlink to {path.resolve()})" if path.is_symlink() else ""
        print(f"{indent}{marker} {path.name}{target}")


def build_command(options: PlaybookOptions, directory: Path) -> list[str]:
    """Build the ansible-playbook command line for the workspace."""
    command = [
        "ansible-playbook",
        "--ask-become-pass",
        "--inventory",
        str(directory / "inventory"),
        str(directory / PLAYBOOK_LINK),
    ]
    if options.dry_run:
        command.append("--check")
    if options.syntax_check:
        command.append("--syntax-check")
    if options.tags:
        command += ["--tags", ",".join(options.tags)]
    if options.verbose:
        command.append("--verbose")
    return command


def run_playbook(root_dir: Path, options: PlaybookOptions) -> int:
    """Run the playbook and return the exit code of Ansible."""
    with workspace(root_dir, options.playbook) as directory:
        command = build_command(options, directory)
        if options.verbose:
            print_tree(directory)
            print(f"Ansible is called with: {' '.join(command)}")
        return subprocess.run(command, cwd=directory, check=False).returncode


def get_parser() -> argparse.ArgumentParser:
    """Get CLI parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "playbook", help='Playbook from playbooks directory, e.g. "helloworld"'
    )
    parser.add_argument(
        "-t",
        "--tag",
        action="extend",
        type=lambda value: value.split(","),
        default=[],
        help="Only these tags of the playbook are executed. Comma separated and/or "
        "repeatable, e.g. --tag zsh,git or -t zsh -t git",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase verbosity of ansible to level 1",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Execution with --check option",
    )
    parser.add_argument(
        "-c",
        "--check",
        action="store_true",
        help="Executes only a syntax-check of the playbook",
    )
    return parser


def main() -> None:
    """Parse the command line and run the requested playbook."""
    parser = get_parser()
    arguments = parser.parse_args()
    root_dir = get_root_dir()
    if not playbook_path(root_dir, arguments.playbook).is_file():
        parser.error(f"Unknown playbook: {arguments.playbook}")

    options = PlaybookOptions(
        playbook=arguments.playbook,
        tags=arguments.tag,
        verbose=arguments.verbose,
        dry_run=arguments.dry_run,
        syntax_check=arguments.check,
    )
    sys.exit(run_playbook(root_dir, options))


if __name__ == "__main__":
    main()
