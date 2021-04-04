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
mapfile -t changed_fies < <(git diff --name-only HEAD.."${target_branch}")
roles=( )

echo
echo
echo "###############################################################"
for file in "${changed_fies[@]}"; do
  echo "Changed file: ${file}"
  role_path=$(echo "${file}" | cut -f1,2 -d'/')
  if [[ "${role_path}" =~ roles/.* ]]; then
    roles+=("${role_path}")
    echo "Adding ${role_path}"
  fi
  if [[ "${file}" == requirements.txt ]]; then
    echo "requirements.txt changed, testing all roles..."
    all_roles=( $( ls roles ) )
    for role in "${all_roles[@]}"
    do
      roles+=("roles/${role}")
    done
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
  echo "Testing role: ${role}"
  {
    pushd "${role}" >/dev/null
    molecule test
    popd >/dev/null
  }
done