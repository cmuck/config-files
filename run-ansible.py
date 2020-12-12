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
        self.venv_path = self.base_path / "venv"
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

    @staticmethod
    def _print_tree(directory):
        file_marker = "f"
        directory_marker = "d"
        print (f'Temporary directory created: {directory}')
        print(f'{directory_marker} {directory}')
        for path in sorted(directory.rglob('*')):
            depth = len(path.relative_to(directory).parts)
            spacer = '    ' * depth
            file = path.name
            if path.is_symlink():
                file += " (symlink to " + str(path.resolve()) + ")"

            marker = file_marker
            if path.is_dir():
                marker = directory_marker

            print(f'{spacer}{marker} {file}')

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
        with tempfile.TemporaryDirectory() as tempdirname:
            tempdir = pathlib.Path(tempdirname)
            self._symlink_ansible_files(tempdir)

            ansible_args = [
                str(self.venv_path / "bin" / "ansible-playbook"), "-i", str(tempdir / "inventory"),
                str(tempdir / "playbook.yml"),
            ]

            ansible_args += ["--ask-become-pass"]

            if self.args.dry_run:
                ansible_args += ["--check"]
            if self.args.check:
                ansible_args += ["--syntax-check"]
            if self.args.tag:
                ansible_args += ["--tag"]
                ansible_args += [','.join(self.args.tag)]
            if self.args.verbose:
                ansible_args += ["-v"]
                self._print_tree(tempdir)
                print(f'Ansible is called with: {ansible_args}')

            res = subprocess.run(ansible_args, cwd=str(tempdir))
            if res.returncode != 0:
                exit(1)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("playbook",
                        help='Playbook from playbooks directory, e.g. "helloworld"')
    parser.add_argument("-t", "--tag", nargs="+",
                        help='Only tag from playbook is executed, e.g. --tag zsh git')
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
