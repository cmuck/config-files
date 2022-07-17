#!/bin/bash

set -e

# OS independent files
echo "Install independent files"

ln -sf "$(pwd)/atom/packages.cson" ~/.atom/packages.cson
ln -sf "$(pwd)/git/.gitconfig-common" ~/.gitconfig-common

# OS depdenent dotfiles
OS=$(uname -s)
GITCONFIG=.gitconfig

echo "Install depdendent files for OS: $OS"
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

if [ -f ~/$GITCONFIG ]; then
  if grep "email" ~/$GITCONFIG; then
    echo "Git already configured with email"
  else
    read -r -p "Enter your name and press [ENTER]: " NAME
    read -r -p "Enter your email and press [ENTER]: " EMAIL
    git config --global user.name "$NAME"
    git config --global user.email "$EMAIL"
  fi
else
   echo "File $GITCONFIG does not exist"
fi

echo "Finished setup"
