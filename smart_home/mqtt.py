"""MQTT stub — uses paho-mqtt if installed."""
_client = None

def connect(broker: str = "localhost", port: int = 1883):
    global _client
    try:
        import paho.mqtt.client as mqtt
        _client = mqtt.Client()
        _client.connect(broker, port, 60)
        _client.loop_start()
        return f"MQTT connected to {broker}:{port}"
    except Exception as e:
        return f"MQTT not available: {e} — pip install paho-mqtt and run a broker (Mosquitto)"

def publish(topic: str, payload: str):
    global _client
    if _client is None:
        return "MQTT not connected — call smart_home_control service=mqtt action=connect first"
    try:
        _client.publish(topic, payload)
        return f"Published to {topic}"
    except Exception as e:
        return f"Publish failed: {e}"
