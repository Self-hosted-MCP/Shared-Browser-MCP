#!/bin/bash
set -e
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99   # a restart (not a fresh start) leaves these behind and blocks the screen
# Xtigervnc is the screen and the VNC server in one, and lets the viewer resize the screen to its own size.
Xtigervnc :99 -geometry ${SCREEN:-1280x800} -depth 24 -SecurityTypes None -localhost -AlwaysShared \
  -rfbport 5900 -nolisten tcp -AcceptSetDesktopSize=1 >/dev/null 2>&1 &
for i in $(seq 1 50); do [ -e /tmp/.X11-unix/X99 ] && break; sleep 0.2; done
openbox >/dev/null 2>&1 &   # keeps the one Chromium window filling the screen as it resizes
# A small taskbar at the bottom: click a window there to bring it forward (Chromium).
mkdir -p /home/browser/.config/tint2
cat > /home/browser/.config/tint2/tint2rc <<'RC'
rounded = 0
border_width = 0
background_color = #0d0f14 100
border_color = #0d0f14 100
rounded = 6
border_width = 0
background_color = #1d2230 100
border_color = #1d2230 100
rounded = 6
border_width = 0
background_color = #33415f 100
border_color = #33415f 100
panel_monitor = all
panel_position = bottom center horizontal
panel_size = 100% 34
panel_margin = 0 0
panel_padding = 6 4 6
panel_items = ETC
panel_background_id = 1
panel_layer = top
wm_menu = 0
strut_policy = follow_size
taskbar_mode = single_desktop
taskbar_name = 0
taskbar_padding = 0 0 6
taskbar_background_id = 0
task_text = 1
task_icon = 0
task_centered = 1
task_maximum_size = 200 30
task_padding = 10 5 10
task_background_id = 2
task_active_background_id = 3
task_iconified_background_id = 2
task_font_color = #d7dae0 100
task_active_font_color = #ffffff 100
task_iconified_font_color = #8a90a0 100
task_font = sans 10
mouse_left = toggle_iconify
mouse_middle = none
mouse_right = none
mouse_scroll_up = none
mouse_scroll_down = none
time1_format = %H:%M
time1_font = sans 10
clock_font_color = #d7dae0 100
clock_padding = 10 0
clock_background_id = 0
execp = new
execp_command = echo Show desktop
execp_interval = 0
execp_has_icon = 0
execp_continuous = 0
execp_markup = 0
execp_lclick_command = /usr/local/bin/show-desktop
execp_font = sans 10
execp_font_color = #d7dae0 100
execp_padding = 12 5
execp_background_id = 2
execp_centered = 1
RC
tint2 -c /home/browser/.config/tint2/tint2rc >/dev/null 2>&1 &
websockify --web /usr/share/novnc 6080 localhost:5900 &
# Chromium listens on localhost only; socat exposes it on 9223 for the MCP container alone (its fixed wall address)
socat TCP-LISTEN:9223,fork,reuseaddr,bind=0.0.0.0,range=10.88.250.10/32 TCP:127.0.0.1:9222 &
rm -f /home/browser/profile/Singleton*   # a restart leaves stale locks behind
# No browsing history is kept: it is wiped on every start. Saved logins (cookies) stay.
P=/home/browser/profile/Default
rm -rf "$P/History" "$P/History-journal" "$P/Visited Links" "$P/Top Sites" "$P/Top Sites-journal" "$P/Favicons" \
  "$P/Favicons-journal" "$P/Shortcuts" "$P/Shortcuts-journal" "$P/Network Action Predictor" "$P/Cache" "$P/Code Cache" \
  "$P/GPUCache" "$P/Session Storage" "$P/Sessions" "$P/DownloadMetadata" "$P/Web Data" "$P/Web Data-journal" 2>/dev/null
# Chromium's own sandbox is ON. CHROME_NO_SANDBOX=1 turns it off, only for a host that refuses user namespaces.
SANDBOX=""; [ "${CHROME_NO_SANDBOX:-0}" = 1 ] && SANDBOX="--no-sandbox"
# Theme from Settings (dark by default): dark browser frame, sites that have a dark style use it, the rest are darkened.
DARK=""; [ "$(cat /state/browser-theme 2>/dev/null || echo dark)" != light ] && DARK="--force-dark-mode --enable-features=WebContentsForceDark"
exec chromium $SANDBOX $DARK --disable-dev-shm-usage --no-first-run --no-default-browser-check \
  --remote-debugging-port=9222 --user-data-dir=/home/browser/profile \
  --start-maximized --disable-gpu \
  --disable-features=Translate,MediaRouter,OptimizationHints --no-pings --disable-breakpad --password-store=basic \
  --proxy-server=http://egress:3128 --proxy-bypass-list="front;<-loopback>" \
  --disable-quic --force-webrtc-ip-handling-policy=disable_non_proxied_udp \
  --lang=en-US --accept-lang=en-US,en \
  "http://front:8088/"
