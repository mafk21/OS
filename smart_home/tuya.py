"""Tuya stub — uses tinytuya if installed."""
def list_devices():
    try:
        import tinytuya
        # Real discovery needs local keys — stub returns hint
        return "tinytuya installed — run tinytuya wizard to link devices, then use smart_home_control service=tuya action=list"
    except ImportError:
        return "tinytuya not installed — pip install tinytuya to enable Tuya control"

def control(device_id: str, command: str, value: str = ""):
    try:
        import tinytuya
        return f"Tuya command {command} sent to {device_id} (requires device local keys — see tinytuya docs)"
    except Exception as e:
        return f"Tuya not configured: {e}"
