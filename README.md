# config-files

[![CI](https://github.com/cmuck/config-files/actions/workflows/ci.yml/badge.svg?event=schedule)](https://github.com/cmuck/config-files/actions/workflows/ci.yml)

Setup your development environment based on Ansible routines for software provisioning, configuration management, and
application-deployment as infrastructure as code, tested with molecule.

## Installation

Follow the instructions at [INSTALL.md](./INSTALL.md)

## Usage

```sh
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
# Required pkg to install dependencies
pip install pip-tools
# Install runtime dependencies
pip-sync
# Install config-files in local venv
pip install -e .

```

```sh
./cf -h
usage: config-files [-h] [-t TAG [TAG ...]] [-v] [-d] [-c] playbook

positional arguments:
  playbook              Playbook from playbooks directory, e.g. "helloworld"

optional arguments:
  -h, --help            show this help message and exit
  -t TAG [TAG ...], --tag TAG [TAG ...]
                        Only tag from playbook is executed, e.g. --tag zsh git
  -v, --verbose         Increase verbosity of ansible to level 1
  -d, --dry-run         Execution with --check option
  -c, --check           Executes only a syntax-check of the playbook
```

### Examples

- Default usage

  ```sh
  cf developer
  ```

- Syntax-check of the playbook

  ```sh
  cf -c developer
  ```

- Dry-run of the playbook

  ```sh
  cf -d developer
  ```

- Execute specific tags of the playbook

  ```sh
  cf -t zsh git developer
  ```

- Increase verbosity

  ```sh
  cf -v developer
  ```

### Playbook helloworld

Can be used to check e.g. if config-files and Ansible works properly

```sh
cf helloworld
cf -v helloworld
cf -d helloworld
cf -c helloworld
```

## Development

Details at [DEVELOPMENT.md](./DEVELOPMENT.md)

## Links

- [Ansible Doc](https://docs.ansible.com/)
- [Ansible configuration settings](https://docs.ansible.com/ansible/2.8/reference_appendices/config.html)
- [Ansible FAQ](https://docs.ansible.com/ansible/latest/reference_appendices/faq.html)
- [Rapidly Build & Test Ansible Roles with Molecule + Docker](https://www.youtube.com/watch?v=DAnMyBZ8-Qs)
- [Testing Ansible Roles with Molecule Behind a Proxy](https://renaudmarti.net/posts/molecule-proxy-support/)
