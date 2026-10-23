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
2. **Isolate the bottleneck with `device_manager`**:
   - Call `device_manager` (`action="top_processes"`, `sort_by="memory"` or `"cpu"`) to pinpoint exact resource hogs with PIDs and window ownership.
   - Check `device_manager` (`action="disks"`, `"battery"`, `"network"`, or `"list_ports"`) for per-drive free space, power state, LAN/Wi-Fi details, or port conflicts (`port=3000`, etc.).
3. **Report diagnosis before remediating**:
   - Lead with the exact culprit and metric (e.g. *"RAM is at 92% — Chrome and Docker hold 19.4 GB; mic and Gemini Live are healthy"*).
   - Give the single concrete fix; apply safe reversible fixes (`computer_settings` or `device_manager` window controls) directly.
4. **Gate disruptive actions**:
   - `device_manager` (`action="kill_process"` / `"empty_recycle_bin"`) and `computer_settings` (`restart` / `shutdown` / `toggle_wifi`) place a `[CONFIRMATION_PENDING]` button on the HUD — ask the user in one short sentence to confirm on screen and never claim it completed early.

## Pitfalls

- Never kill processes (`kill -9` / `taskkill`) blindly without telling the user which app owns the PID and asking first.
- Never read out raw diagnostic tables line by line — report what failed, the exact reading, and how to fix it.

## Verification

Both `system_status` and `diagnostics_check` consulted? Root metric cited concretely? Any state-changing fix confirmed before execution?
