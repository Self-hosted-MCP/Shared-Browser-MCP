#!/bin/sh
# The taskbar's "Show desktop" button: minimize the Chromium window, or bring them back if they are already hidden.
# Chromium also has tiny hidden helper windows; only real windows (wider than 200 px) are touched.
real() { for w in "$@"; do eval "$(xdotool getwindowgeometry --shell "$w" 2>/dev/null)"; [ "${WIDTH:-0}" -gt 200 ] && echo "$w"; done; }
visible=$(real $( { xdotool search --onlyvisible --class chromium; xdotool search --onlyvisible --class XTerm; } 2>/dev/null ))
if [ -n "$visible" ]; then
  for w in $visible; do xdotool windowminimize "$w" 2>/dev/null; done
else
  for w in $(real $( { xdotool search --class chromium; xdotool search --class XTerm; } 2>/dev/null )); do
    xdotool windowmap "$w" windowactivate "$w" 2>/dev/null
  done
fi
