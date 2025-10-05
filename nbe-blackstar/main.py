#!/usr/bin/env python3
import json, os, time, socket, sys
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

# локальний UDP API
from pyduro.actions import get as nbe_get

# cloud (HTTPS) через Basic Auth
import requests
from requests.auth import HTTPBasicAuth

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
        "availability_topic": f"{state_topic}/availability",
        "device": device,
    }

def read_local(host, serial, pin):
    op = nbe_get.run(host, serial, pin, "operating", "")
    st = nbe_get.run(host, serial, pin, "settings", "")
    op_pl = op.get("payload", {}) if isinstance(op, dict) else {}
    st_pl = st.get("payload", {}) if isinstance(st, dict) else {}
    return {"operating": op_pl, "settings": st_pl}

def read_cloud(serial, username, password):
    url = f"https://stokercloud.dk/devices/{serial}/json"
    resp = requests.get(url, auth=HTTPBasicAuth(username, password), timeout=20)
    if resp.status_code != 200:
        raise RuntimeError(f"cloud http {resp.status_code}")
    data = resp.json()
    # У деяких акаунтів StokerCloud поле payload уже “плоске”
    op = data.get("operating", {})
    st = data.get("settings", {})
    # fallback: частина пристроїв має вкладений вигляд
    if not op and "payload" in data and isinstance(data["payload"], dict):
        op = data["payload"].get("operating", {})
        st = data["payload"].get("settings", {})
    return {"operating": op, "settings": st}

def main():
    cfg = load_config()

    mode         = cfg.get("mode", "local").strip().lower()
    nbe_host     = cfg.get("nbe_host", "")
    nbe_serial   = str(cfg["nbe_serial"])
    nbe_password = str(cfg.get("nbe_password", ""))
    cloud_user   = cfg.get("cloud_username") or ""
    cloud_pass   = cfg.get("cloud_password") or ""

    mqtt_host    = cfg.get("mqtt_host", "core-mosquitto")
    mqtt_port    = int(cfg.get("mqtt_port", 1883))
    mqtt_user    = cfg.get("mqtt_user") or None
    mqtt_pass    = cfg.get("mqtt_password") or None
    mqtt_prefix  = cfg.get("mqtt_prefix", "homeassistant")
    interval     = int(cfg.get("interval", 15))

    # MQTT topics
    dev_id  = f"nbe_{nbe_serial}"
    node_id = dev_id
    comp    = "sensor"
    obj     = "status"

    stat_topic = f"{mqtt_prefix}/{comp}/{node_id}/{obj}/state"
    attr_topic = f"{mqtt_prefix}/{comp}/{node_id}/{obj}/attributes"
    disco_topic = f"{mqtt_prefix}/{comp}/{node_id}/{obj}/config"
    avail_topic = f"{stat_topic}/availability"

    device = {
        "identifiers": [dev_id],
        "manufacturer": "NBE",
        "model": f"NBE ({mode})",
        "name": f"NBE {nbe_serial}",
    }

    client = mqtt.Client(client_id=f"{dev_id}-{socket.gethostname()}", protocol=mqtt.MQTTv311)
    if mqtt_user:
        client.username_pw_set(mqtt_user, mqtt_pass)
    client.will_set(avail_topic, payload=json.dumps({"available": False}), retain=True)

    client.connect(mqtt_host, mqtt_port, keepalive=60)

    # discovery
    disco_payload = discovery_payload_sensor(
        name=f"NBE {nbe_serial} status",
        uniq=f"{dev_id}_status",
        state_topic=stat_topic,
        attr_topic=attr_topic,
        device=device,
    )
    client.publish(disco_topic, json.dumps(disco_payload), retain=True)
    client.publish(avail_topic, json.dumps({"available": True}), retain=True)
    client.loop_start()

    def publish(ok: bool, snapshot: dict | None, err: str | None):
        client.publish(stat_topic, "online" if ok else "offline", retain=False)
        payload = {
            "ok": ok,
            "error": err,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": mode,
            "host": nbe_host if mode == "local" else "stokercloud.dk",
            "serial": nbe_serial,
            "operating": (snapshot or {}).get("operating") if snapshot else None,
            "settings": (snapshot or {}).get("settings") if snapshot else None,
        }
        client.publish(attr_topic, json.dumps(payload), retain=False)

    while True:
        try:
            if mode == "cloud":
                if not cloud_user or not cloud_pass:
                    raise RuntimeError("cloud credentials missing")
                snap = read_cloud(nbe_serial, cloud_user, cloud_pass)
            else:
                if not nbe_host or not nbe_password:
                    raise RuntimeError("local host/pin missing")
                snap = read_local(nbe_host, nbe_serial, nbe_password)

            # перевіримо, що є дані
            ok = bool(snap.get("operating")) or bool(snap.get("settings"))
            publish(ok, snap, None if ok else "empty payload")

        except Exception as e:
            publish(False, None, str(e))

        time.sleep(interval)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
