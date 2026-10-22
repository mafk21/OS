---
name: system-doctor
description: Hardware, audio, network, storage, and JARVIS health diagnostics — use when mic/speaker fails, CPU/RAM spikes, APIs error, or asked to run diagnostics.
---

# System doctor

Diagnose slow machines, audio glitches, network/API failures, low disk space, and JARVIS subsystem issues systematically — separating live telemetry from root causes and safe fixes.

## When to use

"Why is my PC lagging?", "run diagnostics", "check my mic/audio/network", "is Ollama running?", "my disk is full", or "what's wrong with JARVIS?".

## Procedure

1. **Collect live telemetry in parallel**:
   - Call `system_status` for real-time CPU, RAM, GPU, and thermal readings.
   - Call `diagnostics_check` (`action="full"`, or targeted `"audio"` / `"network"` / `"storage"` / `"skills"`) to verify API keys, mic/speaker devices, cloud reachability, disk free space, active skills, camera, and local Ollama fallback.
2. **Isolate the bottleneck**:
   - If CPU or RAM is >85% or disk free space is <5 GB, inspect top resource consumers or directory sizes read-only via `shell_agent` (`action="run"`, e.g. process top-10 or disk summary for the active OS).
3. **Report diagnosis before remediating**:
   - Lead with the exact culprit and metric (e.g. *"RAM is at 92% — Chrome and Docker hold 19.4 GB; mic and Gemini Live are healthy"*).
   - Give the single concrete fix; apply safe reversible fixes (`computer_settings` or opening audio picker) directly.
4. **Gate disruptive actions**:
   - Killing user processes, toggling Wi-Fi, restarting services, or rebooting (`computer_settings` restart/shutdown uses the UI `[CONFIRMATION_PENDING]` gate) ALWAYS require explicit user confirmation first.

## Pitfalls

- Never kill processes (`kill -9` / `taskkill`) blindly without telling the user which app owns the PID and asking first.
- Never read out raw diagnostic tables line by line — report what failed, the exact reading, and how to fix it.

## Verification

Both `system_status` and `diagnostics_check` consulted? Root metric cited concretely? Any state-changing fix confirmed before execution?
