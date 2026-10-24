"use client";

import React, { useEffect, useRef, useState } from "react";
import { ChevronDown, Maximize2, Mic, MicOff, Send } from "lucide-react";
import { useJarvis, useJarvisAudioLevel } from "./JarvisBridge";

const RED = "#ff5b79";
const GREEN = "#34d399";

export default function BackgroundCornerDock() {
  const {
    activePersona,
    theme,
    assistantName,
    rawState,
    muted,
    paused,
    logs,
    sendText,
    toggleMute,
    tapOrb,
    exitBackgroundMode,
  } = useJarvis();
  const audioLevel = useJarvisAudioLevel();

  const [expanded, setExpanded] = useState(false);
  const [hovered, setHovered] = useState(false);
  const [text, setText] = useState("");
  const inputRef = useRef<HTMLInputElement | null>(null);
  const feedEndRef = useRef<HTMLDivElement | null>(null);

  const isFemale = activePersona === "female";
  const primary = theme.primary;
  const secondary = theme.secondary;

  const st = (rawState || "LISTENING").toUpperCase();
  const isSpeaking = st === "SPEAKING";
  const isThinking = st === "THINKING" || st === "PROCESSING";
  const isMuted = muted || st === "MUTED";

  const activeAccent = isMuted
    ? RED
    : isSpeaking || isThinking
    ? secondary
    : primary;

  const statusLabel = isMuted
    ? "● MIC MUTED"
    : paused
    ? "● PAUSED"
    : isSpeaking
    ? "● SPEAKING · VOICE ACTIVE"
    : isThinking
    ? "● THINKING…"
    : "● LISTENING · VOICE ACTIVE";

  const statusColor = isMuted
    ? RED
    : isSpeaking || isThinking
    ? secondary
    : GREEN;

  useEffect(() => {
    if (expanded) {
      const t = setTimeout(() => {
        inputRef.current?.focus();
      }, 60);
      return () => clearTimeout(t);
    }
  }, [expanded]);

  useEffect(() => {
    if (expanded) {
      feedEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs, expanded]);

  useEffect(() => {
    if (!expanded) return;
    const onKey = (ev: KeyboardEvent) => {
      if (ev.key === "Escape") {
        setExpanded(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [expanded]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed) return;
    sendText(trimmed);
    setText("");
    inputRef.current?.focus();
  };

  const recentLogs = logs.slice(-10);
  const pulseScale = 1 + Math.min(0.28, audioLevel * 0.42);

  if (!expanded) {
    return (
      <div
        data-testid="bg-corner-dock-collapsed"
        style={{
          position: "fixed",
          right: 20,
          bottom: 20,
          zIndex: 1200,
          display: "flex",
          alignItems: "center",
          gap: 10,
          pointerEvents: "auto",
        }}
      >
        {hovered && (
          <div
            style={{
              padding: "6px 12px",
              borderRadius: 999,
              background: isFemale
                ? "rgba(18, 6, 22, 0.90)"
                : "rgba(4, 11, 20, 0.90)",
              border: `1px solid rgba(${theme.orbGlowRgb}, 0.35)`,
              backdropFilter: "blur(14px)",
              color: "#eef3f8",
              fontFamily: "var(--font-mono), monospace",
              fontSize: 10,
              letterSpacing: "0.10em",
              whiteSpace: "nowrap",
              boxShadow: "0 8px 24px rgba(0,0,0,0.45)",
            }}
          >
            <span style={{ color: statusColor }}>●</span>{" "}
            {assistantName.toUpperCase()} · VOICE ACTIVE — CLICK TO TYPE
          </div>
        )}

        <button
          type="button"
          aria-label={`Expand ${assistantName} quick input`}
          title={`${assistantName} running in background (listening & speaking) — Click to expand & type`}
          onClick={() => setExpanded(true)}
          onMouseEnter={() => setHovered(true)}
          onMouseLeave={() => setHovered(false)}
          style={{
            position: "relative",
            width: 62,
            height: 62,
            borderRadius: "50%",
            border: `1.5px solid ${activeAccent}`,
            background: isFemale
              ? "radial-gradient(circle at 38% 34%, rgba(36, 12, 42, 0.96), rgba(10, 4, 14, 0.97))"
              : "radial-gradient(circle at 38% 34%, rgba(8, 22, 38, 0.96), rgba(3, 8, 16, 0.97))",
            boxShadow: `0 10px 30px rgba(0, 0, 0, 0.55), 0 0 ${
              hovered ? 26 : 18
            }px ${activeAccent}55`,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 0,
            transform: hovered ? "scale(1.06)" : "scale(1)",
            transition:
              "transform 170ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 170ms ease, border-color 170ms ease",
          }}
        >
          {/* Rotating subtle orbital ring */}
          <span
            style={{
              position: "absolute",
              inset: 6,
              borderRadius: "50%",
              border: `1.4px dashed ${activeAccent}88`,
              animation: "spin 9s linear infinite",
              pointerEvents: "none",
            }}
          />
          {/* Live audio-reactive glowing core */}
          <span
            style={{
              width: 22,
              height: 22,
              borderRadius: "50%",
              background: `radial-gradient(circle, #ffffff 0%, ${activeAccent} 55%, transparent 100%)`,
              boxShadow: `0 0 16px ${activeAccent}`,
              transform: `scale(${pulseScale.toFixed(3)})`,
              transition: "transform 75ms linear",
              pointerEvents: "none",
            }}
          />
        </button>
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  return (
    <div
      data-testid="bg-corner-dock-expanded"
      style={{
        position: "fixed",
        right: 20,
        bottom: 20,
        width: "min(392px, calc(100vw - 32px))",
        height: 352,
        zIndex: 1200,
        display: "flex",
        flexDirection: "column",
        borderRadius: 22,
        background: isFemale
          ? "linear-gradient(165deg, rgba(18, 7, 24, 0.95), rgba(9, 4, 13, 0.97))"
          : "linear-gradient(165deg, rgba(5, 13, 24, 0.95), rgba(2, 7, 14, 0.97))",
        border: `1px solid rgba(${theme.orbGlowRgb}, 0.38)`,
        boxShadow: `0 22px 54px rgba(0, 0, 0, 0.68), 0 0 32px rgba(${theme.orbGlowRgb}, 0.14)`,
        backdropFilter: "blur(22px)",
        padding: "13px 14px",
        gap: 10,
        pointerEvents: "auto",
        animation: "bgDockExpand 180ms cubic-bezier(0.22, 1, 0.36, 1)",
      }}
    >
      {/* Top Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 9,
        }}
      >
        <button
          type="button"
          onClick={tapOrb}
          title="Tap to interrupt speech or wake"
          style={{
            width: 30,
            height: 30,
            borderRadius: "50%",
            border: `1px solid ${activeAccent}99`,
            background: "rgba(255,255,255,0.03)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            padding: 0,
            flexShrink: 0,
          }}
        >
          <span
            style={{
              width: 12,
              height: 12,
              borderRadius: "50%",
              background: activeAccent,
              boxShadow: `0 0 12px ${activeAccent}`,
              transform: `scale(${pulseScale.toFixed(3)})`,
              transition: "transform 75ms linear",
            }}
          />
        </button>

        <div style={{ flex: 1, minWidth: 0 }}>
          <div
            style={{
              fontFamily: "var(--font-display), sans-serif",
              fontSize: 11,
              fontWeight: 600,
              letterSpacing: "0.20em",
              color: "#f2efe9",
            }}
          >
            {assistantName.toUpperCase()}
          </div>
          <div
            style={{
              fontFamily: "var(--font-mono), monospace",
              fontSize: 9,
              letterSpacing: "0.08em",
              color: statusColor,
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
          >
            {statusLabel}
          </div>
        </div>

        <button
          type="button"
          onClick={toggleMute}
          title={isMuted ? "Unmute microphone" : "Mute microphone"}
          style={miniActionBtnStyle(
            isMuted ? RED : primary,
            isMuted ? "rgba(255, 91, 121, 0.16)" : "rgba(255,255,255,0.04)"
          )}
        >
          {isMuted ? <MicOff size={12} /> : <Mic size={12} />}
        </button>

        <button
          type="button"
          onClick={() => {
            setExpanded(false);
            exitBackgroundMode();
          }}
          title="Restore full 3D JARVIS HUD"
          style={miniActionBtnStyle(primary, "rgba(255,255,255,0.04)")}
        >
          <Maximize2 size={11} />
          <span>FULL</span>
        </button>

        <button
          type="button"
          onClick={() => setExpanded(false)}
          title="Collapse to bottom-right corner button"
          style={miniActionBtnStyle("#cbd5e1", "rgba(255,255,255,0.04)")}
        >
          <ChevronDown size={13} />
        </button>
      </div>

      {/* Live Mini Conversation Feed */}
      <div
        style={{
          flex: 1,
          minHeight: 0,
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
          gap: 6,
          padding: "4px 2px",
        }}
      >
        {recentLogs.length === 0 ? (
          <div
            style={{
              margin: "auto 0",
              textAlign: "center",
              fontFamily: "var(--font-mono), monospace",
              fontSize: 10.5,
              lineHeight: 1.55,
              color: "rgba(226, 234, 245, 0.48)",
              padding: "0 14px",
            }}
          >
            {assistantName} is active in the background — speak anytime or type a
            command below.
          </div>
        ) : (
          recentLogs.map((entry) => {
            const accent =
              entry.role === "user"
                ? primary
                : entry.role === "jarvis"
                ? secondary
                : "#7f9bb3";
            const bg =
              entry.role === "user"
                ? `rgba(${theme.orbGlowRgb}, 0.11)`
                : entry.role === "jarvis"
                ? `rgba(${theme.orbGlow2Rgb}, 0.10)`
                : "rgba(255,255,255,0.035)";
            return (
              <div
                key={entry.id}
                style={{
                  padding: "6px 9px",
                  borderRadius: 10,
                  borderLeft: `2px solid ${accent}`,
                  background: bg,
                  color: "rgba(242, 245, 250, 0.92)",
                  fontSize: 11.5,
                  lineHeight: 1.42,
                  wordBreak: "break-word",
                }}
              >
                {entry.line}
              </div>
            );
          })
        )}
        <div ref={feedEndRef} />
      </div>

      {/* Bottom Quick-Type Input */}
      <form
        onSubmit={handleSubmit}
        style={{
          display: "flex",
          alignItems: "center",
          gap: 7,
        }}
      >
        <input
          ref={inputRef}
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={`Type to ${assistantName}… (voice stays active)`}
          style={{
            flex: 1,
            height: 36,
            borderRadius: 999,
            border: `1px solid rgba(${theme.orbGlowRgb}, 0.34)`,
            background: "rgba(255, 255, 255, 0.055)",
            padding: "0 13px",
            color: "#f5f7fb",
            fontSize: 12,
            outline: "none",
          }}
        />
        <button
          type="submit"
          disabled={!text.trim()}
          title="Send message"
          style={{
            width: 36,
            height: 36,
            borderRadius: "50%",
            border: `1px solid rgba(${theme.orbGlowRgb}, ${
              text.trim() ? 0.65 : 0.22
            })`,
            background: text.trim()
              ? `rgba(${theme.orbGlowRgb}, 0.22)`
              : "rgba(255, 255, 255, 0.03)",
            color: text.trim() ? primary : "rgba(220, 230, 242, 0.35)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: text.trim() ? "pointer" : "default",
            padding: 0,
            flexShrink: 0,
          }}
        >
          <Send size={13} />
        </button>
      </form>

      <style>{`
        @keyframes bgDockExpand {
          from { opacity: 0; transform: translate(12px, 12px) scale(0.88); }
          to { opacity: 1; transform: translate(0, 0) scale(1); }
        }
      `}</style>
    </div>
  );
}

function miniActionBtnStyle(color: string, bg: string): React.CSSProperties {
  return {
    height: 26,
    padding: "0 8px",
    borderRadius: 999,
    border: `1px solid ${color}44`,
    background: bg,
    color,
    fontFamily: "var(--font-mono), monospace",
    fontSize: 9,
    letterSpacing: "0.08em",
    display: "inline-flex",
    alignItems: "center",
    gap: 4,
    cursor: "pointer",
    flexShrink: 0,
  };
}
