# Installation

Before starting, ensure to have an up-to-date system

```sh
sudo apt update && sudo apt dist-upgrade
```

The script execution is based on Python 3 and [poetry](https://python-poetry.org/), so continue to install these
dependencies.

```sh
sudo apt install python3 python3-pip
pip install --user poetry
poetry install
```

Ansible is used to configure the system and requires a SSH for the connection.

A default installation of Ubuntu does not have installed `openssh-server`. Therefore install `openssh-server` so that
the system can be used by Ansible.

```sh
sudo apt install openssh-server
# Check if openssh-server is running
systemctl status ssh
```

Please re-use your existing SSH key (copy to ~/.ssh) if already created or
[create a new SSH key](https://help.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key)
