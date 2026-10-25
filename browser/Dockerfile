FROM debian:bookworm-slim@sha256:7ff6ba31527b9e336162fa061746c366c4b2032f4d2cff2078bea43f78efe3f8
ENV DEBIAN_FRONTEND=noninteractive DISPLAY=:99 TZ=UTC
RUN apt-get update && apt-get install -y --no-install-recommends \
      chromium tigervnc-standalone-server openbox novnc websockify socat fonts-liberation fonts-noto-color-emoji \
      ca-certificates procps tzdata xdotool x11-utils \
      tint2 fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 browser
COPY policy.json /etc/chromium/policies/managed/policy.json
COPY start.sh /start.sh
COPY show-desktop.sh /usr/local/bin/show-desktop
RUN chmod +x /start.sh /usr/local/bin/show-desktop
RUN mkdir -p /home/browser/profile /home/browser/work /files/downloads /state && chown -R browser:browser /home/browser /files /state
USER browser
WORKDIR /home/browser
EXPOSE 6080 9223
CMD ["/start.sh"]
