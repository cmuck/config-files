# config-files

[![CI](https://github.com/cmuck/config-files/actions/workflows/ci.yml/badge.svg?event=schedule)](https://github.com/cmuck/config-files/actions/workflows/ci.yml)

Setup your development environment based on Ansible routines for software provisioning, configuration management, and
application-deployment as infrastructure as code, tested with molecule.

## Installation

### Setup SSH for Ansible

Ansible is used to configure the system and requires a SSH connection.

First, ensure to have an up-to-date system

```shell
sudo apt update && sudo apt dist-upgrade
```

A vanilla Ubuntu installation missing

- `openssh-server` which is required by Ansible.
- `curl` which is required to install pyenv

```shell
sudo apt install openssh-server curl
```

Check if openssh-server is running

```shell
systemctl status ssh
```

Please re-use your existing SSH key if already created or
[create a new SSH key](https://help.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key)

### Setup Python and virtual environment using uv

The script is based on Python 3.12 and a virtual environment, so install these dependencies.

Install [uv](https://docs.astral.sh/uv)

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install Python 3.12 by

```shell
uv python install 3.12
```

Create the virtual environment

```shell
uv sync
```

Activate the virtual environment

```shell
source .venv/bin/activate
```

## Usage

When installed to the local virtual environment, you can use the script by the command `cf`

```shell
cf -h
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

  ```shell
  cf developer
  ```

- Syntax-check of the playbook

  ```shell
  cf -c developer
  ```

- Dry-run of the playbook

  ```shell
  cf -d developer
  ```

- Execute specific tags of the playbook

  ```shell
  cf -t zsh git developer
  ```

- Increase verbosity

  ```shell
  cf -v developer
  ```

### Playbook helloworld

Can be used to check e.g. if config-files and Ansible works properly

```shell
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
