#!/usr/bin/env python3

import subprocess
import pathlib
import sys
import shutil
import tempfile
import argparse


class AnsibleFacade:
    def __init__(self, args):
        self.base_path = pathlib.Path(__file__).resolve().parent
        self.venv_path = self.base_path / ".venv"
        self.args = args

        self._setup_venv()

    def _setup_venv(self):
        requirements = self.base_path / "requirements.txt"
        venv_requirements = self.venv_path / "installed-requirements.txt"

        if venv_requirements.exists() and \
                venv_requirements.read_bytes() == requirements.read_bytes():
            return

        shutil.rmtree(self.venv_path, ignore_errors=True)
        subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)
        subprocess.run([
            str(self.venv_path / "bin" / "pip"), "install", "-r", str(requirements),
        ], check=True)
        shutil.copy(str(requirements), str(venv_requirements))
        print("Created venv and installed requirements")

    def _symlink_ansible_files(self, tempdir):
        if tempdir.exists():
            (tempdir / "roles").symlink_to(self.base_path / "roles")
            (tempdir / "group_vars").symlink_to(self.base_path / "group_vars")
            # (tempdir / "play" / "host_vars").symlink_to(self.base_path / "host_vars")
            (tempdir / "playbook.yml").symlink_to(
                self.base_path / "playbooks" / (self.args.playbook + ".yml")
            )
            (tempdir / "inventory").symlink_to(self.base_path / "inventory")
            (tempdir / "ansible.cfg").symlink_to(self.base_path / "ansible.cfg")

    def run_playbook(self):
        tempdir = pathlib.Path(tempfile.mkdtemp())
        try:
            self._symlink_ansible_files(tempdir)

            ansible_args = [
                str(self.venv_path / "bin" / "ansible-playbook"), "-i", str(tempdir / "inventory"),
                str(tempdir / "playbook.yml"),
            ]

            ansible_args += ["--ask-become-pass"]

            if self.args.verbose:
                ansible_args += ["-v"]
            if self.args.dry_run:
                ansible_args += ["--check"]
            if self.args.check:
                ansible_args += ["--syntax-check"]
            if self.args.tag:
                ansible_args += ["--tag"]
                ansible_args += [','.join(self.args.tag)]

            res = subprocess.run(ansible_args, cwd=str(tempdir))
            if res.returncode != 0:
                exit(1)
        finally:
            shutil.rmtree(str(tempdir), ignore_errors=True)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("playbook",
                        help='Playbook from playbooks directory, e.g. "helloworld"')
    parser.add_argument("-t", "--tag", action='append',
                        help='Only tag from playbook is executed, e.g. --tag zsh --tag git')
    parser.add_argument("-v", "--verbose", action="store_true",
                        help='Increase verbosity of ansible to level 1')
    parser.add_argument("-d", "--dry-run", action="store_true",
                        help='Execution with --check option')
    parser.add_argument("-c", "--check", action="store_true",
                        help='Executes only a syntax-check of the playbook')

    return parser.parse_args()


if __name__ == "__main__":
    parsed_arguments = parse_arguments()

    if parsed_arguments.playbook:
        ansible_facade = AnsibleFacade(parsed_arguments)
        ansible_facade.run_playbook()