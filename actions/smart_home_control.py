def smart_home_control(parameters: dict, player=None, **_):
    svc=str(parameters.get("service","") or parameters.get("platform","")).strip().lower()
    action=str(parameters.get("action","list")).strip().lower()
    if svc in ("tuya","tinytuya"):
        import smart_home.tuya as tuya
        if action=="list": return tuya.list_devices()
        if action in ("on","off","toggle","control"):
            return tuya.control(str(parameters.get("device_id","")), action, str(parameters.get("value","")))
        return "Tuya actions: list/on/off/toggle"
    if svc in ("mqtt","mosquitto"):
        import smart_home.mqtt as mqtt
        if action=="connect": return mqtt.connect(str(parameters.get("broker","localhost")), int(parameters.get("port",1883)))
        if action=="publish": return mqtt.publish(str(parameters.get("topic","")), str(parameters.get("payload","")) or str(parameters.get("message","")))
        return "MQTT actions: connect/publish"
    return "Smart home services: tuya, mqtt. Example: {service:tuya, action:list} or {service:mqtt, action:publish, topic:'home/light', payload:'on'}"

TOOL={
    "name":"smart_home_control",
    "description":"Smart Home: Tuya/MQTT via tinytuya/paho-mqtt. Services: tuya (list/on/off), mqtt (connect/publish).",
    "parameters":{"type":"OBJECT","properties":{"service":{"type":"STRING","description":"tuya|mqtt"},"platform":{"type":"STRING"},"action":{"type":"STRING","description":"list|on|off|connect|publish"},"device_id":{"type":"STRING"},"value":{"type":"STRING"},"broker":{"type":"STRING"},"port":{"type":"NUMBER"},"topic":{"type":"STRING"},"payload":{"type":"STRING"},"message":{"type":"STRING"}},"required":["service","action"]},"handler":smart_home_control
}
