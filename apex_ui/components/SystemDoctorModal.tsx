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

  useEffect(() => { void request(); }, [request]);
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
              {report.installation.root}
            </div>
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
