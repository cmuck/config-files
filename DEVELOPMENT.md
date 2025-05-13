# Development

## Setup development environment

Follow the instructions from [README.md](./README.md#setup-python-and-virtual-environment-using-uv) to setup Python and
create a virtual environment.

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

```shell
./scripts/test-roles.py
```

or use molecule on a single role

```shell
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

## Generate or upgrade Python dependencies

```shell
uv sync
```

## Further development commands

```shell
# Install locally
uv sync

# Create test coverage
ruff format
ruff check --fix
mypy .
```
