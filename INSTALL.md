# Installation

Before starting, ensure to have an up-to-date system
```sh
sudo apt update && sudo apt dist-upgrade
```

## Python

`run-ansible.py` is based on Python 3, pip3 and virtual env, so install these dependencies.

```sh
sudo apt install python3 python3-pip python3-venv
```

## SSH server

A default installation of Ubuntu does not have installed `openssh-server`.
Therefore install `openssh-server` so that the system can be used by Ansible. 

```sh
sudo apt install openssh-server
# Check if openssh-server is running
systemctl status ssh
```

## SSH key

Because Ansible is based on SSH connections to the targets, we have to ensure a SSH key even we are connecting to localhost.

* Please re-use existing SSH key (copy to ~/.ssh) if already created
* or [create a new SSH key](https://help.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key)


## FYI - Virtual environment for Ansible

Ansible changes a lot between releases or deprecates a lot, therefore I use a pinned version of Ansible.

The first run of `run-ansible.py` creates automatically a virtual environment at `.venv` based on the `requirements.txt`.
All further calls to `./run-ansible.py` will us the Ansible version installed into this virtual environment.
