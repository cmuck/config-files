#!/usr/bin/env bash

set -o errexit
set -o errtrace
set -o nounset
set -o pipefail

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa
