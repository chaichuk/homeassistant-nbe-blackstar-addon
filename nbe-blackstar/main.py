#!/usr/bin/env python3
import json
import os
import time
import socket
import sys
from datetime import datetime

# MQTT
import paho.mqtt.client as mqtt

# NBE local UDP API via pyduro
from pyduro.actions import get as nbe_get

CONFIG_PATH = os.environ.get("NBE_CONFIG", "/app/config.json")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def discovery_payload_sensor(name, uniq, state_topic, attr_topic, device):
    return {
        "name": name,
        "unique_id": uniq,
        "state_topic": state_topic,
        "json_attributes_topic": attr_topic,
        "icon": "mdi:fire",
        "device": device,
    }

def main():
    cfg = load_config()

    nbe_host     = cfg["nbe_host"]
    nbe_serial   = str(cfg["nbe_serial"])
    nbe_password = str(cfg["nbe_password"])
    mqtt_host    = cfg.get("mqtt_host", "core-mosquitto")
    mqtt_port    = int(cfg.get("mqtt_port", 1883))
    mqtt_user    = cfg.get("mqtt_user") or None
    mqtt_pass    = cfg.get("mqtt_password") or None
    mqtt_prefix  = cfg.get("mqtt_prefix", "homeassistant")
    interval     = int(cfg.get("interval", 15))

    # MQTT topics
    base_disco = f"{mqtt_prefix}"
    dev_id = f"nbe_{nbe_serial}"
    node_id = dev_id
    status_obj = "status"
    comp = "sensor"

    # Discovery topics (one sensor with attributes dump)
    stat_topic = f"{base_disco}/{comp}/{node_id}/{status_obj}/state"
    attr_topic = f"{base_disco}/{comp}/{node_id}/{status_obj}/attributes"
    disco_topic = f"{base_disco}/{comp}/{node_id}/{status_obj}/config"

    # Device info for HA
    device = {
        "identifiers": [dev_id],
        "manufacturer": "NBE",
        "model": "NBE burner/boiler",
        "name": f"NBE {nbe_serial}",
    }

    client = mqtt.Client(client_id=f"{dev_id}-{socket.gethostname()}")
    if mqtt_user:
        client.username_pw_set(mqtt_user, mqtt_pass)

    # Basic LWT so HA бачить offline
    lwt_topic = f"{base_disco}/{comp}/{node_id}/{status_obj}/availability"
    client.will_set(lwt_topic, payload=json.dumps({"available": False}), retain=True)

    client.connect(mqtt_host, mqtt_port, keepalive=60)

    # Publish discovery (retain)
    disco_payload = discovery_payload_sensor(
        name=f"NBE {nbe_serial} status",
        uniq=f"{dev_id}_status",
        state_topic=stat_topic,
        attr_topic=attr_topic,
        device=device,
    )
    client.publish(disco_topic, json.dumps(disco_payload), retain=True)
    client.publish(lwt_topic, json.dumps({"available": True}), retain=True)

    client.loop_start()

    def publish_snapshot(ok: bool, snapshot: dict | None, err: str | None):
        state = "online" if ok else "offline"
        client.publish(stat_topic, state, retain=False)

        payload = {
            "ok": ok,
            "error": err,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "host": nbe_host,
            "serial": nbe_serial,
            "operating": snapshot.get("operating") if snapshot else None,
            "settings": snapshot.get("settings") if snapshot else None,
        }
        client.publish(attr_topic, json.dumps(payload), retain=False)

    while True:
        try:
            # read operating + settings via pyduro (blocking in thread ok)
            op = nbe_get.run(nbe_host, nbe_serial, nbe_password, "operating", "")
            st = nbe_get.run(nbe_host, nbe_serial, nbe_password, "settings", "")

            op_pl = op.get("payload", {}) if isinstance(op, dict) else {}
            st_pl = st.get("payload", {}) if isinstance(st, dict) else {}

            publish_snapshot(True, {"operating": op_pl, "settings": st_pl}, None)

        except Exception as e:
            publish_snapshot(False, None, str(e))

        time.sleep(interval)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
