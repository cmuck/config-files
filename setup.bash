#!/bin/bash

set -o errexit
set -o errtrace
set -o nounset
set -o pipefail

ATOM_DIR=~/.atom
ATOM_PROGRAM=atom
EMAIL=
GIT_CONFIG=.gitconfig
GIT_DIR=~/.git
GIT_PROGRAM=git
NAME=
OS=$(uname -s)
OVERWRITE=
SCRIPT=$0
VSCODE_PROGRAM=code
ZSH_PROGRAM=zsh

copyGitConfig ()
{
    case $OS in
        Darwin)
            cp "$(pwd)/git/.gitconfig-osx" ~/$GIT_CONFIG
            ;;
        Linux)
            cp "$(pwd)/git/.gitconfig-linux" ~/$GIT_CONFIG
            ;;
        MINGW64*)
            cp "$(pwd)/git/.gitconfig-windows" ~/$GIT_CONFIG
            ;;
        *)
            echo "Unsupported operating system. Skipping platform-specific dotfiles."
            ;;
    esac

    echo " git config copied"
}

configureGitUserAndMail ()
{
    if grep "email" ~/$GIT_CONFIG &> /dev/null ; then
        echo "Git already configured with email"
    else
        # If NAME is empty, request from user
        if [ -z "$NAME" ]
        then
            read -r -p "Enter your name and press [ENTER]: " NAME
        fi

        # If EMAIL is empty, request from user
        if [ -z "$EMAIL" ]
        then
            read -r -p "Enter your email and press [ENTER]: " EMAIL
        fi

        # Set global git config
        git config --global user.name "$NAME"
        git config --global user.email "$EMAIL"

        echo " git user.name and user.email configured"
    fi
}

installAtom ()
{
    if [ ! -d "$ATOM_DIR" ]; then
        mkdir $ATOM_DIR
    fi
    ln -sf "$(pwd)/atom/packages.cson" $ATOM_DIR/packages.cson

    echo " $ATOM_PROGRAM finished"
}

installGitIndependentOS ()
{
    if [ ! -d "$GIT_DIR" ]; then
        mkdir $GIT_DIR
    fi
    ln -sf "$(pwd)/git/.gitconfig-common" ~/.gitconfig-common

    echo " $GIT_PROGRAM common finished"
}

installGitDependentOS ()
{
    # Chech if git config is present
    if [ -f ~/$GIT_CONFIG ]; then
        # If OVERWRITE is empty, request from user
        if [ -z "$OVERWRITE" ]
        then
            while read -r -p "$GIT_CONFIG already exists, do you want to overwrite it (y/n)?" OVERWRITE; do
                case "$OVERWRITE" in
                    [Yy]*)
                        echo "$GIT_CONFIG will be overwritten"
                        break
                    ;;
                    [Nn]*)
                        break
                    ;;
                    *)
                        echo "Invalid option" >&2
                    ;;
                esac
            done
        fi

        case $OVERWRITE in
            [Yy]*)
                copyGitConfig
            ;;
            [YNn*)
                echo "$GIT_CONFIG will be kept"
            ;;
        esac
    else
        echo "$GIT_CONFIG does not exist, copy new Git config"
        copyGitConfig
    fi

    echo " $GIT_PROGRAM finished"
}

installVSCode ()
{
    for extension in $(cat vscode/extensions.txt)
    do
        echo " -- Installing $extension"
        code --install-extension $extension > /dev/null
    done

    echo " $VSCODE_PROGRAM finished"
}

installZSH ()
{
    if [ -f ~/.zshrc ]; then
        rm ~/.zshrc
    fi

    ln -sf "$(pwd)/oh-my-zsh/.zshrc" ~/.zshrc

    echo " $ZSH_PROGRAM finished"
}

usage ()
{

cat << EOF
Usage: $0 options

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
EOF
}

while getopts "kohn:e:" opt; do
  case ${opt} in
    o )
        # Will overwrite the git config
        OVERWRITE=Y
      ;;
    k )
        # Will overwrite the git config
        OVERWRITE=N
      ;;
    n )
        # Git user name
        NAME=$OPTARG
      ;;
    e )
        # Git user email
        EMAIL=$OPTARG
      ;;
    h)
        usage
        exit 0
      ;;
    \? )
        # Wrong option
        usage
        exit 1
      ;;
    : )
        # Right option with invalid argument
        echo "Invalid option: $OPTARG requires an argument" 1>&2
        usage
        exit 1
    ;;
  esac
done

echo "Check program installation..."

ATOM_INSTALLED=$(which $ATOM_PROGRAM) || true
GIT_INSTALLED=$(which $GIT_PROGRAM) || true
VSCODE_INSTALLED=$(which $VSCODE_PROGRAM) || true
ZSH_INSTALLED=$(which $ZSH_PROGRAM) || true

echo "$ATOM_PROGRAM: $ATOM_INSTALLED"
echo "$GIT_PROGRAM: $GIT_INSTALLED"
echo "$VSCODE_PROGRAM: $VSCODE_INSTALLED"
echo "$ZSH_PROGRAM: $ZSH_INSTALLED"


echo "$ATOM_PROGRAM"
if [ -n "$ATOM_INSTALLED" ]; then
    installAtom
else
    echo " $ATOM_PROGRAM is not installed, skipping setup."
fi

echo "$VSCODE_PROGRAM"
if [ -n "$VSCODE_INSTALLED" ]; then
    installVSCode
else
    echo " $VSCODE_PROGRAM is not installed, skipping setup."
fi

echo "$ZSH_PROGRAM"
if [ -n "$ZSH_INSTALLED" ]; then
    installZSH
else
    echo " $ZSH_PROGRAM is not installed, skipping setup."
fi

echo "$GIT_PROGRAM"
if [ -n "$GIT_INSTALLED" ]; then
    installGitIndependentOS
    installGitDependentOS
    configureGitUserAndMail
else
    echo " $GIT_PROGRAM is not installed, skipping setup."
fi