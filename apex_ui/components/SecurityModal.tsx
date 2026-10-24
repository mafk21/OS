"use client";

import React, { useCallback, useEffect, useState } from "react";
import {
  CheckCircle2,
  Copy,
  FileSearch,
  Globe,
  KeyRound,
  Lock,
  PowerOff,
  RefreshCw,
  ShieldCheck,
  X,
} from "lucide-react";
import { useJarvis } from "./JarvisBridge";

type AuditRow = {
  id: number;
  time_str: string;
  actor: string;
  action: string;
  args_redacted: string;
  result_summary: string;
  status: string;
  entry_hash: string;
};

type PortalVisit = {
  ts: string;
  ip: string;
  user_agent: string;
  allowed: boolean;
  reason: string;
};

type PortalItem = {
  id: string;
  title: string;
  scope_type: string;
  active: boolean;
  revoked: boolean;
  expired: boolean;
  view_count: number;
  max_views: number;
  created_str: string;
  visits: PortalVisit[];
};

type SecSnap = {
  cipher: string;
  key_present: boolean;
  encrypted_account_secrets: number;
  encrypted_config_secrets: number;
  chain: { valid: boolean; checked: number; broken_at_id: number | null };
  audit_logs: AuditRow[];
  portals: PortalItem[];
};

const GREEN = "#3be38a";
const RED = "#ff5d6c";

export default function SecurityModal() {
  const { securityModalOpen, setSecurityModalOpen, theme } = useJarvis();

  const [tab, setTab] = useState<"vault" | "audit" | "portals">("vault");
  const [sec, setSec] = useState<SecSnap | null>(null);
  const [auditQuery, setAuditQuery] = useState("");
  const [statusMsg, setStatusMsg] = useState("");

  // Portal creation form
  const [pTitle, setPTitle] = useState("");
  const [pBody, setPBody] = useState("");
  const [pHours, setPHours] = useState(24);
  const [pMaxViews, setPMaxViews] = useState(50);
  const [latestPortalUrl, setLatestPortalUrl] = useState("");

  const refresh = useCallback(async () => {
    try {
      const r = await fetch("/api/hud/security");
      if (r.ok) {
        const j = await r.json();
        if (j.security) setSec(j.security);
      }
    } catch {}
  }, []);

  useEffect(() => {
    if (securityModalOpen) {
      refresh();
      setStatusMsg("");
    }
  }, [securityModalOpen, refresh]);

  if (!securityModalOpen) return null;

  const PRIMARY = theme.primary;
  const SECONDARY = theme.secondary;

  const post = async (payload: Record<string, unknown>) => {
    const r = await fetch("/api/hud/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const j = await r.json();
    if (j.security) setSec(j.security);
    return j;
  };

  const onSearchAudit = async (e: React.FormEvent) => {
    e.preventDefault();
    const j = await post({ action: "audit_search", query: auditQuery });
    if (Array.isArray(j.audit_logs) && sec) {
      setSec({ ...sec, audit_logs: j.audit_logs });
    }
  };

  const onCreatePortal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pBody.trim()) return;
    const j = await post({
      action: "portal_create",
      title: pTitle.trim() || "Shared JARVIS Brief",
      content_body: pBody.trim(),
      expires_hours: pHours,
      max_views: pMaxViews,
    });
    if (j.ok && j.portal?.path) {
      const fullUrl = `${window.location.origin}${j.portal.path}`;
      setLatestPortalUrl(fullUrl);
      setPTitle("");
      setPBody("");
      setStatusMsg("Created scoped read-only Guest Portal.");
    } else if (j.error) {
      setStatusMsg(j.error);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Security Vault, Audit Log & Guest Portals"
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 85,
        background: "rgba(2, 5, 12, 0.8)",
        backdropFilter: "blur(18px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 18,
      }}
    >
      <div
        style={{
          width: "min(960px, 96vw)",
          height: "min(730px, 90vh)",
          background: theme.drawerBg,
          border: `1px solid ${PRIMARY}44`,
          borderRadius: 20,
          boxShadow: "0 24px 80px rgba(0,0,0,0.85)",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        {/* Header */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            padding: "14px 22px",
            borderBottom: `1px solid ${PRIMARY}26`,
          }}
        >
          <ShieldCheck size={17} color={PRIMARY} />
          <div style={{ flex: 1 }}>
            <div
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: 11,
                letterSpacing: "0.24em",
                color: PRIMARY,
              }}
            >
              SHIELD · ENCRYPTED VAULT, TAMPER-EVIDENT AUDIT & PORTALS
            </div>
            <div style={{ fontSize: 11.5, color: "rgba(240,237,232,0.58)", marginTop: 2 }}>
              Cipher: {sec?.cipher || "AES-256-GCM"} · Chain:{" "}
              {sec?.chain?.valid
                ? `VERIFIED (${sec.chain.checked} entries)`
                : "CHECK REQUIRED"}
            </div>
          </div>
          <button
            type="button"
            onClick={() => setSecurityModalOpen(false)}
            style={{
              background: "none",
              border: "none",
              color: "rgba(240,237,232,0.6)",
              cursor: "pointer",
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Tabs */}
        <div
          style={{
            display: "flex",
            gap: 8,
            padding: "10px 22px",
            borderBottom: "1px solid rgba(255,255,255,0.07)",
          }}
        >
          {(
            [
              { id: "vault", label: "CREDENTIAL VAULT", icon: Lock },
              {
                id: "audit",
                label: `AUDIT CHAIN (${sec?.audit_logs?.length || 0})`,
                icon: FileSearch,
              },
              {
                id: "portals",
                label: `GUEST PORTALS (${sec?.portals?.length || 0})`,
                icon: Globe,
              },
            ] as const
          ).map((t) => {
            const Icon = t.icon;
            const active = tab === t.id;
            return (
              <button
                key={t.id}
                type="button"
                onClick={() => setTab(t.id)}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 6,
                  padding: "7px 13px",
                  borderRadius: 999,
                  border: `1px solid ${active ? PRIMARY : "rgba(255,255,255,0.12)"}`,
                  background: active ? `${PRIMARY}22` : "transparent",
                  color: active ? PRIMARY : "rgba(240,237,232,0.7)",
                  fontFamily: "var(--font-mono)",
                  fontSize: 10,
                  letterSpacing: "0.12em",
                  cursor: "pointer",
                }}
              >
                <Icon size={12} />
                {t.label}
              </button>
            );
          })}
          {statusMsg && (
            <span
              style={{
                marginLeft: "auto",
                alignSelf: "center",
                fontFamily: "var(--font-mono)",
                fontSize: 10,
                color: GREEN,
              }}
            >
              {statusMsg}
            </span>
          )}
        </div>

        {/* Body */}
        <div style={{ flex: 1, overflowY: "auto", padding: "18px 22px" }}>
          {tab === "vault" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
                  gap: 14,
                }}
              >
                <div
                  style={{
                    padding: 16,
                    borderRadius: 14,
                    background: "rgba(255,255,255,0.025)",
                    border: `1px solid ${GREEN}44`,
                  }}
                >
                  <div
                    style={{
                      fontFamily: "var(--font-mono)",
                      fontSize: 10,
                      color: GREEN,
                      letterSpacing: "0.14em",
                    }}
                  >
                    AT-REST CIPHER
                  </div>
                  <div style={{ fontSize: 17, fontWeight: 600, marginTop: 6 }}>
                    {sec?.cipher || "AES-256-GCM"}
                  </div>
                  <div style={{ fontSize: 11.5, color: "rgba(240,237,232,0.6)", marginTop: 4 }}>
                    256-bit local master key (`0600` permissions) — never leaves your device.
                  </div>
                </div>

                <div
                  style={{
                    padding: 16,
                    borderRadius: 14,
                    background: "rgba(255,255,255,0.025)",
                    border: `1px solid ${PRIMARY}38`,
                  }}
                >
                  <div
                    style={{
                      fontFamily: "var(--font-mono)",
                      fontSize: 10,
                      color: PRIMARY,
                      letterSpacing: "0.14em",
                    }}
                  >
                    ENCRYPTED SECRETS ON DISK
                  </div>
                  <div style={{ fontSize: 17, fontWeight: 600, marginTop: 6 }}>
                    {(sec?.encrypted_account_secrets || 0) +
                      (sec?.encrypted_config_secrets || 0)}{" "}
                    protected tokens
                  </div>
                  <div style={{ fontSize: 11.5, color: "rgba(240,237,232,0.6)", marginTop: 4 }}>
                    Accounts Vault: {sec?.encrypted_account_secrets || 0} · Config Vault:{" "}
                    {sec?.encrypted_config_secrets || 0}
                  </div>
                </div>
              </div>

              <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
                <button
                  type="button"
                  onClick={async () => {
                    const j = await post({ action: "vault_rotate_key" });
                    setStatusMsg(
                      `Rotated master key & re-encrypted ${j.reencrypted_count ?? 0} secrets.`
                    );
                  }}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 7,
                    padding: "9px 16px",
                    borderRadius: 999,
                    border: `1px solid ${PRIMARY}66`,
                    background: `${PRIMARY}22`,
                    color: PRIMARY,
                    fontFamily: "var(--font-mono)",
                    fontSize: 10,
                    cursor: "pointer",
                  }}
                >
                  <KeyRound size={12} /> ROTATE 256-BIT MASTER KEY
                </button>

                <button
                  type="button"
                  onClick={async () => {
                    const enable = (sec?.encrypted_config_secrets || 0) === 0;
                    await post({ action: "vault_encrypt_config", enabled: enable });
                    setStatusMsg(
                      enable
                        ? "Encrypted config/api_keys.json secrets at rest."
                        : "Restored plaintext compatibility on config/api_keys.json."
                    );
                  }}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 7,
                    padding: "9px 16px",
                    borderRadius: 999,
                    border: `1px solid ${SECONDARY}66`,
                    background: `${SECONDARY}1f`,
                    color: SECONDARY,
                    fontFamily: "var(--font-mono)",
                    fontSize: 10,
                    cursor: "pointer",
                  }}
                >
                  <Lock size={12} />
                  {(sec?.encrypted_config_secrets || 0) > 0
                    ? "STRICT CONFIG ENCRYPTION: ON"
                    : "ENABLE STRICT API_KEYS.JSON ENCRYPTION"}
                </button>
              </div>
            </div>
          )}

          {tab === "audit" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <form onSubmit={onSearchAudit} style={{ flex: 1, display: "flex", gap: 8 }}>
                  <input
                    value={auditQuery}
                    onChange={(e) => setAuditQuery(e.target.value)}
                    placeholder="Search tamper-evident action logs…"
                    style={{
                      flex: 1,
                      padding: "8px 12px",
                      borderRadius: 8,
                      border: "1px solid rgba(255,255,255,0.14)",
                      background: "rgba(0,0,0,0.35)",
                      color: "#f0ede8",
                      fontSize: 12,
                    }}
                  />
                  <button
                    type="submit"
                    style={{
                      padding: "8px 14px",
                      borderRadius: 8,
                      border: `1px solid ${PRIMARY}55`,
                      background: `${PRIMARY}1c`,
                      color: PRIMARY,
                      fontFamily: "var(--font-mono)",
                      fontSize: 10,
                      cursor: "pointer",
                    }}
                  >
                    SEARCH
                  </button>
                </form>

                <button
                  type="button"
                  onClick={async () => {
                    const j = await post({ action: "audit_verify" });
                    setStatusMsg(
                      j.chain?.valid
                        ? `SHA-256 Chain Verified (${j.chain.checked} entries intact)`
                        : `TAMPER DETECTED at entry #${j.chain?.broken_at_id}`
                    );
                  }}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 6,
                    padding: "8px 14px",
                    borderRadius: 8,
                    border: `1px solid ${GREEN}66`,
                    background: `${GREEN}1a`,
                    color: GREEN,
                    fontFamily: "var(--font-mono)",
                    fontSize: 10,
                    cursor: "pointer",
                  }}
                >
                  <CheckCircle2 size={12} /> VERIFY HASH CHAIN
                </button>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {(sec?.audit_logs || []).map((row) => (
                  <div
                    key={row.id}
                    style={{
                      padding: "9px 12px",
                      borderRadius: 9,
                      background: "rgba(255,255,255,0.025)",
                      border: "1px solid rgba(255,255,255,0.08)",
                      fontFamily: "var(--font-mono)",
                      fontSize: 11,
                    }}
                  >
                    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                      <span style={{ color: PRIMARY }}>#{row.id}</span>
                      <span style={{ color: SECONDARY }}>{row.action}</span>
                      <span style={{ color: "rgba(240,237,232,0.5)" }}>by {row.actor}</span>
                      <span style={{ flex: 1 }} />
                      <span style={{ color: "rgba(240,237,232,0.45)", fontSize: 10 }}>
                        {row.time_str} · sha256:{row.entry_hash}
                      </span>
                    </div>
                    <div style={{ color: "rgba(240,237,232,0.72)", marginTop: 4 }}>
                      {row.result_summary || row.args_redacted}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {tab === "portals" && (
            <div style={{ display: "grid", gridTemplateColumns: "1.1fr 1fr", gap: 18 }}>
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span
                    style={{
                      fontFamily: "var(--font-mono)",
                      fontSize: 10,
                      letterSpacing: "0.16em",
                      color: SECONDARY,
                      flex: 1,
                    }}
                  >
                    SCOPED EXTERNAL GUEST PORTALS
                  </span>
                  {(sec?.portals?.length || 0) > 0 && (
                    <button
                      type="button"
                      onClick={() => post({ action: "portal_revoke_all" })}
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: 5,
                        padding: "4px 10px",
                        borderRadius: 999,
                        border: `1px solid ${RED}66`,
                        background: `${RED}1f`,
                        color: RED,
                        fontFamily: "var(--font-mono)",
                        fontSize: 9,
                        cursor: "pointer",
                      }}
                    >
                      <PowerOff size={10} /> SHUT OFF ALL
                    </button>
                  )}
                </div>

                {(sec?.portals || []).map((p) => (
                  <div
                    key={p.id}
                    style={{
                      padding: "11px 14px",
                      borderRadius: 11,
                      background: "rgba(255,255,255,0.025)",
                      border: `1px solid ${p.active ? `${GREEN}55` : "rgba(255,255,255,0.08)"}`,
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ fontWeight: 600, fontSize: 12.5 }}>{p.title}</span>
                      <span
                        style={{
                          fontFamily: "var(--font-mono)",
                          fontSize: 9,
                          color: p.active ? GREEN : RED,
                        }}
                      >
                        {p.active ? "LIVE" : p.revoked ? "REVOKED" : "EXPIRED"}
                      </span>
                      <span style={{ flex: 1 }} />
                      <span style={{ fontFamily: "var(--font-mono)", fontSize: 9.5 }}>
                        Views: {p.view_count}/{p.max_views}
                      </span>
                      {p.active && (
                        <button
                          type="button"
                          onClick={() =>
                            post({ action: "portal_revoke", portal_id: p.id })
                          }
                          style={{
                            padding: "3px 8px",
                            borderRadius: 999,
                            border: `1px solid ${RED}66`,
                            background: "transparent",
                            color: RED,
                            fontFamily: "var(--font-mono)",
                            fontSize: 8.5,
                            cursor: "pointer",
                          }}
                        >
                          REVOKE
                        </button>
                      )}
                    </div>
                    {p.visits.length > 0 && (
                      <div
                        style={{
                          marginTop: 6,
                          paddingTop: 6,
                          borderTop: "1px solid rgba(255,255,255,0.06)",
                          fontFamily: "var(--font-mono)",
                          fontSize: 9.5,
                          color: "rgba(240,237,232,0.58)",
                        }}
                      >
                        Recent visit: {p.visits[0].ip} @ {p.visits[0].ts} ({p.visits[0].reason})
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <form
                onSubmit={onCreatePortal}
                style={{
                  padding: 15,
                  borderRadius: 14,
                  background: "rgba(255,255,255,0.025)",
                  border: "1px solid rgba(255,255,255,0.09)",
                  display: "flex",
                  flexDirection: "column",
                  gap: 9,
                }}
              >
                <div
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: 10,
                    letterSpacing: "0.16em",
                    color: PRIMARY,
                  }}
                >
                  + CREATE SCOPED GUEST PORTAL
                </div>
                <input
                  value={pTitle}
                  onChange={(e) => setPTitle(e.target.value)}
                  placeholder="Portal Title (e.g. Q4 Research Brief)"
                  style={{
                    padding: "8px 11px",
                    borderRadius: 8,
                    border: "1px solid rgba(255,255,255,0.14)",
                    background: "rgba(0,0,0,0.35)",
                    color: "#f0ede8",
                    fontSize: 12,
                  }}
                />
                <div style={{ display: "flex", gap: 8 }}>
                  <input
                    type="number"
                    min={1}
                    value={pHours}
                    onChange={(e) => setPHours(Number(e.target.value) || 24)}
                    placeholder="Expires (hours)"
                    style={{
                      flex: 1,
                      padding: "8px",
                      borderRadius: 8,
                      border: "1px solid rgba(255,255,255,0.14)",
                      background: "rgba(0,0,0,0.35)",
                      color: "#f0ede8",
                      fontSize: 12,
                    }}
                  />
                  <input
                    type="number"
                    min={1}
                    value={pMaxViews}
                    onChange={(e) => setPMaxViews(Number(e.target.value) || 50)}
                    placeholder="Max views"
                    style={{
                      flex: 1,
                      padding: "8px",
                      borderRadius: 8,
                      border: "1px solid rgba(255,255,255,0.14)",
                      background: "rgba(0,0,0,0.35)",
                      color: "#f0ede8",
                      fontSize: 12,
                    }}
                  />
                </div>
                <textarea
                  value={pBody}
                  onChange={(e) => setPBody(e.target.value)}
                  rows={5}
                  placeholder="Read-only content shared at /portal/<token> (zero OS/tool access granted)…"
                  style={{
                    padding: "8px 11px",
                    borderRadius: 8,
                    border: "1px solid rgba(255,255,255,0.14)",
                    background: "rgba(0,0,0,0.35)",
                    color: "#f0ede8",
                    fontSize: 12,
                  }}
                />
                <button
                  type="submit"
                  style={{
                    padding: "9px 14px",
                    borderRadius: 9,
                    border: `1px solid ${PRIMARY}66`,
                    background: `${PRIMARY}22`,
                    color: PRIMARY,
                    fontFamily: "var(--font-mono)",
                    fontSize: 10,
                    cursor: "pointer",
                  }}
                >
                  CREATE REVOCABLE PORTAL LINK
                </button>

                {latestPortalUrl && (
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
                      padding: "8px 10px",
                      borderRadius: 8,
                      background: "rgba(0,0,0,0.45)",
                      border: `1px solid ${GREEN}55`,
                      fontFamily: "var(--font-mono)",
                      fontSize: 10.5,
                      color: GREEN,
                    }}
                  >
                    <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis" }}>
                      {latestPortalUrl}
                    </span>
                    <button
                      type="button"
                      onClick={() => navigator.clipboard?.writeText(latestPortalUrl)}
                      style={{
                        background: "none",
                        border: "none",
                        color: GREEN,
                        cursor: "pointer",
                      }}
                    >
                      <Copy size={12} />
                    </button>
                  </div>
                )}
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
