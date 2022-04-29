#!/usr/bin/env bash

# Prints CPU usage with a warning (yellow color) and critical (red color) threshold

THRESHOLD_WARNING=50
THRESHOLD_CRITICAL=80

ERROR_MESSAGE="i3blocks default module missing"

# 1 to 3 for left/middle/right mouse button
case "${BLOCK_BUTTON}" in
  1) notify-send "🖥CPU hogs" "$(ps axch -o cmd:15,%cpu --sort=-%cpu | head)\\n(100% per core)" ;;
  2) setsid "$TERMINAL" -e htop & ;;
  3) notify-send "CPU status" "Shows CPU details
- Left click to show intensive processes
- Middle click to open htop
- Right click none" ;;
esac

I3_BLOCKS_DEFAULT="/usr/share/i3blocks/cpu_usage"

if [[ ! -e "${I3_BLOCKS_DEFAULT}" ]]; then
  # i3blocks full_text
  echo "${ERROR_MESSAGE}"
  # i3blocks full_text
  echo "${ERROR_MESSAGE}"
  exit 33
fi

"${I3_BLOCKS_DEFAULT}" -w "${THRESHOLD_WARNING}" -c "${THRESHOLD_CRITICAL}"
