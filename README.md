[![Build Status](https://travis-ci.com/cmuck/config-files.svg?branch=master)](https://travis-ci.com/cmuck/config-files)




# config-files

Software provisioning, configuration management, and application-deployment for developers based on Ansible.

## Prerequisites

Follow the instructions at [INSTALL.md](./INSTALL.md)

## Usage

### Command line options

Run `./setup.py --help` to see the available options.

```sh
./setup.py --help
usage: setup.py [-h] [-t TAG] [-v] [-d] [-c] playbook

positional arguments:
  playbook           Playbook from playbooks directory, e.g. "helloworld"

optional arguments:
  -h, --help         show this help message and exit
  -t TAG, --tag TAG  Only tag from playbook is executed, e.g. --tag git --tag
                     ssh
  -v, --verbose      Increase verbosity of ansible to level 1
  -d, --dry-run      Execution with --check option
  -c, --check        Executes only a syntax-check of the playbook

```

### Playbook development

* Default usage
    ```sh
    ./setup.py developer
    ```
* Syntax-check of the playbook
    ```sh
    ./setup.py -c developer
    ```
* Dry-run of the playbook
    ```sh
    ./setup.py -d developer
    ```
* Execute specific tags of the playbook
    ```sh
    ./setup.py -t zsh -t git developer
    ```
* Increase verbosity
    ```sh
    ./setup.py -v developer
    ```

### Playbook helloworld

Can be used to check e.g. if config-files and Ansible works properly

```sh
./setup.py helloworld
./setup.py -v helloworld
./setup.py -d helloworld
./setup.py -c helloworld
```

## Testing

The testing of Ansible roles is based on [molecule](https://molecule.readthedocs.io/en/stable/index.html).

* `molecule` provides support for testing with multiple instances, operating systems and distributions, virtualization providers, test frameworks and testing scenarios.
* `molecule` encourages an approach that results in consistently developed roles that are well-written, easily understood and maintained.
* `molecule` is already part of the virtual environment installation.

### Example

```sh
# Activate venv so that ansible, molecule etc. is available
source .venv/bin/activate

# Change directory to the explict role which sould be tested
cd ./roles/<role>

# Run complete test sequence
molecule test

# Run some parts of the test sequence
molecule converge

# Run some parts of the test sequence with debug output
molecule --debug test

# Run lint
molecule lint

# If nothing works anymore, try to destroy running stuff
molecule destroy

# Add molecule to already existing role
cd ./roles/<role>
molecule init scenario -r <role> -d docker

# Setup new role based on molecule
cd ./roles
molecule init role -r <role> -d docker                                            
```

## Proxy

* `config-files` should be capable of a proxy and non-proxy environment
    * Ansible
        * The `group_vars` for `all` sets `proxy_environment` using e.g. `lookup("env","http_proxy")`
        * The `group_vars` directory is linked to the molecule default scenario for all roles
        * `proxy_environment` is used by all playbooks (`development` and molecule playbooks) as `environment: '{{ proxy_environment }}'`
        * If `lookup` does not find any proxy vars e.g. `http_proxy`, playbook(s) and roles should run either way
        * Proxy affected roles check for the proxy e.g. `{% if environment[0].http_proxy is defined and environment[0].http_proxy | length %}`
    * Molecule
        * All `molecule.yml` files are extended with env for proxies, so that the docker images can be build
        * They are disabled by default due to GitHub Travis CI, so please enable them if a proxy is used

## Links

* [Ansible Doc](https://docs.ansible.com/)
* [Ansible configuration settings](https://docs.ansible.com/ansible/2.8/reference_appendices/config.html)
* [Ansible FAQ](https://docs.ansible.com/ansible/latest/reference_appendices/faq.html)
* [Rapidly Build & Test Ansible Roles with Molecule + Docker](https://www.youtube.com/watch?v=DAnMyBZ8-Qs)
* [Testing Ansible Roles with Molecule Behind a Proxy ](https://renaudmarti.net/posts/molecule-proxy-support/)
