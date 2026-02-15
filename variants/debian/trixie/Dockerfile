FROM debian:trixie-slim

LABEL maintainer="HallowsTechLab"
LABEL description="Dovecot IMAP test server with virtual users for imapsync testing"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    dovecot-imapd \
    python3 \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Create vmail user for virtual mailbox ownership
RUN groupadd -g 1000 vmail && \
    useradd -u 1000 -g vmail -d /mail -s /usr/sbin/nologin vmail && \
    mkdir -p /mail && chown vmail:vmail /mail

# Copy Dovecot configuration (v2.4+ format, variant-specific)
COPY variants/debian/trixie/dovecot/dovecot.conf /etc/dovecot/dovecot.conf

# Copy runtime scripts
COPY common/entrypoint.sh /entrypoint.sh
COPY common/populate_inbox.py /populate_inbox.py
RUN chmod +x /entrypoint.sh

# Runtime environment defaults
ENV USERS_CSV_PATH=/users.csv
ENV POPULATE_INBOX=false
ENV MEASURE_SIZE=false
ENV MIN_MESSAGES=5
ENV MAX_MESSAGES=20

EXPOSE 143

VOLUME /mail

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD nc -z localhost 143 || exit 1

ENTRYPOINT ["/entrypoint.sh"]
