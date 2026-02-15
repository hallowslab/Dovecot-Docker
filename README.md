# Dovecot Docker Test Server

A reusable Dovecot IMAP image designed for testing `imapsync` and mail migrations. Configured entirely at runtime via environment variables and CSV files.

## Features

- **Runtime Provisioning**: No user data is baked into the image. Everything happens at container startup.
- **Virtual Users**: Uses `passwd-file` authentication for virtual users (isolated from host OS).
- **Inbox Population**: Optionally populate inboxes with random, realistic multipart MIME messages.
- **Multi-Variant Support**: Designed to support multiple OS bases and versions (e.g., `debian/trixie`, `alpine/3.19`).

---

## Quick Start (from Docker Hub)

### 1. Create a `users.csv`
Format: `email,password`
```csv
user1@example.com,password1
user2@example.com,password2
```

### 2. Run with Docker

1. Create a network
```bash
docker network create dovecot-net
```
2. Run the source server
```bash
docker run -d --name dovecot-source --network dovecot-net -p 143:143 -v ./users.csv:/users.csv:ro -e POPULATE_INBOX=true -e MIN_MESSAGES=10 -e MAX_MESSAGES=30 hallowtechlab/dovecot-debian:trixie
```
3. Run the destination server
```bash
docker run -d --name dovecot-dest --network dovecot-net -p 2143:143 -v ./users.csv:/users.csv:ro -e POPULATE_INBOX=false -e MIN_MESSAGES=10 -e MAX_MESSAGES=30 hallowtechlab/dovecot-debian:trixie
```
4. Run imapsync docker image on the same network
```bash
docker run --rm --network dovecot-net \
  gilleslamiral/imapsync imapsync \
  --host1 dovecot-source --port1 143 --user1 user1@example.com --password1 password1 \
  --host2 dovecot-dest --port2 143 --user2 user1@example.com --password2 password1 \
  --no-ssl1 --no-ssl2
```

---

## Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `USERS_CSV_PATH` | `/users.csv` | Path to the mounted users CSV file. |
| `POPULATE_INBOX` | `false` | Set to `true` to generate random mail at startup. |
| `MEASURE_SIZE` | `false` | Set to `true` to measure the /mail dir size |
| `MIN_MESSAGES` | `5` | Minimum messages to generate per user. |
| `MAX_MESSAGES` | `20` | Maximum messages to generate per user. |
| `POPULATE_WORKERS` | `Num of CPUs` | Defines the amount of workers that will generate mail messages, needs to be a positive number. |

---

## Imapsync Testing (Docker Compose)

To test synchronization between two instances locally:

### 1. Start Source and Destination
```bash
docker compose up -d
```
- **Source**: Port 1143 (populated with mail)
- **Destination**: Port 2143 (empty)

### 2. Run imapsync
```bash
imapsync --host1 localhost --port1 1143 --user1 user1@example.com --password1 password1 \
         --host2 localhost --port2 2143 --user2 user1@example.com --password2 password1 \
         --no-ssl1 --no-ssl2
```

---

## Development & Multi-Variant Build

The project is structured to share scripts across different OS bases.

### Project Structure
- `build.sh` / `build.ps1`: Automated build scripts.
- `common/`: Shared entrypoint and population scripts.
- `variants/<OS>/<Variant>/`: OS-specific Dockerfiles and Dovecot configurations.

### Building a Variant
Run the build script from the repository root:

**Windows (PowerShell):**
```powershell
.\build.ps1 -Username hallowtechlab -OS debian -Variant trixie -Push
```

**Linux (Bash):**
```bash
./build.sh hallowtechlab debian trixie --push
```
