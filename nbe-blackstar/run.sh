#!/usr/bin/env bash
set -euo pipefail

echo "[nbe-blackstar] Starting container initialization..."

OPTS_FILE="/data/options.json"
if [ ! -f "$OPTS_FILE" ]; then
  echo "Options file not found at $OPTS_FILE" >&2
  exit 1
fi

# --- Read user options ---
NBE_HOST=$(jq -r '.nbe_host // ""' "$OPTS_FILE")
NBE_SERIAL=$(jq -r '.nbe_serial // ""' "$OPTS_FILE")
NBE_PASSWORD=$(jq -r '.nbe_password // ""' "$OPTS_FILE")
MQTT_HOST=$(jq -r '.mqtt_host // "core-mosquitto"' "$OPTS_FILE")
MQTT_PORT=$(jq -r '.mqtt_port // 1883' "$OPTS_FILE")
MQTT_USER=$(jq -r '.mqtt_user // "homeassistant"' "$OPTS_FILE")
MQTT_PASSWORD=$(jq -r '.mqtt_password // ""' "$OPTS_FILE")
MQTT_PREFIX=$(jq -r '.mqtt_prefix // "homeassistant"' "$OPTS_FILE")
INTERVAL=$(jq -r '.interval // 15' "$OPTS_FILE")

# --- Validate required fields ---
if [ -z "$NBE_HOST" ] || [ -z "$NBE_SERIAL" ] || [ -z "$NBE_PASSWORD" ]; then
  echo "ERROR: Please configure nbe_host, nbe_serial and nbe_password in add-on options." >&2
  exit 1
fi

# --- Prepare /app/config.json for Python script ---
mkdir -p /app
cat > /app/config.json <<EOF
{
  "nbe_host": "${NBE_HOST}",
  "nbe_serial": "${NBE_SERIAL}",
  "nbe_password": "${NBE_PASSWORD}",
  "mqtt_host": "${MQTT_HOST}",
  "mqtt_port": ${MQTT_PORT},
  "mqtt_user": "${MQTT_USER}",
  "mqtt_password": "${MQTT_PASSWORD}",
  "mqtt_prefix": "${MQTT_PREFIX}",
  "interval": ${INTERVAL}
}
EOF

echo "[nbe-blackstar] Configuration file created."
echo "[nbe-blackstar] Host: ${NBE_HOST}, MQTT: ${MQTT_HOST}:${MQTT_PORT}, Interval: ${INTERVAL}s"

# --- Download main.py if missing ---
if [ ! -f /app/main.py ]; then
  echo "[nbe-blackstar] Downloading upstream main.py ..."
  set +e
  urls=(
    "https://raw.githubusercontent.com/e1z0/nbe-blackstar-homeassistant/master/src/main.py"
    "https://raw.githubusercontent.com/e1z0/nbe-blackstar-homeassistant/main/src/main.py"
    "https://raw.githubusercontent.com/e1z0/nbe-blackstar-homeassistant/master/main.py"
    "https://raw.githubusercontent.com/e1z0/nbe-blackstar-homeassistant/main/main.py"
  )
  ok=0
  for u in "${urls[@]}"; do
    echo "  trying: $u"
    if curl -fsSL "$u" -o /app/main.py; then
      echo "  downloaded from: $u"
      ok=1
      break
    fi
  done
  set -e
  if [ "$ok" -ne 1 ] || [ ! -s /app/main.py ]; then
    echo "ERROR: could not download main.py from upstream" >&2
    exit 1
  fi
fi

# --- Run main.py ---
echo "[nbe-blackstar] Starting NBE service..."
exec python3 /app/main.py
