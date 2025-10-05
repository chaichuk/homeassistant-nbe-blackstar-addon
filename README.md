# Chaichuk NBE Blackstar Home Assistant Add-on

This repository contains a Home Assistant add-on that wraps the community project
`e1z0/nbe-blackstar-homeassistant` and publishes NBE (Blackstar/RTB/Scotte) data
to Home Assistant via MQTT Discovery, using the local UDP API (no cloud needed).

## How to use
1. In Home Assistant: **Settings → Add-ons → Add-on Store → ⋮ → Repositories → Add**
   Add this URL: `https://github.com/chaichuk/homeassistant-nbe-blackstar-addon`
2. A new section **"Chaichuk NBE Blackstar Add-ons"** will appear at the bottom. Open
   **"NBE Blackstar Local (MQTT)"**, install, configure, and start.

## Notes
- Requires MQTT broker (Mosquitto is fine). Defaults point to `core-mosquitto`.
- Burner must be reachable on the LAN and local UDP/API enabled.
