# Development

- [molecule](https://molecule.readthedocs.io/en/latest/) is used for testing Ansible roles
- [pre-commit](https://pre-commit.com/) is used for several formatters and linters

## molecule

The testing of Ansible roles is based on [molecule](https://molecule.readthedocs.io/en/stable/index.html).

- `molecule` provides support for testing with multiple instances, operating systems and distributions, virtualization
  providers, test frameworks and testing scenarios.
- `molecule` encourages an approach that results in consistently developed roles that are well-written, easily
  understood and maintained.
- `molecule` is already part of the virtual environment installation.

### Examples

Execute molecule for all roles

```bash
poetry run ./scripts/test-roles.sh
```

or use molecule for single roles

```bash
# Activate interactive poetry shell so that molecule can be executed
poetry shell
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

Example execution of pre-commit on all files

```bash
poetry run pre-commit run --all-files
```

But it's recommended to install the automatic git pre-commit hook by `poetry run pre-commit install`
