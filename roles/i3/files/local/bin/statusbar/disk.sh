#!/usr/bin/env bash

# Prints disk details e.g. used, free, total, percent used/free, ...
# with a warning (yellow color) and critical (red color) threshold

THRESHOLD_WARNING=60
THRESHOLD_CRITICAL=80

# 1 to 3 for left/middle/right mouse button
case "${BLOCK_BUTTON}" in
	1) notify-send "💽Disk space" "$(df -h --output=target,used,size)" ;;
	3) notify-send "Disk status" "Shows disk space [used]/[total] [% used]
- Left click to show all disk info
- Middle none
- Right click none" ;;
esac

directory="${BLOCK_INSTANCE:-/}"
df_dump="$( df -h -P -l "${directory}" | tail -1 )"

total="$( echo "${df_dump}" | awk '{ print $2}' | grep -o '[.0-9]*' || true )"
used="$( echo "${df_dump}"  | awk '{ print $3}' | grep -o '[.0-9]*' || true )"
free="$( echo "${df_dump}"  | awk '{ print $4}' | grep -o '[.0-9]*' || true )"

percent_used="$( echo "${df_dump}" | awk '{ print $5}' | sed 's/%//g' )"
percent_free="$(( 100 - percent_used ))"

#echo "total: $total"
#echo "used: $used"
#echo "free: $free"
#echo "pused: $pused"
#echo "pfree: $pfree"

# i3blocks full_text
echo "${used}G/${total}G ${percent_used}%"
# i3blocks short_text
echo "${used}G/${total}G ${percent_used}%"

if [[ "${percent_used}" -ge "${THRESHOLD_CRITICAL}" ]]; then
    echo "#FF0000"
    exit 33
elif [[ "${percent_used}" -ge "${THRESHOLD_WARNING}" ]]; then
    echo "#FFFC00"
fi
