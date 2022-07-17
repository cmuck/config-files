#!/usr/bin/env bash

set -o nounset
set -o errexit
set -o pipefail

realpath=$(realpath "${BASH_SOURCE[0]}")
scripts_dir=$(dirname "${realpath}")
root_dir=$(dirname "${scripts_dir}")
echo "${root_dir}"
cd "${root_dir}"

target_branch="origin/master"
if [[ -v TRAVIS_BRANCH ]] && [[ -n "${TRAVIS_BRANCH}" ]]; then
  target_branch="${TRAVIS_BRANCH}"
  echo "Build for Travis CI: ${target_branch}"
else
  echo "Build locally: ${target_branch}"
  venv="./venv/bin/activate"
  if [[ ! -f "$venv" ]]; then
    echo "Error, venv does not exist..."
    exit 1
  fi
  # shellcheck disable=SC1090
  source "${venv}"
fi

mapfile -t changed_fies < <(git diff --name-only HEAD.."${target_branch}")
roles=( )

echo
echo
echo "###############################################################"
for file in "${changed_fies[@]}"
do
  echo "Changed file: $file"
  role_path=$(echo "${file}" | cut -f1,2 -d'/')
  if [[ $role_path = roles* ]]; then
    roles+=("$role_path")
  fi
done

echo
echo
echo "###############################################################"
echo "All roles: ${roles[*]}"
# shellcheck disable=SC2207
unique_roles=($(echo "${roles[*]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))
echo "Unique roles: ${unique_roles[*]}"
echo "###############################################################"

for role in "${unique_roles[@]}"
do
  echo
  echo
  echo "###############################################################"
  echo "Testing role: $role"
  {
    pushd "$role" >/dev/null
    molecule test
    popd >/dev/null
  }
done