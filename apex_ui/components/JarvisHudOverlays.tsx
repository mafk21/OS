"use client";

import React, { useEffect, useRef, useState } from "react";
import {
  Mic,
  MicOff,
  Pause,
  Play,
  Send,
  Sliders,
  Square,
  Terminal,
  Scan,
  ShieldAlert,
  KeyRound,
  X,
} from "lucide-react";
import { useJarvis } from "./JarvisBridge";

const CYAN = "#00e5ff";
const GOLD = "#f5a623";
const RED = "#ff5b79";
const GREEN = "#34d399";

export default function JarvisHudOverlays() {
  const {
    connected,
    assistantName,
    orbState,
    rawState,
    muted,
    paused,
    offline,
    offlineReason,
    voice,
    voices,
    bargeEnabled,
    gracePeriod,
    inputs,
    outputs,
    currentInput,
    currentOutput,
    logs,
    confirm,
    content,
    consoleOpen,
    settingsOpen,
    setupOpen,
    setConsoleOpen,
    setSettingsOpen,
    setSetupOpen,
    clearContent,
    sendText,
    toggleMute,
    togglePause,
    interrupt,
    stopAll,
    captureRegion,
    setVoice,
    setDevices,
    setBarge,
    setGrace,
    resolveConfirm,
    saveApiKey,
  } = useJarvis();

  const [cmd, setCmd] = useState("");
  const [apiKeyInput, setApiKeyInput] = useState("");
  const [savingKey, setSavingKey] = useState(false);
  const [keyError, setKeyError] = useState("");
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (consoleOpen) {
      logEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs, consoleOpen]);

  const onSubmitCmd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!cmd.trim()) return;
    sendText(cmd);
    setCmd("");
  };

  const onSaveKey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (apiKeyInput.trim().length < 15) {
      setKeyError("Please enter a valid Gemini API key.");
      return;
    }
    setSavingKey(true);
    setKeyError("");
    const ok = await saveApiKey(apiKeyInput);
    setSavingKey(false);
    if (!ok) {
      setKeyError("Could not save API key — check that JARVIS is running.");
    } else {
      setApiKeyInput("");
    }
  };

  const pillBase: React.CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    gap: 7,
    fontFamily: "var(--font-mono)",
    fontSize: "0.64rem",
    letterSpacing: "0.18em",
    textTransform: "uppercase",
    color: "rgba(240,237,232,0.82)",
    border: "1px solid rgba(240,237,232,0.18)",
    borderRadius: 20,
    padding: "7px 13px",
    background: "rgba(4,8,15,0.62)",
    backdropFilter: "blur(10px)",
    cursor: "pointer",
    transition: "all 0.2s",
  };

  const dotColor = offline
    ? GOLD
    : muted
    ? RED
    : paused
    ? GOLD
    : orbState === "speaking"
    ? GOLD
    : connected
    ? GREEN
    : CYAN;

  const statusText = offline
    ? `OFFLINE${offlineReason ? ` · ${offlineReason}` : ""}`
    : muted
    ? "MIC MUTED"
    : paused
    ? "PAUSED"
    : connected
    ? rawState || "ONLINE"
    : "PREVIEW";

  return (
    <>
      {/* ── Top-Right HUD Controls ── */}
      <div
        style={{
          position: "fixed",
          top: 14,
          right: "clamp(14px, 2.4vw, 32px)",
          zIndex: 42,
          display: "flex",
          alignItems: "center",
          gap: 8,
          flexWrap: "wrap",
          justifyContent: "flex-end",
        }}
      >
        <button
          type="button"
          onClick={toggleMute}
          title={muted ? "Click to unmute microphone" : "Click to mute microphone"}
          style={{
            ...pillBase,
            borderColor: muted ? `${RED}55` : `${dotColor}44`,
          }}
        >
          <span
            style={{
              width: 7,
              height: 7,
              borderRadius: "50%",
              background: dotColor,
              boxShadow: `0 0 8px ${dotColor}`,
            }}
          />
          {statusText}
        </button>

        <button
          type="button"
          onClick={() => setConsoleOpen((o) => !o)}
          style={{
            ...pillBase,
            borderColor: consoleOpen ? `${CYAN}66` : "rgba(240,237,232,0.18)",
            color: consoleOpen ? CYAN : "rgba(240,237,232,0.82)",
          }}
        >
          <Terminal size={13} />
          CONSOLE{logs.length > 0 ? ` (${logs.length})` : ""}
        </button>

        <button
          type="button"
          onClick={() => setSettingsOpen(true)}
          aria-label="Open JARVIS settings"
          style={pillBase}
        >
          <Sliders size={13} />
          HUD
        </button>
      </div>

      {/* ── Unforgeable Confirmation Banner (core/confirm.py) ── */}
      {confirm && (
        <div
          role="alertdialog"
          aria-label="Action confirmation required"
          style={{
            position: "fixed",
            top: 66,
            left: "50%",
            transform: "translateX(-50%)",
            width: "min(520px, 92vw)",
            zIndex: 85,
            background: "rgba(12, 8, 4, 0.94)",
            border: `1px solid ${GOLD}88`,
            borderRadius: 14,
            padding: "14px 18px",
            boxShadow: `0 0 36px ${GOLD}2e, 0 12px 36px rgba(0,0,0,0.75)`,
            backdropFilter: "blur(20px)",
            display: "flex",
            alignItems: "center",
            gap: 14,
          }}
        >
          <ShieldAlert size={22} style={{ color: GOLD, flexShrink: 0 }} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: 11,
                letterSpacing: "0.14em",
                color: GOLD,
                textTransform: "uppercase",
              }}
            >
              CONFIRMATION REQUIRED · {confirm.title}
            </div>
            {confirm.detail && (
              <div
                style={{
                  fontSize: 12,
                  color: "rgba(240,237,232,0.78)",
                  marginTop: 3,
                }}
              >
                {confirm.detail}
              </div>
            )}
          </div>
          <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
            <button
              type="button"
              onClick={() => resolveConfirm(false)}
              style={{
                ...pillBase,
                padding: "7px 12px",
                borderColor: "rgba(255,255,255,0.22)",
              }}
            >
              CANCEL
            </button>
            <button
              type="button"
              onClick={() => resolveConfirm(true)}
              style={{
                ...pillBase,
                padding: "7px 14px",
                background: `${GOLD}26`,
                borderColor: GOLD,
                color: "#ffe4a3",
              }}
            >
              CONFIRM
            </button>
          </div>
        </div>
      )}

      {/* ── Rich Content Card (show_content from tools/skills) ── */}
      {content && (
        <div
          role="dialog"
          aria-label={content.title || "JARVIS output"}
          style={{
            position: "fixed",
            left: 20,
            bottom: 72,
            width: "min(440px, 92vw)",
            maxHeight: "52vh",
            zIndex: 55,
            background: "rgba(4, 9, 18, 0.9)",
            border: `1px solid ${CYAN}3a`,
            borderRadius: 14,
            backdropFilter: "blur(22px)",
            boxShadow: `0 0 32px ${CYAN}18, 0 10px 30px rgba(0,0,0,0.65)`,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              padding: "10px 14px",
              borderBottom: `1px solid ${CYAN}22`,
            }}
          >
            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: 10.5,
                letterSpacing: "0.16em",
                color: CYAN,
                textTransform: "uppercase",
                flex: 1,
              }}
            >
              {content.title || assistantName}
            </span>
            <button
              type="button"
              onClick={clearContent}
              aria-label="Close content card"
              style={{
                background: "none",
                border: "none",
                color: "rgba(255,255,255,0.45)",
                cursor: "pointer",
                padding: 2,
              }}
            >
              <X size={15} />
            </button>
          </div>
          <pre
            style={{
              margin: 0,
              padding: "12px 14px",
              overflowY: "auto",
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
              fontFamily: "inherit",
              fontSize: 12,
              lineHeight: 1.55,
              color: "rgba(240,237,232,0.85)",
            }}
          >
            {content.text}
          </pre>
        </div>
      )}

      {/* ── Collapsible Right-Side Live Console Drawer ── */}
      {consoleOpen && (
        <aside
          aria-label="JARVIS live transcript console"
          style={{
            position: "fixed",
            top: 56,
            right: 16,
            bottom: 68,
            width: "min(390px, 92vw)",
            zIndex: 50,
            background: "rgba(4, 9, 18, 0.88)",
            border: `1px solid ${CYAN}33`,
            borderRadius: 16,
            backdropFilter: "blur(24px)",
            boxShadow: "0 12px 44px rgba(0,0,0,0.65)",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              padding: "12px 16px",
              borderBottom: `1px solid ${CYAN}20`,
            }}
          >
            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: 10,
                letterSpacing: "0.24em",
                color: CYAN,
                flex: 1,
              }}
            >
              {assistantName.toUpperCase()} · LIVE STREAM
            </span>
            <button
              type="button"
              onClick={() => setConsoleOpen(false)}
              aria-label="Close console"
              style={{
                background: "none",
                border: "none",
                color: "rgba(255,255,255,0.45)",
                cursor: "pointer",
              }}
            >
              <X size={16} />
            </button>
          </div>

          <div
            style={{
              flex: 1,
              overflowY: "auto",
              padding: "12px 14px",
              display: "flex",
              flexDirection: "column",
              gap: 8,
            }}
          >
            {logs.length === 0 ? (
              <div
                style={{
                  fontSize: 11.5,
                  color: "rgba(240,237,232,0.4)",
                  textAlign: "center",
                  marginTop: 32,
                }}
              >
                Speak naturally or type below — live transcripts and tool actions
                appear here.
              </div>
            ) : (
              logs.map((entry) => {
                const accent =
                  entry.role === "user"
                    ? CYAN
                    : entry.role === "jarvis"
                    ? GOLD
                    : "rgba(160,185,205,0.65)";
                return (
                  <div
                    key={entry.id}
                    style={{
                      padding: "8px 11px",
                      borderRadius: 10,
                      background:
                        entry.role === "user"
                          ? "rgba(0,229,255,0.06)"
                          : entry.role === "jarvis"
                          ? "rgba(245,166,35,0.07)"
                          : "rgba(255,255,255,0.03)",
                      borderLeft: `2px solid ${accent}`,
                      fontSize: 12,
                      lineHeight: 1.5,
                      color:
                        entry.role === "sys"
                          ? "rgba(200,215,228,0.68)"
                          : "rgba(240,237,232,0.92)",
                      wordBreak: "break-word",
                    }}
                  >
                    {entry.line}
                  </div>
                );
              })
            )}
            <div ref={logEndRef} />
          </div>
        </aside>
      )}

      {/* ── Bottom Slim Glass Command Bar ── */}
      <form
        onSubmit={onSubmitCmd}
        style={{
          position: "fixed",
          left: "50%",
          bottom: 12,
          transform: "translateX(-50%)",
          width: "min(620px, 94vw)",
          zIndex: 40,
          display: "flex",
          alignItems: "center",
          gap: 6,
          padding: "5px 8px",
          borderRadius: 999,
          background: "rgba(4, 10, 20, 0.74)",
          border: `1px solid rgba(0, 229, 255, 0.24)`,
          backdropFilter: "blur(16px)",
          boxShadow: "0 8px 28px rgba(0,0,0,0.5)",
        }}
      >
        <button
          type="button"
          onClick={toggleMute}
          title={muted ? "Unmute microphone" : "Mute microphone"}
          style={{
            width: 32,
            height: 32,
            borderRadius: "50%",
            border: `1px solid ${muted ? `${RED}66` : `${CYAN}44`}`,
            background: muted ? `${RED}1f` : `${CYAN}14`,
            color: muted ? RED : CYAN,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            flexShrink: 0,
          }}
        >
          {muted ? <MicOff size={15} /> : <Mic size={15} />}
        </button>

        <button
          type="button"
          onClick={togglePause}
          title={paused ? "Resume listening" : "Pause listening"}
          style={{
            width: 32,
            height: 32,
            borderRadius: "50%",
            border: `1px solid ${paused ? `${GOLD}66` : "rgba(255,255,255,0.14)"}`,
            background: paused ? `${GOLD}22` : "transparent",
            color: paused ? GOLD : "rgba(240,237,232,0.7)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            flexShrink: 0,
          }}
        >
          {paused ? <Play size={14} /> : <Pause size={14} />}
        </button>

        <input
          type="text"
          value={cmd}
          onChange={(e) => setCmd(e.target.value)}
          placeholder={`Message ${assistantName}, or speak naturally…`}
          aria-label={`Command input for ${assistantName}`}
          style={{
            flex: 1,
            minWidth: 0,
            background: "transparent",
            border: "none",
            outline: "none",
            color: "#f0ede8",
            fontSize: 12.5,
            padding: "6px 8px",
            fontFamily: "inherit",
          }}
        />

        {orbState === "speaking" && (
          <button
            type="button"
            onClick={interrupt}
            title="Interrupt speech"
            style={{
              height: 30,
              padding: "0 11px",
              borderRadius: 999,
              border: `1px solid ${GOLD}66`,
              background: `${GOLD}22`,
              color: GOLD,
              fontFamily: "var(--font-mono)",
              fontSize: 10,
              letterSpacing: "0.12em",
              display: "flex",
              alignItems: "center",
              gap: 5,
              cursor: "pointer",
              flexShrink: 0,
            }}
          >
            <Square size={11} />
            STOP
          </button>
        )}

        <button
          type="button"
          onClick={captureRegion}
          title="Capture screen region for vision"
          style={{
            width: 32,
            height: 32,
            borderRadius: "50%",
            border: "1px solid rgba(255,255,255,0.14)",
            background: "transparent",
            color: "rgba(240,237,232,0.72)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            flexShrink: 0,
          }}
        >
          <Scan size={14} />
        </button>

        <button
          type="submit"
          title="Send command"
          style={{
            width: 32,
            height: 32,
            borderRadius: "50%",
            border: `1px solid ${CYAN}55`,
            background: `${CYAN}1c`,
            color: CYAN,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            flexShrink: 0,
          }}
        >
          <Send size={14} />
        </button>
      </form>

      {/* ── Settings Modal (Voice, Mic/Speaker, Barge-In, API Key) ── */}
      {settingsOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="JARVIS HUD Settings"
          onClick={() => setSettingsOpen(false)}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 75,
            background: "rgba(2, 6, 12, 0.72)",
            backdropFilter: "blur(10px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 16,
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              width: "min(440px, 94vw)",
              background: "rgba(5, 11, 22, 0.96)",
              border: `1px solid ${CYAN}40`,
              borderRadius: 18,
              padding: "20px 22px",
              boxShadow: `0 0 44px ${CYAN}1c, 0 16px 48px rgba(0,0,0,0.8)`,
              display: "flex",
              flexDirection: "column",
              gap: 16,
            }}
          >
            <div style={{ display: "flex", alignItems: "center" }}>
              <span
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: 11,
                  letterSpacing: "0.24em",
                  color: CYAN,
                  flex: 1,
                }}
              >
                {assistantName.toUpperCase()} · SYSTEM CONTROLS
              </span>
              <button
                type="button"
                onClick={() => setSettingsOpen(false)}
                style={{
                  background: "none",
                  border: "none",
                  color: "rgba(255,255,255,0.5)",
                  cursor: "pointer",
                }}
              >
                <X size={18} />
              </button>
            </div>

            {/* Voice selector */}
            <div>
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: 9.5,
                  letterSpacing: "0.16em",
                  color: "rgba(240,237,232,0.55)",
                  marginBottom: 8,
                }}
              >
                ASSISTANT VOICE
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {voices.map((v) => (
                  <button
                    key={v}
                    type="button"
                    onClick={() => setVoice(v)}
                    style={{
                      padding: "6px 12px",
                      borderRadius: 16,
                      border: `1px solid ${
                        voice === v ? CYAN : "rgba(255,255,255,0.15)"
                      }`,
                      background: voice === v ? `${CYAN}22` : "transparent",
                      color: voice === v ? CYAN : "rgba(240,237,232,0.75)",
                      fontSize: 11.5,
                      cursor: "pointer",
                    }}
                  >
                    {v}
                  </button>
                ))}
              </div>
            </div>

            {/* Microphone & Speaker pickers */}
            <div style={{ display: "grid", gap: 10 }}>
              <label style={{ display: "grid", gap: 5 }}>
                <span
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: 9.5,
                    letterSpacing: "0.16em",
                    color: "rgba(240,237,232,0.55)",
                  }}
                >
                  MICROPHONE INPUT
                </span>
                <select
                  value={currentInput}
                  onChange={(e) => setDevices(e.target.value, currentOutput)}
                  style={{
                    background: "rgba(10, 20, 36, 0.9)",
                    color: "#f0ede8",
                    border: "1px solid rgba(0,229,255,0.28)",
                    borderRadius: 8,
                    padding: "8px 10px",
                    fontSize: 12,
                  }}
                >
                  <option value="">System default</option>
                  {inputs
                    .filter((n) => n && n !== "System default")
                    .map((n) => (
                      <option key={n} value={n}>
                        {n}
                      </option>
                    ))}
                </select>
              </label>

              <label style={{ display: "grid", gap: 5 }}>
                <span
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: 9.5,
                    letterSpacing: "0.16em",
                    color: "rgba(240,237,232,0.55)",
                  }}
                >
                  SPEAKER OUTPUT
                </span>
                <select
                  value={currentOutput}
                  onChange={(e) => setDevices(currentInput, e.target.value)}
                  style={{
                    background: "rgba(10, 20, 36, 0.9)",
                    color: "#f0ede8",
                    border: "1px solid rgba(0,229,255,0.28)",
                    borderRadius: 8,
                    padding: "8px 10px",
                    fontSize: 12,
                  }}
                >
                  <option value="">System default</option>
                  {outputs
                    .filter((n) => n && n !== "System default")
                    .map((n) => (
                      <option key={n} value={n}>
                        {n}
                      </option>
                    ))}
                </select>
              </label>
            </div>

            {/* Barge-in & Grace period */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 12,
              }}
            >
              <button
                type="button"
                onClick={() => setBarge(!bargeEnabled)}
                style={{
                  ...pillBase,
                  borderColor: bargeEnabled ? `${GREEN}66` : "rgba(255,255,255,0.2)",
                  color: bargeEnabled ? GREEN : "rgba(240,237,232,0.65)",
                }}
              >
                BARGE-IN: {bargeEnabled ? "ON" : "OFF"}
              </button>

              <label
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  fontFamily: "var(--font-mono)",
                  fontSize: 10,
                  color: "rgba(240,237,232,0.65)",
                }}
              >
                GRACE (S)
                <input
                  type="number"
                  min={2}
                  max={30}
                  value={gracePeriod}
                  onChange={(e) => setGrace(Number(e.target.value) || 8)}
                  style={{
                    width: 54,
                    background: "rgba(10,20,36,0.9)",
                    color: "#f0ede8",
                    border: "1px solid rgba(0,229,255,0.28)",
                    borderRadius: 6,
                    padding: "5px 7px",
                    fontSize: 12,
                  }}
                />
              </label>
            </div>

            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                gap: 8,
                paddingTop: 6,
                borderTop: "1px solid rgba(255,255,255,0.08)",
              }}
            >
              <button
                type="button"
                onClick={() => {
                  setSettingsOpen(false);
                  setSetupOpen(true);
                }}
                style={pillBase}
              >
                <KeyRound size={12} />
                API KEY
              </button>

              <button
                type="button"
                onClick={() => {
                  stopAll();
                  setSettingsOpen(false);
                }}
                style={{
                  ...pillBase,
                  borderColor: `${RED}66`,
                  color: RED,
                }}
              >
                <Square size={11} />
                EMERGENCY STOP
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── First-Boot / Reconfigure Gemini API Key Modal ── */}
      {setupOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Configure Gemini API Key"
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 90,
            background: "rgba(2, 6, 12, 0.84)",
            backdropFilter: "blur(14px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 16,
          }}
        >
          <form
            onSubmit={onSaveKey}
            style={{
              width: "min(420px, 94vw)",
              background: "rgba(5, 11, 22, 0.97)",
              border: `1px solid ${CYAN}55`,
              borderRadius: 18,
              padding: "24px 24px",
              boxShadow: `0 0 50px ${CYAN}24, 0 18px 50px rgba(0,0,0,0.85)`,
              display: "flex",
              flexDirection: "column",
              gap: 14,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <KeyRound size={18} style={{ color: CYAN }} />
              <span
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: 11.5,
                  letterSpacing: "0.22em",
                  color: CYAN,
                  flex: 1,
                }}
              >
                INITIALIZE {assistantName.toUpperCase()}
              </span>
              <button
                type="button"
                onClick={() => setSetupOpen(false)}
                style={{
                  background: "none",
                  border: "none",
                  color: "rgba(255,255,255,0.45)",
                  cursor: "pointer",
                }}
              >
                <X size={17} />
              </button>
            </div>

            <div
              style={{
                fontSize: 12,
                lineHeight: 1.55,
                color: "rgba(240,237,232,0.72)",
              }}
            >
              Enter your Google Gemini API key to activate real-time voice,
              vision, and autonomous tools. Stored locally in{" "}
              <code>config/api_keys.json</code>.
            </div>

            <input
              type="password"
              value={apiKeyInput}
              onChange={(e) => setApiKeyInput(e.target.value)}
              placeholder="AIzaSy..."
              autoFocus
              style={{
                background: "rgba(10, 20, 36, 0.92)",
                color: "#f0ede8",
                border: `1px solid ${CYAN}44`,
                borderRadius: 10,
                padding: "10px 12px",
                fontSize: 13,
                outline: "none",
                fontFamily: "var(--font-mono)",
              }}
            />

            {keyError && (
              <div style={{ fontSize: 11.5, color: RED }}>{keyError}</div>
            )}

            <button
              type="submit"
              disabled={savingKey}
              style={{
                ...pillBase,
                justifyContent: "center",
                padding: "10px 16px",
                background: `${CYAN}24`,
                borderColor: CYAN,
                color: "#dffbff",
                fontWeight: 600,
              }}
            >
              {savingKey ? "SAVING..." : "ACTIVATE JARVIS"}
            </button>
          </form>
        </div>
      )}
    </>
  );
}
