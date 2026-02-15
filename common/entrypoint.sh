#!/bin/bash
set -euo pipefail

USERS_CSV="${USERS_CSV_PATH:-/users.csv}"
POPULATE="${POPULATE_INBOX:-false}"

echo "=== Dovecot Test Server ==="
echo "Users CSV:       ${USERS_CSV}"
echo "Populate Inbox:  ${POPULATE}"

# ── Validate CSV exists ──────────────────────────────────────────────
if [ ! -f "${USERS_CSV}" ]; then
    echo "ERROR: Users CSV file not found at ${USERS_CSV}"
    echo "Mount a CSV file with format: email,password"
    exit 1
fi

# ── Generate passwd-file from CSV ────────────────────────────────────
PASSWD_FILE="/etc/dovecot/users"
> "${PASSWD_FILE}"

USER_COUNT=0
while IFS=',' read -r email password || [ -n "${email}" ]; do
    # Skip empty lines and comments
    email=$(echo "${email}" | tr -d '[:space:]')
    password=$(echo "${password}" | tr -d '[:space:]')
    [ -z "${email}" ] && continue
    [[ "${email}" == \#* ]] && continue

    # Extract domain and local part
    domain="${email#*@}"
    localpart="${email%@*}"

    # Append to passwd-file
    # Format: user:{SCHEME}password:uid:gid::home
    echo "${email}:{PLAIN}${password}:1000:1000::/mail/${domain}/${localpart}" >> "${PASSWD_FILE}"

    # Create Maildir structure
    MAILDIR="/mail/${domain}/${localpart}/Maildir"
    mkdir -p "${MAILDIR}/cur" "${MAILDIR}/new" "${MAILDIR}/tmp"
    chown -R vmail:vmail "/mail/${domain}/${localpart}"

    USER_COUNT=$((USER_COUNT + 1))
    echo "  Created user: ${email}"
done < "${USERS_CSV}"

echo "Generated ${USER_COUNT} user(s)"

# ── Populate inboxes if requested ────────────────────────────────────
if [ "${POPULATE}" = "true" ]; then
    echo "Populating inboxes with random messages..."
    START=$(date +%s)
    runuser -u vmail -- python3 /populate_inbox.py
    END=$(date +%s)
    echo "Population took $((END - START)) seconds"
fi

# ── Measure used size ────────────────────────────────────────────────
if [ "${MEASURE_SIZE}" = "true" ]; then
    echo "/mail - Total size: $(du -sh /mail)"
fi

# ── Start Dovecot in foreground ──────────────────────────────────────
echo "Starting Dovecot..."
exec dovecot -F
