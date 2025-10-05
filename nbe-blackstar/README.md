# NBE Blackstar Local (MQTT)

Publishes NBE burner/boiler data to Home Assistant via MQTT Discovery (local UDP API).
Based on: https://github.com/e1z0/nbe-blackstar-homeassistant

## Options
- `nbe_host` (required)
- `nbe_serial` (required)
- `nbe_password` (required)
- `mqtt_host` (default `core-mosquitto`)
- `mqtt_port` (default `1883`)
- `mqtt_user` (default `homeassistant`)
- `mqtt_password`
- `mqtt_prefix` (default `homeassistant`)
- `interval` seconds (default `15`)

## Networking
Runs in host network mode. Ensure the burner is reachable from Home Assistant.
