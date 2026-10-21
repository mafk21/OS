"""Hosted auth action — Phase 7.3"""
def hosted_auth(parameters: dict, player=None, **_):
    action=str(parameters.get("action","status")).strip().lower()
    if action=="request_otp":
        email=str(parameters.get("email","")).strip()
        import auth.hosted_auth as ha
        return ha.request_otp(email)
    if action=="verify":
        email=str(parameters.get("email","")).strip()
        otp=str(parameters.get("otp","") or parameters.get("code","")).strip()
        import auth.hosted_auth as ha
        return ha.verify_otp(email, otp)
    if action=="status":
        import auth.hosted_auth as ha
        return ha.quota_status()
    return "Hosted auth: request_otp (email), verify (email, otp), status"

TOOL={
    "name":"hosted_auth",
    "description":"Hosted auth alternative: email OTP + daily quota, no API key paste (opt-in). Actions: request_otp, verify, status.",
    "parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"request_otp|verify|status"},"email":{"type":"STRING"},"otp":{"type":"STRING"},"code":{"type":"STRING"}},"required":["action"]},"handler":hosted_auth
}
