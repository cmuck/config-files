#!/usr/bin/env bash

set -o nounset
set -o errexit
set -o pipefail

realpath=$(realpath "${BASH_SOURCE[0]}")
scripts_dir=$(dirname "${realpath}")
root_dir=$(dirname "${scripts_dir}")
echo "${root_dir}"
cd "${root_dir}"

ROLES=()

check_github_execution() {
	if [[ -n "${GITHUB_EVENT_NAME:-}" ]]; then
		return 0
	fi
	return 1
}

add_all_roles() {
	mapfile -t all_roles < <(ls roles)
	for role in "${all_roles[@]}"; do
		ROLES+=("roles/${role}")
		echo "Added role ${role}"
	done
}

add_changed_role() {
	local changed_files=("$@")
	for file in "${changed_files[@]}"; do
		echo "Changed file: ${file}"
		role_path=$(echo "${file}" | cut -f1,2 -d'/')
		if [[ "${role_path}" =~ roles/.* ]]; then
			ROLES+=("${role_path}")
			echo "Adding ${role_path}"
		fi
	done
}

handle_uv() {
	local changed_files=("$@")
	if [[ ${changed_files[*]} =~ uv.lock ]]; then
		echo "python requirements changed, testing all roles..."
		add_all_roles
		return 0
	fi
	return 1
}

handle_github() {
	if ! check_github_execution; then
		echo "GitHub execution skipped..."
		return 0
	fi
	echo "GitHub execution..."
	local changed_files=("${@}")
	if [[ "${GITHUB_EVENT_NAME}" == pull_request ]]; then
		echo "Pull request run, testing roles ..."
		if handle_uv "${changed_files[@]}"; then
			return 0
		fi
		add_changed_role "${changed_files[@]}"
	fi
	if [[ "${GITHUB_EVENT_NAME}" =~ schedule|workflow_dispatch ]]; then
		echo "Scheduled run, testing all roles..."
		add_all_roles
	fi
}

handle_local_run() {
	if check_github_execution; then
		echo "Local execution skipped..."
		return 0
	fi
	echo "Local execution..."
	mapfile -t changed_files < <(git diff --name-only HEAD..origin/master)
	if handle_uv "${changed_files[@]}"; then
		return 0
	fi
	add_changed_role "${changed_files[@]}"
}

remove_blacklisted_roles() {
	local blacklist=("roles/apt_add_repo")
	for item in "${blacklist[@]}"; do
		echo "Removing blacklisted role: ${item}"
		ROLES=("${ROLES[@]/$item}")
	done
}

handle_github "${@}"
handle_local_run
remove_blacklisted_roles

echo
echo
echo "###############################################################"
echo "Listing ROLES: ${ROLES[*]}"
# shellcheck disable=SC2207
unique_roles=($(echo "${ROLES[*]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))
echo "Unique ROLES: ${unique_roles[*]}"
echo "###############################################################"

for role in "${unique_roles[@]}"; do
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
