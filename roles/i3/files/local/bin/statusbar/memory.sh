#!/usr/bin/env bash

# Prints memory details e.g. used, free, total, percent used/free, ...
# with a warning (yellow color) and critical (red color) threshold

THRESHOLD_WARNING=50
THRESHOLD_CRITICAL=80

# 1 to 3 for left/middle/right mouse button
case "${BLOCK_BUTTON}" in
  1) notify-send "🧠 Memory hogs" "$(ps axch -o cmd:15,%mem --sort=-%mem | head)" ;;
  2) setsid "${TERMINAL}" -e htop &;;
  3) notify-send "Memory status" "Shows memory [used]/[total] [% used]
- Left click to show memory hogs
- Middle click to open htop
- Right click none" ;;
esac

free_dump="$(free | grep 'Mem' || true)"

total="$(echo "${free_dump}" | awk '{printf("%.2f\n", $2/(1024*1024))}')"
free="$(echo "${free_dump}" | awk '{printf("%.2f\n", $7/(1024*1024))}')"
used="$(awk -v total="${total}" -v free="${free}" 'BEGIN {printf("%.2f\n", total-free)}')"
percent_used="$(awk -v total="${total}" -v used="${used}" 'BEGIN {printf("%0.f\n", 100*used/total)}')"
percent_free="$(awk -v total="${total}" -v free="${free}" 'BEGIN {printf("%0.f\n", 100*free/total)}')"

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
