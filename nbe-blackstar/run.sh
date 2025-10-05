#!/usr/bin/env bash
set -euo pipefail

OPTS_FILE="/data/options.json"
if [ ! -f "$OPTS_FILE" ]; then
  echo "Options file not found at $OPTS_FILE" >&2
  exit 1
fi

NBE_HOST=$(jq -r '.nbe_host // ""' "$OPTS_FILE")
NBE_SERIAL=$(jq -r '.nbe_serial // ""' "$OPTS_FILE")
NBE_PASSWORD=$(jq -r '.nbe_password // ""' "$OPTS_FILE")
MQTT_HOST=$(jq -r '.mqtt_host // "core-mosquitto"' "$OPTS_FILE")
MQTT_PORT=$(jq -r '.mqtt_port // 1883' "$OPTS_FILE")
MQTT_USER=$(jq -r '.mqtt_user // "homeassistant"' "$OPTS_FILE")
MQTT_PASSWORD=$(jq -r '.mqtt_password // ""' "$OPTS_FILE")
MQTT_PREFIX=$(jq -r '.mqtt_prefix // "homeassistant"' "$OPTS_FILE")
INTERVAL=$(jq -r '.interval // 15' "$OPTS_FILE")

if [ -z "$NBE_HOST" ] || [ -z "$NBE_SERIAL" ] || [ -z "$NBE_PASSWORD" ]; then
  echo "Please configure nbe_host, nbe_serial and nbe_password in add-on options." >&2
  exit 1
fi

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

echo "[nbe-blackstar] Starting with MQTT host ${MQTT_HOST}:${MQTT_PORT}"
exec python3 /app/main.py
