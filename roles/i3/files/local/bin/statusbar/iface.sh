#!/usr/bin/env bash

# Prints network interface details

INTERFACE=$(ip route | awk '/^default/ { print $5 }' | sort | head -1)
INTERFACE_DOWN_MESSAGE="IPv4: Down"

INET=$(ip addr show "${INTERFACE}" | awk '/^.*inet.*\/24/ {print substr($2, 1, length($2)-3)}')
INET6=$(ip addr show "${INTERFACE}" | awk '/^.*inet6.*\/64/ {print substr($2, 1, length($2)-3)}')

# 1 to 3 for left/middle/right mouse button
case "${BLOCK_BUTTON}" in
	#1) notify-send "Network interfaces" "Interface (default): ${INTERFACE}\nIPv4: ${INET}\nIPv6: ${INET6}" ;;
	1) notify-send "Network interfaces" "$(ip addr show)" ;;
	2) echo -n "${INET:-$INTERFACE_DOWN_MESSAGE}" | xclip -q -se c ;;
	3) notify-send "Network interface status" "Shows network interface details
- Click to show network interface details
- Middle click to copy IPv4 adress
- Right click none" ;;
esac

if [[ -z ${INTERFACE} ]]; then
  echo "${INTERFACE_DOWN_MESSAGE}"
  exit 33;
fi

# i3blocks full_text
echo "IPv4 ${INET}"
# i3blocks full_text
echo "IPv4 ${INET}"
