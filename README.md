# config-files

[![CI](https://github.com/cmuck/config-files/actions/workflows/ci.yml/badge.svg?event=schedule)](https://github.com/cmuck/config-files/actions/workflows/ci.yml)

Setup your development environment based on Ansible routines for software provisioning, configuration management, and
application-deployment as infrastructure as code, tested with molecule.

## Installation

Follow the instructions at [INSTALL.md](./INSTALL.md)

## Usage

```sh
python3 -m venv venv
source venv/bin/activate
pip install pip-tools
pip-sync requirements.txt
```

```sh
./config-files -h
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
  config-files developer
  ```

- Syntax-check of the playbook

  ```sh
  config-files -c developer
  ```

- Dry-run of the playbook

  ```sh
  config-files -d developer
  ```

- Execute specific tags of the playbook

  ```sh
  config-files -t zsh git developer
  ```

- Increase verbosity

  ```sh
  config-files -v developer
  ```

### Playbook helloworld

Can be used to check e.g. if config-files and Ansible works properly

```sh
config-files helloworld
config-files -v helloworld
config-files -d helloworld
config-files -c helloworld
```

## Development

Details at [DEVELOPMENT.md](./DEVELOPMENT.md)

## Links

- [Ansible Doc](https://docs.ansible.com/)
- [Ansible configuration settings](https://docs.ansible.com/ansible/2.8/reference_appendices/config.html)
- [Ansible FAQ](https://docs.ansible.com/ansible/latest/reference_appendices/faq.html)
- [Rapidly Build & Test Ansible Roles with Molecule + Docker](https://www.youtube.com/watch?v=DAnMyBZ8-Qs)
- [Testing Ansible Roles with Molecule Behind a Proxy](https://renaudmarti.net/posts/molecule-proxy-support/)
