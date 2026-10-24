"use client";

import React, { useEffect, useRef, useState } from "react";
import { Activity, Mic, MicOff, Send, Square } from "lucide-react";
import { useJarvis } from "./JarvisBridge";

const GREEN = "#3be38a";
const RED = "#ff5d6c";

/**
 * Standalone Dual-Monitor Console & Parallel Activity Deck (`/?view=console`).
 * Syncs in real time with the main 3D Orb window over `/ws/hud` and respects
 * both Male (Cyan/Gold) and Female (Rose/Orchid) interface themes.
 */
export default function DualMonitorConsole() {
  const {
    connected,
    assistantName,
    activePersona,
    theme,
    logs,
    workers,
    muted,
    toggleMute,
    sendText,
    cancelWorker,
  } = useJarvis();

  const [cmd, setCmd] = useState("");
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs.length]);

  const PRIMARY = theme.primary;
  const SECONDARY = theme.secondary;

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!cmd.trim()) return;
    sendText(cmd);
    setCmd("");
  };

  return (
    <main
      style={{
        height: "100vh",
        background: theme.pageBg,
        color: "#f0ede8",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <header
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          padding: "12px 18px",
          borderBottom: `1px solid ${PRIMARY}33`,
          background: theme.drawerBg,
        }}
      >
        <span
          style={{
            width: 8,
            height: 8,
            borderRadius: "50%",
            background: connected ? GREEN : RED,
            boxShadow: `0 0 10px ${connected ? GREEN : RED}`,
          }}
        />
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: 11,
            letterSpacing: "0.22em",
            color: PRIMARY,
            flex: 1,
          }}
        >
          {assistantName.toUpperCase()} · DUAL-MONITOR CONSOLE ({activePersona.toUpperCase()})
        </span>
      </header>

      {/* Main Split: Live Transcript + Active Parallel Workers */}
      <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
        <section
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "16px 18px",
            display: "flex",
            flexDirection: "column",
            gap: 9,
          }}
        >
          {logs.map((entry) => {
            const accent =
              entry.role === "user"
                ? PRIMARY
                : entry.role === "jarvis"
                ? SECONDARY
                : "rgba(160,185,205,0.65)";
            return (
              <div
                key={entry.id}
                style={{
                  padding: "10px 13px",
                  borderRadius: 10,
                  background:
                    entry.role === "user"
                      ? theme.primarySoftBg
                      : entry.role === "jarvis"
                      ? theme.secondarySoftBg
                      : "rgba(255,255,255,0.03)",
                  borderLeft: `2px solid ${accent}`,
                  fontSize: 12.5,
                  lineHeight: 1.55,
                }}
              >
                {entry.line}
              </div>
            );
          })}
          <div ref={endRef} />
        </section>

        <aside
          style={{
            width: "min(300px, 38vw)",
            borderLeft: `1px solid ${PRIMARY}24`,
            padding: "14px",
            overflowY: "auto",
            background: "rgba(0,0,0,0.22)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              fontFamily: "var(--font-mono)",
              fontSize: 10,
              letterSpacing: "0.16em",
              color: SECONDARY,
              marginBottom: 10,
            }}
          >
            <Activity size={12} />
            LIVE WORKERS ({workers.length})
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {workers.map((w) => (
              <div
                key={w.id}
                style={{
                  padding: "8px 10px",
                  borderRadius: 9,
                  border: `1px solid ${PRIMARY}2a`,
                  background: "rgba(255,255,255,0.025)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span
                    style={{
                      fontFamily: "var(--font-mono)",
                      fontSize: 8.5,
                      color: w.status === "in_progress" ? PRIMARY : GREEN,
                      textTransform: "uppercase",
                    }}
                  >
                    {w.status}
                  </span>
                  <span style={{ flex: 1 }} />
                  {(w.status === "in_progress" || w.status === "pending") && (
                    <button
                      type="button"
                      onClick={() => cancelWorker(w.id)}
                      style={{
                        background: "none",
                        border: "none",
                        color: RED,
                        cursor: "pointer",
                      }}
                    >
                      <Square size={10} />
                    </button>
                  )}
                </div>
                <div style={{ fontSize: 11.5, marginTop: 4 }}>{w.title}</div>
              </div>
            ))}
          </div>
        </aside>
      </div>

      {/* Bottom Command Bar */}
      <form
        onSubmit={onSubmit}
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: "12px 18px",
          borderTop: `1px solid ${PRIMARY}28`,
          background: theme.barBg,
        }}
      >
        <button
          type="button"
          onClick={toggleMute}
          style={{
            width: 34,
            height: 34,
            borderRadius: "50%",
            border: `1px solid ${muted ? RED : PRIMARY}66`,
            background: "transparent",
            color: muted ? RED : PRIMARY,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
          }}
        >
          {muted ? <MicOff size={15} /> : <Mic size={15} />}
        </button>
        <input
          type="text"
          value={cmd}
          onChange={(e) => setCmd(e.target.value)}
          placeholder={`Message ${assistantName} from secondary monitor…`}
          style={{
            flex: 1,
            padding: "9px 14px",
            borderRadius: 999,
            border: `1px solid ${PRIMARY}44`,
            background: "rgba(0,0,0,0.35)",
            color: "#f0ede8",
            fontSize: 13,
            outline: "none",
          }}
        />
        <button
          type="submit"
          style={{
            padding: "9px 16px",
            borderRadius: 999,
            border: `1px solid ${PRIMARY}66`,
            background: `${PRIMARY}22`,
            color: PRIMARY,
            fontFamily: "var(--font-mono)",
            fontSize: 10,
            cursor: "pointer",
            display: "inline-flex",
            alignItems: "center",
            gap: 5,
          }}
        >
          <Send size={12} />
          SEND
        </button>
      </form>
    </main>
  );
}
