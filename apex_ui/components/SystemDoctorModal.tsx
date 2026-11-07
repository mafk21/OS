"use client";

import React, { useCallback, useEffect, useState } from "react";
import { Activity, Download, RefreshCw, ShieldCheck, Wrench, X } from "lucide-react";

export type DoctorItem = {
  check: string;
  status: "ok" | "warning" | "error";
  state: "healthy" | "degraded" | "unavailable" | "not_configured";
  code: string;
  summary: string;
  evidence: string;
  remediation: string;
};

type DoctorReport = {
  overall: "ok" | "warning" | "error";
  counts: Record<string, number>;
  installation: {
    installation_id: string;
    root: string;
    executable: string;
    entrypoint: string;
    install_type: string;
    revision: string;
    platform: string;
    python: string;
  };
  results: DoctorItem[];
};

const REPAIRS: Record<string, string> = {
  shortcut: "shortcut",
  permissions: "permissions",
  dependencies: "dependencies",
  hud: "hud",
  hud_port: "hud_port",
  backups: "soul_backup",
  memory: "soul_backup",
};

export default function SystemDoctorModal({
  primary,
  panelBg,
  onClose,
}: {
  primary: string;
  panelBg: string;
  onClose: () => void;
}) {
  const [report, setReport] = useState<DoctorReport | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [repairResult, setRepairResult] = useState<{ repair: string; ok: boolean; verified: boolean; message: string; rolled_back: boolean } | null>(null);
  const [lifecycle, setLifecycle] = useState<{ active_id: string; current_id: string; is_active: boolean; other_count: number; installations: { installation_id: string; root: string; revision: string; install_type: string }[] } | null>(null);
  const [operations, setOperations] = useState<{ tasks: Record<string, number>; actions: Record<string, number>; memory_conflicts: number; providers: Record<string, { failures: number }>; proactive: { enabled: boolean; daily_limit?: number } } | null>(null);
  const [proactivePolicy, setProactivePolicy] = useState<{ enabled: boolean; use_memory: boolean; use_monitors: boolean; use_recent_conversation: boolean; quiet_start: number; quiet_end: number; daily_limit: number; allowed_topics: string[]; blocked_topics: string[]; minimum_urgency: string } | null>(null);
  const [providerRouting, setProviderRouting] = useState<{ provider: string; cost_priority: string; latency_priority: string } | null>(null);
  const [browserCompanion, setBrowserCompanion] = useState<{ paired: boolean; connected: boolean; last_received_at?: number; extension_path?: string; token?: string } | null>(null);

  const loadLifecycle = useCallback(async () => {
    try {
      const response = await fetch("/api/action", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "installation_lifecycle", operation: "status" }) });
      const data = await response.json();
      if (data.lifecycle) setLifecycle(data.lifecycle);
    } catch {}
  }, []);

  const lifecycleAction = useCallback(async (operation: "make_active" | "unregister", installationId?: string) => {
    setBusy(true);
    try {
      const response = await fetch("/api/action", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "installation_lifecycle", operation, installation_id: installationId }) });
      const data = await response.json();
      setMessage(data.message || data.error || "Lifecycle action was not staged.");
      if (data.lifecycle) setLifecycle(data.lifecycle);
    } catch { setMessage("Lifecycle request failed safely. Nothing was changed."); }
    finally { setBusy(false); }
  }, []);

  const request = useCallback(async (operation: "run" | "report" = "run") => {
    setBusy(true);
    setMessage("");
    try {
      const response = await fetch("/api/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "system_doctor", operation }),
      });
      const data = await response.json();
      if (!response.ok || !data.ok) throw new Error(data.error || "System Doctor failed");
      setReport(data.doctor as DoctorReport);
      setMessage(data.report_path ? `Redacted report saved to ${data.report_path}` : "Health checks completed.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "System Doctor failed safely.");
    } finally {
      setBusy(false);
    }
  }, []);

  const repair = useCallback(async (name: string) => {
    setBusy(true);
    setMessage("");
    try {
      const response = await fetch("/api/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "system_doctor", operation: "repair", repair: name }),
      });
      const data = await response.json();
      setMessage(data.message || data.error || "Repair was not staged.");
    } catch {
      setMessage("Repair request failed safely. Nothing was changed.");
    } finally {
      setBusy(false);
    }
  }, []);

  const browserAction = useCallback(async (action: "browser_companion_pair" | "browser_companion_revoke") => {
    try {
      const response = await fetch("/api/hud/action", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action }) });
      const data = await response.json();
      if (action === "browser_companion_pair" && data.ok) setBrowserCompanion({ ...data.status, token: data.token, extension_path: data.extension_path });
      if (action === "browser_companion_revoke" && data.ok) setBrowserCompanion({ paired: false, connected: false });
      setMessage(data.message || (data.ok ? "Browser companion updated." : data.error));
    } catch { setMessage("Browser companion request failed safely."); }
  }, []);

  const saveProviderRouting = useCallback(async (next: NonNullable<typeof providerRouting>) => {
    setProviderRouting(next);
    try {
      const response = await fetch("/api/hud/action", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "provider_routing_save", ...next }) });
      const data = await response.json();
      setMessage(data.ok ? "Provider routing preferences updated." : (data.error || "Routing update failed safely."));
    } catch { setMessage("Routing update failed safely."); }
  }, []);

  const saveProactivePolicy = useCallback(async (next: NonNullable<typeof proactivePolicy>) => {
    setProactivePolicy(next);
    try {
      const response = await fetch("/api/hud/action", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "proactive_policy_save", ...next }) });
      const data = await response.json();
      setMessage(data.ok ? "Proactive permissions updated." : (data.error || "Policy update failed safely."));
    } catch { setMessage("Policy update failed safely."); }
  }, []);

  useEffect(() => {
    void request(); void loadLifecycle();
    void fetch("/api/hud/operations").then((response) => response.json()).then((data) => { if (data.ok) setOperations(data); }).catch(() => {});
    void fetch("/api/hud/action", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "proactive_policy_get" }) }).then((response) => response.json()).then((data) => { if (data.ok) setProactivePolicy(data.policy); }).catch(() => {});
    void fetch("/api/hud/action", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "provider_routing_get" }) }).then((response) => response.json()).then((data) => { if (data.ok) setProviderRouting(data.routing); }).catch(() => {});
    void fetch("/api/hud/action", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "browser_companion_status" }) }).then((response) => response.json()).then((data) => { if (data.ok) setBrowserCompanion({ ...data.status, extension_path: data.extension_path }); }).catch(() => {});
  }, [request, loadLifecycle]);
  useEffect(() => {
    const poll = window.setInterval(async () => {
      try {
        const response = await fetch("/api/action", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ action: "system_doctor", operation: "repair_status" }),
        });
        const data = await response.json();
        if (data.repair_result) setRepairResult(data.repair_result);
      } catch {}
    }, 2000);
    return () => window.clearInterval(poll);
  }, []);
  useEffect(() => {
    const key = (event: KeyboardEvent) => { if (event.key === "Escape") onClose(); };
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  }, [onClose]);

  const statusColor = (status: string) => status === "ok" ? "#34d399" : status === "warning" ? "#f5a623" : "#ff5b79";

  return (
    <div role="dialog" aria-modal="true" aria-label="JARVIS System Doctor" onClick={onClose}
      style={{ position: "fixed", inset: 0, zIndex: 110, background: "rgba(2,6,12,.82)", backdropFilter: "blur(12px)", display: "grid", placeItems: "center", padding: 16 }}>
      <section onClick={(event) => event.stopPropagation()}
        style={{ width: "min(820px,96vw)", maxHeight: "90vh", overflow: "auto", background: panelBg, border: `1px solid ${primary}55`, borderRadius: 18, padding: 20, boxShadow: `0 0 50px ${primary}22` }}>
        <header style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
          <ShieldCheck size={20} color={primary} aria-hidden="true" />
          <div style={{ flex: 1 }}>
            <div style={{ color: primary, fontFamily: "var(--font-mono)", letterSpacing: ".18em", fontSize: 12 }}>SYSTEM DOCTOR</div>
            <div style={{ color: "rgba(240,237,232,.58)", fontSize: 11 }}>Observed health, evidence, and confirmation-gated repairs</div>
          </div>
          <button type="button" aria-label="Close System Doctor" onClick={onClose} style={iconButton}><X size={18} /></button>
        </header>

        {operations && (
          <section aria-label="Operations overview" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(140px,1fr))", gap: 8, marginBottom: 12 }}>
            {[
              ["ACTIVE TASKS", Object.entries(operations.tasks).filter(([state]) => !["completed", "failed", "cancelled", "expired"].includes(state)).reduce((sum, [, count]) => sum + count, 0)],
              ["UNCERTAIN ACTIONS", operations.actions.unverified || 0],
              ["MEMORY CONFLICTS", operations.memory_conflicts],
              ["PROACTIVE", operations.proactive.enabled ? `ON · ${operations.proactive.daily_limit || 0}/DAY` : "OFF"],
            ].map(([label, value]) => <div key={String(label)} style={{ border: "1px solid rgba(255,255,255,.09)", borderRadius: 10, padding: 10, background: "rgba(255,255,255,.025)" }}><div style={meta}>{label}</div><strong style={{ color: primary, fontFamily: "var(--font-mono)", fontSize: 16 }}>{value}</strong></div>)}
          </section>
        )}

        {browserCompanion && (
          <section aria-label="Browser companion" style={{ border: "1px solid rgba(255,255,255,.09)", borderRadius: 10, padding: 10, marginBottom: 12 }}>
            <div style={{ ...meta, marginBottom: 7 }}>BROWSER COMPANION · {browserCompanion.connected ? "CONNECTED" : browserCompanion.paired ? "PAIRED" : "NOT PAIRED"}</div>
            <div style={{ color: "rgba(240,237,232,.7)", fontSize: 11 }}>Load the extension from <code>{browserCompanion.extension_path || "browser_extension"}</code>. It shares only the active tab after you press Send.</div>
            {browserCompanion.token && <div style={{ ...meta, overflowWrap: "anywhere", marginTop: 7 }}>Pairing token: <code>{browserCompanion.token}</code></div>}
            <button type="button" onClick={() => void browserAction("browser_companion_pair")} style={{ ...actionButton, color: primary, borderColor: `${primary}77`, marginTop: 8 }}>{browserCompanion.paired ? "Show pairing token" : "Pair extension"}</button>
            {browserCompanion.paired && <button type="button" onClick={() => void browserAction("browser_companion_revoke")} style={{ ...actionButton, marginTop: 8, marginLeft: 7 }}>Revoke access</button>}
          </section>
        )}

        {providerRouting && (
          <section aria-label="Provider routing preferences" style={{ border: "1px solid rgba(255,255,255,.09)", borderRadius: 10, padding: 10, marginBottom: 12 }}>
            <div style={{ ...meta, marginBottom: 8 }}>PROVIDER ROUTING · selected provider: {providerRouting.provider}</div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <label style={meta}>Cost<select value={providerRouting.cost_priority} onChange={(event) => void saveProviderRouting({ ...providerRouting, cost_priority: event.target.value })}><option value="balanced">Balanced</option><option value="lowest">Lowest cost</option></select></label>
              <label style={meta}>Latency<select value={providerRouting.latency_priority} onChange={(event) => void saveProviderRouting({ ...providerRouting, latency_priority: event.target.value })}><option value="balanced">Balanced</option><option value="fastest">Fastest</option></select></label>
            </div>
            <div style={{ ...meta, marginTop: 6 }}>Private and restricted requests remain local-only regardless of these preferences. Pinned providers never silently fail over.</div>
          </section>
        )}

        {proactivePolicy && (
          <section aria-label="Proactive permissions" style={{ border: "1px solid rgba(255,255,255,.09)", borderRadius: 10, padding: 10, marginBottom: 12 }}>
            <div style={{ ...meta, marginBottom: 8 }}>PROACTIVE PERMISSIONS · quiet {proactivePolicy.quiet_start}:00–{proactivePolicy.quiet_end}:00 · limit {proactivePolicy.daily_limit}/day</div>
            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", color: "rgba(240,237,232,.76)", fontSize: 11 }}>
              {([['enabled', 'Enabled'], ['use_memory', 'Use memory'], ['use_monitors', 'Use monitors'], ['use_recent_conversation', 'Use recent conversation']] as const).map(([key, label]) => (
                <label key={key} style={{ display: "flex", gap: 5, alignItems: "center" }}><input type="checkbox" checked={proactivePolicy[key]} onChange={(event) => void saveProactivePolicy({ ...proactivePolicy, [key]: event.target.checked })} />{label}</label>
              ))}
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(130px,1fr))", gap: 7, marginTop: 9 }}>
              {([['quiet_start', 'Quiet start', 0, 23], ['quiet_end', 'Quiet end', 0, 23], ['daily_limit', 'Daily limit', 0, 48]] as const).map(([key, label, min, max]) => <label key={key} style={meta}>{label}<input aria-label={label} type="number" min={min} max={max} value={proactivePolicy[key]} onChange={(event) => setProactivePolicy({ ...proactivePolicy, [key]: Number(event.target.value) })} onBlur={() => void saveProactivePolicy(proactivePolicy)} style={{ width: "100%", marginTop: 3 }} /></label>)}
              <label style={meta}>Minimum urgency<select value={proactivePolicy.minimum_urgency} onChange={(event) => void saveProactivePolicy({ ...proactivePolicy, minimum_urgency: event.target.value })} style={{ width: "100%", marginTop: 3 }}><option>low</option><option>normal</option><option>high</option><option>critical</option></select></label>
              <label style={meta}>Allowed topics<input aria-label="Allowed topics" value={proactivePolicy.allowed_topics.join(', ')} onChange={(event) => setProactivePolicy({ ...proactivePolicy, allowed_topics: event.target.value.split(',').map((v) => v.trim()).filter(Boolean) })} onBlur={() => void saveProactivePolicy(proactivePolicy)} style={{ width: "100%", marginTop: 3 }} /></label>
              <label style={meta}>Blocked topics<input aria-label="Blocked topics" value={proactivePolicy.blocked_topics.join(', ')} onChange={(event) => setProactivePolicy({ ...proactivePolicy, blocked_topics: event.target.value.split(',').map((v) => v.trim()).filter(Boolean) })} onBlur={() => void saveProactivePolicy(proactivePolicy)} style={{ width: "100%", marginTop: 3 }} /></label>
            </div>
          </section>
        )}

        {report && (
          <div style={{ padding: 12, borderRadius: 12, border: `1px solid ${statusColor(report.overall)}55`, marginBottom: 12 }}>
            <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
              <Activity size={16} color={statusColor(report.overall)} />
              <strong style={{ color: statusColor(report.overall), textTransform: "uppercase" }}>{report.overall}</strong>
              <span style={meta}>{report.counts.ok || 0} healthy · {report.counts.warning || 0} degraded · {report.counts.error || 0} unavailable</span>
            </div>
            <div style={{ ...meta, marginTop: 8, overflowWrap: "anywhere" }}>
              ID {report.installation.installation_id} · {report.installation.install_type} · {report.installation.revision}<br />
              Python {report.installation.python} · {report.installation.platform}<br />
              {report.installation.root}<br />
              {lifecycle ? `${lifecycle.is_active ? "ACTIVE INSTALLATION" : "NOT ACTIVE"} · ${lifecycle.other_count} other registered` : "Loading lifecycle…"}
            </div>
            {lifecycle && !lifecycle.is_active && (
              <button type="button" disabled={busy} onClick={() => void lifecycleAction("make_active")} style={{ ...actionButton, borderColor: `${primary}77`, color: primary, marginTop: 9 }}>
                Make this installation active
              </button>
            )}
            {lifecycle && (
              <button type="button" disabled={busy} onClick={() => void lifecycleAction("unregister", lifecycle.current_id)} style={{ ...actionButton, marginTop: 9, marginLeft: 7 }}>
                Unregister this metadata
              </button>
            )}
            {lifecycle && lifecycle.installations.filter((row) => row.installation_id !== lifecycle.current_id).map((row) => (
              <div key={row.installation_id} style={{ ...meta, marginTop: 9, paddingTop: 8, borderTop: "1px solid rgba(255,255,255,.07)", overflowWrap: "anywhere" }}>
                Registered: {row.install_type} · {row.revision} · {row.root}
                {row.installation_id === lifecycle.active_id ? " · ACTIVE" : ""}
                <button type="button" disabled={busy || row.installation_id === lifecycle.active_id} onClick={() => void lifecycleAction("unregister", row.installation_id)} style={{ ...actionButton, marginLeft: 7 }}>
                  Unregister obsolete metadata
                </button>
              </div>
            ))}
          </div>
        )}

        <div aria-live="polite" role="status" style={{ color: "rgba(240,237,232,.7)", minHeight: 18, fontSize: 11, marginBottom: 8 }}>{busy ? "Running bounded checks…" : message}</div>
        {repairResult && (
          <div role="status" style={{ border: `1px solid ${statusColor(repairResult.ok && repairResult.verified ? "ok" : "error")}55`, borderRadius: 9, padding: 9, marginBottom: 9, color: "rgba(240,237,232,.78)", fontSize: 11 }}>
            Repair {repairResult.repair}: {repairResult.message} · verified={String(repairResult.verified)}
            {repairResult.rolled_back ? " · previous state restored" : ""}
          </div>
        )}

        <div style={{ display: "grid", gap: 8 }}>
          {report?.results.map((item) => {
            const repairName = REPAIRS[item.check];
            return (
              <details key={`${item.check}-${item.code}`} style={{ border: "1px solid rgba(255,255,255,.09)", borderRadius: 10, padding: "10px 12px", background: "rgba(255,255,255,.025)" }}>
                <summary style={{ cursor: "pointer", color: "#f0ede8", display: "flex", gap: 9, alignItems: "center" }}>
                  <span aria-hidden="true" style={{ width: 8, height: 8, borderRadius: 8, background: statusColor(item.status), boxShadow: `0 0 8px ${statusColor(item.status)}` }} />
                  <strong style={{ textTransform: "uppercase", fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: ".08em" }}>{item.check.replaceAll("_", " ")}</strong>
                  <span style={{ ...meta, marginLeft: "auto" }}>{item.state}</span>
                </summary>
                <div style={{ marginTop: 10, paddingLeft: 17, color: "rgba(240,237,232,.74)", fontSize: 12, lineHeight: 1.55 }}>
                  <div>{item.summary}</div>
                  {item.evidence && <div style={{ ...meta, marginTop: 5, overflowWrap: "anywhere" }}>Evidence: {item.evidence}</div>}
                  {item.remediation && <div style={{ color: "#f5c76b", marginTop: 5 }}>Recommendation: {item.remediation}</div>}
                  <div style={{ ...meta, marginTop: 5 }}>{item.code}</div>
                  {repairName && item.status !== "ok" && (
                    <button type="button" disabled={busy} onClick={() => void repair(repairName)} style={{ ...actionButton, borderColor: `${primary}77`, color: primary, marginTop: 9 }}>
                      <Wrench size={12} /> Stage verified repair
                    </button>
                  )}
                </div>
              </details>
            );
          })}
        </div>

        <footer style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 16, borderTop: "1px solid rgba(255,255,255,.08)", paddingTop: 14 }}>
          <button type="button" disabled={busy} onClick={() => void request()} style={{ ...actionButton, borderColor: `${primary}77`, color: primary }}><RefreshCw size={13} /> Run again</button>
          <button type="button" disabled={busy} onClick={() => void request("report")} style={actionButton}><Download size={13} /> Export redacted report</button>
          <button type="button" onClick={onClose} style={{ ...actionButton, marginLeft: "auto" }}>Close</button>
        </footer>
      </section>
    </div>
  );
}

const meta: React.CSSProperties = { color: "rgba(240,237,232,.5)", fontFamily: "var(--font-mono)", fontSize: 10 };
const iconButton: React.CSSProperties = { background: "none", border: 0, color: "rgba(255,255,255,.65)", cursor: "pointer", padding: 5 };
const actionButton: React.CSSProperties = { display: "inline-flex", alignItems: "center", gap: 6, border: "1px solid rgba(255,255,255,.18)", borderRadius: 999, background: "rgba(255,255,255,.035)", color: "rgba(240,237,232,.76)", padding: "7px 12px", cursor: "pointer", fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: ".04em" };
