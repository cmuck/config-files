#!/bin/bash

set -euf -o pipefail

ATOM_DIR=~/.atom
ATOM_INSTALLED=
ATOM_PROGRAM=atom
EMAIL=
GIT_CONFIG=.gitconfig
GIT_DIR=~/.git
GIT_INSTALLED=
GIT_PROGRAM=git
NAME=
OS=$(uname -s)
OVERWRITE=
VSCODE_INSTALLED=
VSCODE_PROGRAM=code
ZSH_INSTALLED=
ZSH_PROGRAM=zsh

echo "================================================="
echo "Check programs"

ATOM_INSTALLED=$(which $ATOM_PROGRAM) || true
GIT_INSTALLED=$(which $GIT_PROGRAM) || true
VSCODE_INSTALLED=$(which $VSCODE_PROGRAM) || true
ZSH_INSTALLED=$(which $ZSH_PROGRAM) || true

echo "Finished."


function copyGitConfig
{
    OS=$1
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
    esac
}

function configureGlobalGitAccount
{
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
}

function installAtom
{
    if [ ! -d "$ATOM_DIR" ]; then
        mkdir $ATOM_DIR
    fi
    ln -sf "$(pwd)/atom/packages.cson" $ATOM_DIR/packages.cson
}

function installGitIndependentOS
{    
    if [ ! -d "$GIT_DIR" ]; then
        mkdir $GIT_DIR
    fi
    ln -sf "$(pwd)/git/.gitconfig-common" ~/.gitconfig-common
    ln -sf "$(pwd)/git/.git_commit_message.txt" ~/.git_commit_message.txt
}

function installGitDependentOS
{
    # Chech if git config is present
    if [ -f ~/$GIT_CONFIG ]; then

        # If OVERWRITE is empty, request from user
        if [ -z "$OVERWRITE" ]
        then
            read -r -p "$GIT_CONFIG already exists, do you want to overwrite it (y/n)?" OVERWRITE
        fi

        case $OVERWRITE in
            "y"|"Y")
                copyGitConfig $OS
                ;;
            "n"|"N")
                echo "$GIT_CONFIG not overwritten"
                ;;
        esac
    else
        echo "$GIT_CONFIG does not exist, copy new Git config"
        copyGitConfig $OS
    fi

    if grep "email" ~/$GIT_CONFIG &> /dev/null ; then
        echo "Git already configured with email"
    else
        configureGlobalGitAccount
    fi
}

function installVSCode
{
    for extension in $(cat vscode/extensions.txt)
    do
        echo " -- Installing $extension"
        code --install-extension $extension > /dev/null
    done
}

function installZSH
{
    if [ -f ~/.zshrc ]; then
        rm ~/.zshrc
    fi

    ln -sf "$(pwd)/oh-my-zsh/.zshrc" ~/.zshrc
    ln -sf "$(pwd)/oh-my-zsh/.oh-my-zsh" ~/.oh-my-zsh
}

while getopts ":yn:e:" opt; do
  case ${opt} in
    y )
        # Will overwrite the git config
        OVERWRITE=Y
      ;;
    n )
        # Git user name
        NAME=$OPTARG
      ;;
    e )
        # Git user email
        EMAIL=$OPTARG
      ;;
    \? )
        # Wrong option
        echo "Usage: cmd [-n NAME] [-e EMAIL]"
        exit -1
      ;;
    : )
        # Right option with invalid argument
        echo "Invalid option: $OPTARG requires an argument" 1>&2
        exit -1
    ;;
  esac
done

echo
echo "================================================="
echo "Install independent OS files"
echo
echo "-------------------------------------------------"
echo "Atom"

if [ -n "$ATOM_INSTALLED" ]; then
    echo "Setup..."
    installAtom
    echo "Finished."
else
    echo "Atom is not installed, skipping setup."
fi

echo
echo "-------------------------------------------------"
echo "VSCode"

if [ -n "$VSCODE_INSTALLED" ]; then
    echo "Setup..."
    installVSCode
    echo "Finished."
else
    echo "VSCode is not installed, skipping setup."
fi

echo
echo "-------------------------------------------------"
echo "Git"

if [ -n "$GIT_INSTALLED" ]; then
    echo "Setup..."
    installGitIndependentOS
    echo "Finished."
else
    echo "Git is not installed, skipping setup."
fi


echo
echo "-------------------------------------------------"
echo "oh-my-zsh"
if [ -n "$ZSH_INSTALLED" ]; then
    echo "Setup..."
    installZSH
    echo "Finished."
else
    echo "Git is not installed, skipping setup."
fi

echo
echo "================================================="
echo "Install depdendent OS files for: $OS"
echo "================================================="
echo
echo "-------------------------------------------------"
echo "Git"
if [ -n "$GIT_INSTALLED" ]; then
    echo "Setup..."
    installGitDependentOS
    echo "Finished."
else
    echo "Git is not installed, skipping setup."
fi
