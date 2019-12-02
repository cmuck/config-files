[![Build Status](https://travis-ci.com/cmuck/config-files.svg?branch=master)](https://travis-ci.com/cmuck/config-files)

# config-files

Configuration files for

- Atom
- Git
- VSCode
- Oh-my-zsh

## Installation

```
./setup.sh
```

## Command line options

```
./setup.sh -h
Usage: ./setup.sh options
This script helps to setup config-files for development using
- Atom
- Git (OS dependant)
- VSCode
- Oh-my-zsh
OPTIONS:
   -h      Show usage message
   -k      Git - keep existing files
   -o      Git - overwrite existing files
   -n      Git - user.name
   -e      Git - user.email
```

## Shellcheck

```
docker run --rm -v "$PWD:/mnt" koalaman/shellcheck:stable setup.sh
```

## TODO

- Switch to Ansible
- Install applications git, atom, ... for different OS
