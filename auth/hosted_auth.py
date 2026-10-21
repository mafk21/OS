"""
Hosted auth alternative — Phase 7.3: email OTP + daily quota, no user API key paste (opt-in).
Falls back to local api_keys.json if hosted unreachable.
"""
import pathlib, json, time, requests

STORE = pathlib.Path("memory/hosted_auth.json")
HOSTED_URL = "https://os-auth.example.com"  # placeholder — user can self-host

def is_hosted_enabled():
    try:
        import memory.config_manager as cm
        return bool(cm.load_api_keys().get("hosted_auth_enabled"))
    except: return False

def request_otp(email: str):
    if not email or "@" not in email: return "Need valid email"
    try:
        r = requests.post(f"{HOSTED_URL}/otp/request", json={"email": email}, timeout=10)
        if r.ok: return f"OTP sent to {email} — check inbox"
        return f"OTP request failed: {r.text[:200]}"
    except Exception as e: return f"Hosted auth offline: {e} — using local api_keys.json"

def verify_otp(email: str, otp: str):
    try:
        r = requests.post(f"{HOSTED_URL}/otp/verify", json={"email": email, "otp": otp}, timeout=10)
        if r.ok:
            j = r.json()
            STORE.parent.mkdir(parents=True, exist_ok=True)
            STORE.write_text(json.dumps({"email": email, "token": j.get("token",""), "quota": j.get("quota", 50), "verified": time.time()}, indent=2))
            return f"Verified — daily quota {j.get('quota', 50)}"
        return f"Verify failed: {r.text[:200]}"
    except Exception as e: return f"Verify error: {e}"

def quota_status():
    if not STORE.exists(): return "Not logged in via hosted auth"
    d = json.loads(STORE.read_text())
    return f"{d.get('email','')} — quota {d.get('quota','?')} / day"
