#!/bin/bash

set -e
GITCONFIG=.gitconfig
OS=$(uname -s)

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
    read -r -p "Enter your name and press [ENTER]: " NAME
    read -r -p "Enter your email and press [ENTER]: " EMAIL
    git config --global user.name "$NAME"
    git config --global user.email "$EMAIL"
}


# OS independent files
echo "Install independent OS files"

ln -sf "$(pwd)/atom/packages.cson" ~/.atom/packages.cson
ln -sf "$(pwd)/git/.gitconfig-common" ~/.gitconfig-common


# OS depdenent dotfiles
echo "Install depdendent OS files for: $OS"


if [ -f ~/$GITCONFIG ]; then
    read -r -p "$GITCONFIG already exists, do you want to overwrite it (y/n)?" OVERWRITE

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
