#!/usr/bin/env python3

import argparse
import shlex
import subprocess
import tempfile
from pathlib import Path


class AnsibleFacade:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.base_path = Path.cwd()

    @staticmethod
    def _print_tree(directory: Path) -> None:
        file_marker = "f"
        directory_marker = "d"
        print(f"Temporary directory created: {directory}")
        print(f"{directory_marker} {directory}")
        for path in sorted(directory.rglob("*")):
            depth = len(path.relative_to(directory).parts)
            spacer = "    " * depth
            file = path.name
            if path.is_symlink():
                file += " (symlink to " + str(path.resolve()) + ")"
            marker = file_marker
            if path.is_dir():
                marker = directory_marker
            print(f"{spacer}{marker} {file}")

    def _symlink_ansible_files(self, tempdir: Path) -> None:
        if tempdir.exists():
            (tempdir / "roles").symlink_to(self.base_path / "roles")
            (tempdir / "group_vars").symlink_to(self.base_path / "group_vars")
            (tempdir / "playbook.yml").symlink_to(self.base_path / "playbooks" / (self.args.playbook + ".yml"))
            (tempdir / "inventory").symlink_to(self.base_path / "inventory")
            (tempdir / "ansible.cfg").symlink_to(self.base_path / "ansible.cfg")

    def run_playbook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tempdir = Path(tmp)
            self._symlink_ansible_files(tempdir)

            ansible_args = f"ansible-playbook --ask-become-pass --inventory {tempdir}/inventory {tempdir}/playbook.yml"
            if self.args.dry_run:
                ansible_args += " --check"
            if self.args.check:
                ansible_args += " --syntax-check"
            if self.args.tag:
                ansible_args += " --tag "
                ansible_args += ",".join(self.args.tag)
            if self.args.verbose:
                ansible_args += " --verbose"
                self._print_tree(tempdir)
                print(f"Ansible is called with: {ansible_args}")

            res = subprocess.run(shlex.split(ansible_args), cwd=str(tempdir))
            if res.returncode != 0:
                exit(1)


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("playbook", help='Playbook from playbooks directory, e.g. "helloworld"')
    parser.add_argument(
        "-t",
        "--tag",
        nargs="+",
        help="Only tag from playbook is executed, e.g. --tag zsh git",
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
    parsed_arguments = get_parser().parse_args()
    AnsibleFacade(parsed_arguments).run_playbook()


if __name__ == "__main__":
    main()
