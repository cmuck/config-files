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
uv run cf-molecule --all-roles
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

When running Molecule through `cf-molecule` behind a local proxy, export the usual proxy variables before starting the
test:

```shell
export http_proxy=http://127.0.0.1:<port>
export https_proxy=http://127.0.0.1:<port>
export no_proxy=127.0.0.1,localhost,::1
```

`cf-molecule` detects loopback proxy URLs such as `localhost`, `127.0.0.1`, and `::1`. When such a proxy is present, it
creates a temporary Molecule scenario that passes these variables as Docker build arguments and container environment
variables, with host networking so proxy URLs bound to localhost on the host are reachable while Molecule builds the
Ubuntu test images. Without a loopback proxy, the default scenario is used without proxy build arguments or container
environment variables.

### CI molecule strategy

CI no longer executes all roles for scheduled runs or lock-file changes.

The selector is implemented in [src/config_files/config_files_molecule.py](./src/config_files/config_files_molecule.py)
and configured in [ci.yml](./.github/workflows/ci.yml).

- pull request strategy (`--strategy pr`)
  - tests changed roles
  - if shared infrastructure files changed (`group_vars/`, `inventory/`, `playbooks/`, `ansible.cfg`,
    `requirements.yml`, `pyproject.toml`) the critical smoke roles are added
  - if `uv.lock` changed, tests critical smoke roles plus a rotating bucket sample instead of all roles
  - role count is capped with `--max-roles`
- schedule and workflow dispatch strategy (`--strategy schedule`)
  - tests one round-robin bucket per run via `--bucket-count` and `--bucket-index`
  - gives full-role coverage over multiple days while keeping each run bounded

Critical smoke roles are listed in
[molecule-critical-roles.txt](./.github/molecule-critical-roles.txt).

Local examples:

```shell
# Test specific roles by name or path
uv run cf-molecule --roles git zsh
uv run cf-molecule --role roles/eza --role roles/krew

# Pull request-style selection from changed files
uv run cf-molecule --strategy pr roles/git/tasks/main.yml roles/zsh/tasks/main.yml

# Simulate lock-file behavior (critical smoke + rotating sample)
uv run cf-molecule --strategy lock --bucket-count 5 --bucket-index 2

# Simulate scheduled round-robin run
uv run cf-molecule --strategy schedule --bucket-count 7 --bucket-index 0

# Force full test set (manual only)
uv run cf-molecule --all-roles
```

## Generate or upgrade Python dependencies

```shell
uv sync
```

## Further development commands

```shell
ruff format
ruff check --fix
```
