# Development

## Setup development environment

The script execution is based on Python 3 and a virtual environment, so continue to install these dependencies.

```sh
sudo apt install python3 python3-pip python3-venv
```

Setup Python virtual environment and install development dependencies

```bash
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip-sync dev-requirements.txt
```

## Typical development

Changes shall be developed on feature-branches, tested by molecule and pre-commit locally and by
[CI](./.github/workflows/ci.yml).

Setup of git, usage of feature-branches and pushing is not explained in detail here, assumption is that you are familiar
with this tool.

### Check changes using `pre-commit`

[pre-commit](https://pre-commit.com/) is used for several formatters and linters

Example execute pre-commit on all files

```bash
pre-commit run --all-files
```

But it's recommended to install the automatic git pre-commit hook by `pre-commit install`

### Check changes using `molecule`

[molecule](https://molecule.readthedocs.io/en/latest/) is used for testing Ansible roles

- `molecule` provides support for testing with multiple instances, operating systems and distributions, virtualization
  providers, test frameworks and testing scenarios.
- `molecule` encourages an approach that results in consistently developed roles that are well-written, easily
  understood and maintained.
- `molecule` is already part of the virtual environment installation.

Example execute molecule for all roles

```bash
./scripts/test-roles.sh
```

or use molecule on a single role

```bash
# Execute molecule on a single role
cd roles/<role>
molecule test
# Run some parts of the test sequence with debug output
molecule --debug test
# Run some parts of the test sequence
molecule converge
# If nothing works anymore, try to destroy running stuff
molecule destroy
```

## Generate or upgrade Python `[dev-]requirements.txt`

```sh
# Regenerate requirement files
pip-compile --upgrade --extra=dev --generate-hashes --output-file=dev-requirements.txt pyproject.toml
pip-compile --upgrade --generate-hashes --output-file=requirements.txt pyproject.toml
```

## Further development commands

```sh
# Install locally
pip install -e .

# Build package
python -m build

# Create test coverage
coverage run -m pytest && coverage report -m
coverage run -m pytest && coverage html

# Format code
black --line-length=120 .

# Run unit tests
pytest

# Static type checker
mypy
```
