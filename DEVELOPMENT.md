# Development

Setup python virtual environment and install development dependencies

```bash
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Regenerate requirement files
pip-compile --extra=dev --generate-hashes --output-file=dev-requirements.txt pyproject.toml
pip-compile --generate-hashes --output-file=requirements.txt pyproject.toml

# Install dependencies
pip-sync
pip-sync dev-requirements.txt

# Build package
python -m build

# Install locally
pip install -e .

# Check pre-commit gates
pre-commit run --all-files

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

## molecule

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

or use molecule for single roles

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

## pre-commit

[pre-commit](https://pre-commit.com/) is used for several formatters and linters

Example execute pre-commit on all files

```bash
pre-commit run --all-files
```

But it's recommended to install the automatic git pre-commit hook by `pre-commit install`
