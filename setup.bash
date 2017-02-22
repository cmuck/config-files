#!/bin/bash

set -e
ATOMDIR=~/.atom
EMAIL=
GITCONFIG=.gitconfig
GITDIR=~/.git
NAME=
OS=$(uname -s)
OVERWRITE=

function copyGitConfig
{
    OS=$1
    case $OS in
        Darwin)
            cp "$(pwd)/git/.gitconfig-osx" ~/$GITCONFIG
            ;;
        Linux)
            cp "$(pwd)/git/.gitconfig-linux" ~/$GITCONFIG
            ;;
        MINGW64*)
            cp "$(pwd)/git/.gitconfig-windows" ~/$GITCONFIG
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


# OS independent files
echo "Install independent OS files"

# Atom
if [ ! -d "$ATOMDIR" ]; then
  mkdir $ATOMDIR
fi
ln -sf "$(pwd)/atom/packages.cson" ~/.atom/packages.cson

# Git
if [ ! -d "$GITDIR" ]; then
    mkdir $GITDIR
fi
ln -sf "$(pwd)/git/.gitconfig-common" ~/.gitconfig-common
ln -sf "$(pwd)/git/.git_commit_message.txt" ~/.git_commit_message.txt

# oh-my-zsh
ln -sf "$(pwd)/oh-my-zsh/.zshrc" ~/.zshrc
ln -sf "$(pwd)/oh-my-zsh/.oh-my-zsh" ~/.oh-my-zsh


# OS depdenent dotfiles
echo "Install depdendent OS files for: $OS"

# Chech if git config is present
if [ -f ~/$GITCONFIG ]; then

    # If OVERWRITE is empty, request from user
    if [ -z "$OVERWRITE" ]
    then
        read -r -p "$GITCONFIG already exists, do you want to overwrite it (y/n)?" OVERWRITE
    fi

    case $OVERWRITE in
        "y"|"Y")
            copyGitConfig $OS
            ;;
        "n"|"N")
            echo "$GITCONFIG not overwritten"
            ;;
    esac
else
    echo "$GITCONFIG does not exist, copy new Git config"
    copyGitConfig $OS
fi

if grep "email" ~/$GITCONFIG &> /dev/null ; then
    echo "Git already configured with email"
else
    configureGlobalGitAccount
fi

echo "Finished setup"
