#!/usr/bin/env bash

# Prints all batteries, their percentage remaining and an emoji corresponding to charge status

# 1 to 3 for left/middle/right mouse button
case "${BLOCK_BUTTON}" in
3) notify-send "🔋 Battery module" "🔋: discharging
🛑: not charging
♻: stagnant charge
🔌: charging
⚡: charged
❗: battery very low!" ;;
esac

if [[ -L /sys/class/power_supply/AC ]]; then
	# i3blocks full_text
	echo 🔌
	# i3blocks full_text
	echo 🔌🔌
	exit 0
fi

# Loop through all attached batteries.
for battery in /sys/class/power_supply/BAT?; do
	# Get its remaining capacity and charge status.
	capacity=$(cat "$battery"/capacity) || break
	status=$(sed "s/Discharging/🔋/;s/Not charging/🛑/;s/Charging/🔌/;s/Unknown/♻️/;s/Full/⚡/" "$battery"/status)

	# If it is discharging and 25% or less, we will add a ❗ as a warning.
	[ "$capacity" -le 25 ] && [ "$status" = "🔋" ] && warn="❗"

	printf "%s%s%s%% " "$status" "$warn" "$capacity"
	unset warn
done | sed s/\ $/\\n/
