"use client";

import React, { useCallback, useEffect, useState } from "react";
import {
  Clock,
  Pause,
  Play,
  Plug,
  RefreshCw,
  Server,
  Trash2,
  X,
  Zap,
} from "lucide-react";
import { useJarvis } from "./JarvisBridge";

type RunRec = {
  id: string;
  ts: string;
  status: string;
  duration_ms: number;
  output: string;
};

type AutoItem = {
  id: string;
  name: string;
  enabled: boolean;
  schedule_type: "interval" | "daily" | "manual";
  every_minutes: number;
  daily_at: string;
  steps: { tool: string; params: Record<string, unknown> }[];
  runs: RunRec[];
};

type RestItem = {
  id: string;
  name: string;
  description: string;
  method: string;
  url: string;
  bearer_token: string;
  body_template: string;
};

type McpItem = {
  id: string;
  name: string;
  transport: "http" | "stdio";
  url: string;
  command: string;
  tools: { name: string; description: string }[];
};

const GREEN = "#3be38a";
const RED = "#ff5d6c";

export default function AutomationsModal() {
  const { automationsModalOpen, setAutomationsModalOpen, theme } = useJarvis();

  const [tab, setTab] = useState<"automations" | "rest" | "mcp">("automations");
  const [autos, setAutos] = useState<AutoItem[]>([]);
  const [rests, setRests] = useState<RestItem[]>([]);
  const [mcps, setMcps] = useState<McpItem[]>([]);
  const [tools, setTools] = useState<string[]>([]);
  const [statusMsg, setStatusMsg] = useState("");
  const [testOutput, setTestOutput] = useState("");

  // Automation form
  const [autoName, setAutoName] = useState("");
  const [schedType, setSchedType] = useState<"interval" | "daily" | "manual">("interval");
  const [everyMins, setEveryMins] = useState(60);
  const [dailyAt, setDailyAt] = useState("09:00");
  const [stepTool, setStepTool] = useState("cloud_integrations");
  const [stepJson, setStepJson] = useState('{"action": "status"}');

  // REST connector form
  const [rName, setRName] = useState("");
  const [rDesc, setRDesc] = useState("");
  const [rMethod, setRMethod] = useState("GET");
  const [rUrl, setRUrl] = useState("");
  const [rToken, setRToken] = useState("");
  const [rBody, setRBody] = useState("");

  // MCP server form
  const [mName, setMName] = useState("");
  const [mTransport, setMTransport] = useState<"http" | "stdio">("http");
  const [mUrl, setMUrl] = useState("");
  const [mCmd, setMCmd] = useState("");

  const applyData = (j: Record<string, unknown>) => {
    if (Array.isArray(j.automations)) setAutos(j.automations as AutoItem[]);
    if (Array.isArray(j.rest_connectors)) setRests(j.rest_connectors as RestItem[]);
    if (Array.isArray(j.mcp_servers)) setMcps(j.mcp_servers as McpItem[]);
    if (Array.isArray(j.available_tools)) setTools(j.available_tools as string[]);
  };

  const refresh = useCallback(async () => {
    try {
      const r = await fetch("/api/hud/automations");
      if (r.ok) applyData(await r.json());
    } catch {}
  }, []);

  useEffect(() => {
    if (automationsModalOpen) {
      refresh();
      setStatusMsg("");
      setTestOutput("");
    }
  }, [automationsModalOpen, refresh]);

  if (!automationsModalOpen) return null;

  const PRIMARY = theme.primary;
  const SECONDARY = theme.secondary;

  const post = async (payload: Record<string, unknown>) => {
    const r = await fetch("/api/hud/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const j = await r.json();
    applyData(j);
    return j;
  };

  const onSaveAuto = async (e: React.FormEvent) => {
    e.preventDefault();
    let parsedParams: Record<string, unknown> = {};
    try {
      parsedParams = stepJson.trim() ? JSON.parse(stepJson) : {};
    } catch {
      setStatusMsg("Step parameters must be valid JSON.");
      return;
    }
    const j = await post({
      action: "auto_save",
      automation: {
        name: autoName,
        schedule_type: schedType,
        every_minutes: everyMins,
        daily_at: dailyAt,
        steps: [{ tool: stepTool, params: parsedParams }],
      },
    });
    if (j.ok) {
      setAutoName("");
      setStatusMsg(`Saved automation "${j.automation?.name}".`);
    } else if (j.error) {
      setStatusMsg(j.error);
    }
  };

  const onSaveRest = async (e: React.FormEvent) => {
    e.preventDefault();
    const j = await post({
      action: "rest_save",
      connector: {
        name: rName,
        description: rDesc,
        method: rMethod,
        url: rUrl,
        bearer_token: rToken,
        body_template: rBody,
      },
    });
    if (j.ok) {
      setRName("");
      setRDesc("");
      setRUrl("");
      setRToken("");
      setRBody("");
      setStatusMsg(`Saved REST connector "${j.connector?.name}".`);
    } else if (j.error) {
      setStatusMsg(j.error);
    }
  };

  const onSaveMcp = async (e: React.FormEvent) => {
    e.preventDefault();
    const j = await post({
      action: "mcp_save",
      server: {
        name: mName,
        transport: mTransport,
        url: mUrl,
        command: mCmd,
      },
    });
    if (j.ok) {
      setMName("");
      setMUrl("");
      setMCmd("");
      setStatusMsg(`Registered MCP server "${j.server?.name}".`);
    } else if (j.error) {
      setStatusMsg(j.error);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Automations, APIs & MCP Center"
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 83,
        background: "rgba(2, 5, 12, 0.78)",
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
          boxShadow: "0 24px 80px rgba(0,0,0,0.82)",
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
            padding: "15px 22px",
            borderBottom: `1px solid ${PRIMARY}26`,
          }}
        >
          <Zap size={17} color={PRIMARY} />
          <div style={{ flex: 1 }}>
            <div
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: 11,
                letterSpacing: "0.24em",
                color: PRIMARY,
              }}
            >
              AUTOMATIONS · CUSTOM REST/WEBHOOKS & MCP BRIDGE
            </div>
            <div style={{ fontSize: 11.5, color: "rgba(240,237,232,0.58)", marginTop: 2 }}>
              Schedule recurring multi-app workflows, build custom REST tools & connect MCP servers.
            </div>
          </div>
          <button
            type="button"
            onClick={() => setAutomationsModalOpen(false)}
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
              { id: "automations", label: `AUTOMATIONS (${autos.length})`, icon: Clock },
              { id: "rest", label: `REST / WEBHOOKS (${rests.length})`, icon: Plug },
              { id: "mcp", label: `MCP SERVERS (${mcps.length})`, icon: Server },
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
          {tab === "automations" && (
            <div style={{ display: "grid", gridTemplateColumns: "1.1fr 1fr", gap: 18 }}>
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {autos.length === 0 ? (
                  <div style={{ fontSize: 12, color: "rgba(240,237,232,0.45)", padding: 20 }}>
                    No recurring automations yet. Create one on the right to run intervals or daily briefings.
                  </div>
                ) : (
                  autos.map((a) => (
                    <div
                      key={a.id}
                      style={{
                        padding: "12px 14px",
                        borderRadius: 12,
                        border: `1px solid ${a.enabled ? `${PRIMARY}44` : "rgba(255,255,255,0.08)"}`,
                        background: "rgba(255,255,255,0.025)",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span style={{ fontWeight: 600, fontSize: 12.5 }}>{a.name}</span>
                        <span
                          style={{
                            fontFamily: "var(--font-mono)",
                            fontSize: 9,
                            color: a.enabled ? GREEN : "rgba(240,237,232,0.48)",
                          }}
                        >
                          {a.schedule_type === "interval"
                            ? `EVERY ${a.every_minutes}M`
                            : a.schedule_type === "daily"
                            ? `DAILY ${a.daily_at}`
                            : "MANUAL"}
                        </span>
                        <span style={{ flex: 1 }} />
                        <button
                          type="button"
                          onClick={async () => {
                            const j = await post({ action: "auto_run_now", id: a.id });
                            if (j.run?.output) setTestOutput(j.run.output);
                          }}
                          title="Run automation immediately"
                          style={{
                            padding: "4px 9px",
                            borderRadius: 999,
                            border: `1px solid ${PRIMARY}66`,
                            background: `${PRIMARY}1f`,
                            color: PRIMARY,
                            fontFamily: "var(--font-mono)",
                            fontSize: 9,
                            cursor: "pointer",
                          }}
                        >
                          RUN NOW
                        </button>
                        <button
                          type="button"
                          onClick={() => post({ action: "auto_toggle", id: a.id })}
                          style={{
                            background: "none",
                            border: "none",
                            color: SECONDARY,
                            cursor: "pointer",
                          }}
                        >
                          {a.enabled ? <Pause size={13} /> : <Play size={13} />}
                        </button>
                        <button
                          type="button"
                          onClick={() => post({ action: "auto_delete", id: a.id })}
                          style={{
                            background: "none",
                            border: "none",
                            color: RED,
                            cursor: "pointer",
                          }}
                        >
                          <Trash2 size={13} />
                        </button>
                      </div>
                      {a.runs && a.runs.length > 0 && (
                        <div
                          style={{
                            fontFamily: "var(--font-mono)",
                            fontSize: 9.5,
                            color: "rgba(240,237,232,0.58)",
                            marginTop: 6,
                          }}
                        >
                          Last run: {a.runs[a.runs.length - 1].ts} ·{" "}
                          {a.runs[a.runs.length - 1].status} ({a.runs[a.runs.length - 1].duration_ms}ms)
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>

              <form
                onSubmit={onSaveAuto}
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
                  + NEW RECURRING AUTOMATION
                </div>
                <input
                  value={autoName}
                  onChange={(e) => setAutoName(e.target.value)}
                  placeholder="Workflow Name (e.g. Morning Inbox & Calendar Sync)"
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
                  <select
                    value={schedType}
                    onChange={(e) =>
                      setSchedType(e.target.value as "interval" | "daily" | "manual")
                    }
                    style={{
                      flex: 1,
                      padding: "8px",
                      borderRadius: 8,
                      border: "1px solid rgba(255,255,255,0.14)",
                      background: "rgba(0,0,0,0.45)",
                      color: "#f0ede8",
                      fontSize: 12,
                    }}
                  >
                    <option value="interval">Every N Minutes</option>
                    <option value="daily">Daily at HH:MM</option>
                    <option value="manual">Manual Trigger Only</option>
                  </select>
                  {schedType === "interval" && (
                    <input
                      type="number"
                      min={1}
                      value={everyMins}
                      onChange={(e) => setEveryMins(Number(e.target.value) || 60)}
                      style={{
                        width: 100,
                        padding: "8px",
                        borderRadius: 8,
                        border: "1px solid rgba(255,255,255,0.14)",
                        background: "rgba(0,0,0,0.35)",
                        color: "#f0ede8",
                        fontSize: 12,
                      }}
                    />
                  )}
                  {schedType === "daily" && (
                    <input
                      type="time"
                      value={dailyAt}
                      onChange={(e) => setDailyAt(e.target.value)}
                      style={{
                        width: 120,
                        padding: "8px",
                        borderRadius: 8,
                        border: "1px solid rgba(255,255,255,0.14)",
                        background: "rgba(0,0,0,0.35)",
                        color: "#f0ede8",
                        fontSize: 12,
                      }}
                    />
                  )}
                </div>
                <select
                  value={stepTool}
                  onChange={(e) => setStepTool(e.target.value)}
                  style={{
                    padding: "8px",
                    borderRadius: 8,
                    border: "1px solid rgba(255,255,255,0.14)",
                    background: "rgba(0,0,0,0.45)",
                    color: "#f0ede8",
                    fontSize: 12,
                  }}
                >
                  {tools.map((t) => (
                    <option key={t} value={t}>
                      Action: {t}
                    </option>
                  ))}
                </select>
                <textarea
                  value={stepJson}
                  onChange={(e) => setStepJson(e.target.value)}
                  rows={4}
                  placeholder='{"action": "email_unread"}'
                  style={{
                    padding: "8px 11px",
                    borderRadius: 8,
                    border: "1px solid rgba(255,255,255,0.14)",
                    background: "rgba(0,0,0,0.35)",
                    color: "#f0ede8",
                    fontFamily: "var(--font-mono)",
                    fontSize: 11.5,
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
                  SAVE AUTOMATION
                </button>
              </form>
            </div>
          )}

          {tab === "rest" && (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {rests.map((c) => (
                  <div
                    key={c.id}
                    style={{
                      padding: "11px 14px",
                      borderRadius: 11,
                      background: "rgba(255,255,255,0.025)",
                      border: "1px solid rgba(255,255,255,0.09)",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span
                        style={{
                          fontFamily: "var(--font-mono)",
                          fontSize: 9,
                          color: SECONDARY,
                        }}
                      >
                        {c.method}
                      </span>
                      <span style={{ fontWeight: 600, fontSize: 12.5, flex: 1 }}>{c.name}</span>
                      <button
                        type="button"
                        onClick={async () => {
                          const j = await post({ action: "rest_test", id: c.id });
                          setTestOutput(j.output || j.error || "");
                        }}
                        style={{
                          padding: "3px 9px",
                          borderRadius: 999,
                          border: `1px solid ${PRIMARY}55`,
                          background: "transparent",
                          color: PRIMARY,
                          fontFamily: "var(--font-mono)",
                          fontSize: 9,
                          cursor: "pointer",
                        }}
                      >
                        TEST
                      </button>
                      <button
                        type="button"
                        onClick={() => post({ action: "rest_delete", id: c.id })}
                        style={{
                          background: "none",
                          border: "none",
                          color: RED,
                          cursor: "pointer",
                        }}
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                    <div style={{ fontSize: 11, color: "rgba(240,237,232,0.58)", marginTop: 4 }}>
                      {c.url}
                    </div>
                  </div>
                ))}
              </div>

              <form
                onSubmit={onSaveRest}
                style={{
                  padding: 15,
                  borderRadius: 14,
                  background: "rgba(255,255,255,0.025)",
                  border: "1px solid rgba(255,255,255,0.09)",
                  display: "flex",
                  flexDirection: "column",
                  gap: 8,
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
                  + CUSTOM REST / WEBHOOK CONNECTOR
                </div>
                <input
                  value={rName}
                  onChange={(e) => setRName(e.target.value)}
                  placeholder="Connector Name (e.g. deploy_webhook)"
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
                  <select
                    value={rMethod}
                    onChange={(e) => setRMethod(e.target.value)}
                    style={{
                      width: 95,
                      padding: "8px",
                      borderRadius: 8,
                      border: "1px solid rgba(255,255,255,0.14)",
                      background: "rgba(0,0,0,0.45)",
                      color: "#f0ede8",
                      fontSize: 12,
                    }}
                  >
                    <option>GET</option>
                    <option>POST</option>
                    <option>PUT</option>
                    <option>DELETE</option>
                  </select>
                  <input
                    value={rUrl}
                    onChange={(e) => setRUrl(e.target.value)}
                    placeholder="https://api.example.com/v1/items?q={{query}}"
                    style={{
                      flex: 1,
                      padding: "8px 11px",
                      borderRadius: 8,
                      border: "1px solid rgba(255,255,255,0.14)",
                      background: "rgba(0,0,0,0.35)",
                      color: "#f0ede8",
                      fontSize: 12,
                    }}
                  />
                </div>
                <input
                  type="password"
                  value={rToken}
                  onChange={(e) => setRToken(e.target.value)}
                  placeholder="Optional Bearer Token"
                  style={{
                    padding: "8px 11px",
                    borderRadius: 8,
                    border: "1px solid rgba(255,255,255,0.14)",
                    background: "rgba(0,0,0,0.35)",
                    color: "#f0ede8",
                    fontSize: 12,
                  }}
                />
                <textarea
                  value={rBody}
                  onChange={(e) => setRBody(e.target.value)}
                  rows={3}
                  placeholder='Optional JSON body template, e.g. {"event": "{{message}}"}'
                  style={{
                    padding: "8px 11px",
                    borderRadius: 8,
                    border: "1px solid rgba(255,255,255,0.14)",
                    background: "rgba(0,0,0,0.35)",
                    color: "#f0ede8",
                    fontFamily: "var(--font-mono)",
                    fontSize: 11.5,
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
                  SAVE REST CONNECTOR
                </button>
              </form>
            </div>
          )}

          {tab === "mcp" && (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {mcps.map((s) => (
                  <div
                    key={s.id}
                    style={{
                      padding: "11px 14px",
                      borderRadius: 11,
                      background: "rgba(255,255,255,0.025)",
                      border: "1px solid rgba(255,255,255,0.09)",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span
                        style={{
                          fontFamily: "var(--font-mono)",
                          fontSize: 9,
                          color: SECONDARY,
                        }}
                      >
                        MCP/{s.transport.toUpperCase()}
                      </span>
                      <span style={{ fontWeight: 600, fontSize: 12.5, flex: 1 }}>{s.name}</span>
                      <button
                        type="button"
                        onClick={() => post({ action: "mcp_discover", id: s.id })}
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: 4,
                          padding: "3px 9px",
                          borderRadius: 999,
                          border: `1px solid ${PRIMARY}55`,
                          background: "transparent",
                          color: PRIMARY,
                          fontFamily: "var(--font-mono)",
                          fontSize: 9,
                          cursor: "pointer",
                        }}
                      >
                        <RefreshCw size={10} /> DISCOVER
                      </button>
                      <button
                        type="button"
                        onClick={() => post({ action: "mcp_delete", id: s.id })}
                        style={{
                          background: "none",
                          border: "none",
                          color: RED,
                          cursor: "pointer",
                        }}
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                    <div style={{ fontSize: 11, color: "rgba(240,237,232,0.58)", marginTop: 4 }}>
                      {s.transport === "http" ? s.url : s.command}
                    </div>
                    {s.tools && s.tools.length > 0 && (
                      <div
                        style={{
                          fontFamily: "var(--font-mono)",
                          fontSize: 9.5,
                          color: GREEN,
                          marginTop: 5,
                        }}
                      >
                        Tools ({s.tools.length}): {s.tools.map((t) => t.name).join(", ")}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <form
                onSubmit={onSaveMcp}
                style={{
                  padding: 15,
                  borderRadius: 14,
                  background: "rgba(255,255,255,0.025)",
                  border: "1px solid rgba(255,255,255,0.09)",
                  display: "flex",
                  flexDirection: "column",
                  gap: 8,
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
                  + REGISTER MCP SERVER (JSON-RPC 2.0)
                </div>
                <input
                  value={mName}
                  onChange={(e) => setMName(e.target.value)}
                  placeholder="Server Name (e.g. filesystem-mcp, composio-mcp)"
                  style={{
                    padding: "8px 11px",
                    borderRadius: 8,
                    border: "1px solid rgba(255,255,255,0.14)",
                    background: "rgba(0,0,0,0.35)",
                    color: "#f0ede8",
                    fontSize: 12,
                  }}
                />
                <select
                  value={mTransport}
                  onChange={(e) => setMTransport(e.target.value === "stdio" ? "stdio" : "http")}
                  style={{
                    padding: "8px",
                    borderRadius: 8,
                    border: "1px solid rgba(255,255,255,0.14)",
                    background: "rgba(0,0,0,0.45)",
                    color: "#f0ede8",
                    fontSize: 12,
                  }}
                >
                  <option value="http">HTTP JSON-RPC Endpoint</option>
                  <option value="stdio">Local Stdio Command</option>
                </select>
                {mTransport === "http" ? (
                  <input
                    value={mUrl}
                    onChange={(e) => setMUrl(e.target.value)}
                    placeholder="https://mcp.example.com/rpc"
                    style={{
                      padding: "8px 11px",
                      borderRadius: 8,
                      border: "1px solid rgba(255,255,255,0.14)",
                      background: "rgba(0,0,0,0.35)",
                      color: "#f0ede8",
                      fontSize: 12,
                    }}
                  />
                ) : (
                  <input
                    value={mCmd}
                    onChange={(e) => setMCmd(e.target.value)}
                    placeholder="npx -y @modelcontextprotocol/server-filesystem /tmp"
                    style={{
                      padding: "8px 11px",
                      borderRadius: 8,
                      border: "1px solid rgba(255,255,255,0.14)",
                      background: "rgba(0,0,0,0.35)",
                      color: "#f0ede8",
                      fontFamily: "var(--font-mono)",
                      fontSize: 11.5,
                    }}
                  />
                )}
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
                  SAVE MCP SERVER
                </button>
              </form>
            </div>
          )}

          {testOutput && (
            <pre
              style={{
                marginTop: 14,
                padding: 12,
                borderRadius: 10,
                background: "rgba(0,0,0,0.45)",
                border: `1px solid ${PRIMARY}33`,
                fontFamily: "var(--font-mono)",
                fontSize: 11,
                whiteSpace: "pre-wrap",
                color: "#f0ede8",
              }}
            >
              {testOutput}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}
