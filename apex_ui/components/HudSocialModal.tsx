"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Heart,
  Maximize2,
  Minimize2,
  RefreshCw,
  Send,
  X,
} from "lucide-react";
import { useJarvis } from "./JarvisBridge";

const PLATFORMS = [
  { key: "instagram", short: "IG" },
  { key: "snapchat", short: "SNAP" },
  { key: "tiktok", short: "TIKTOK" },
  { key: "x", short: "X" },
  { key: "whatsapp", short: "WA" },
  { key: "reddit", short: "REDDIT" },
];

const VIEWS = [
  { key: "feed", label: "FEED" },
  { key: "reels", label: "REELS" },
  { key: "inbox", label: "DMs" },
  { key: "notifications", label: "ALERTS" },
];

const GREEN = "#34d399";
const AMBER = "#f5a623";

export default function HudSocialModal() {
  const { socialHud, theme, openSocialHud, closeSocialHud } = useJarvis();

  const [frameB64, setFrameB64] = useState<string>("");
  const [liveUrl, setLiveUrl] = useState<string>("");
  const [isConn, setIsConn] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [frameError, setFrameError] = useState<string>("");
  const [inputBusy, setInputBusy] = useState(false);
  const [sessionHealth, setSessionHealth] = useState("unverified");
  const [errMsg, setErrMsg] = useState<string>("");
  const [quickText, setQuickText] = useState<string>("");
  const [ripple, setRipple] = useState<{ x: number; y: number; id: number } | null>(
    null
  );

  const activeBoostUntilRef = useRef<number>(0);
  const inFlightRef = useRef<boolean>(false);
  const epochRef = useRef(0);
  const inputBusyRef = useRef(false);
  const queueRef = useRef<Promise<unknown>>(Promise.resolve());
  const viewportRef = useRef<HTMLDivElement | null>(null);

  const boostFps = useCallback(() => {
    activeBoostUntilRef.current = Date.now() + 3200;
  }, []);

  const fetchFrame = useCallback(async (plat: string) => {
    if (inFlightRef.current) return;
    inFlightRef.current = true;
    const epoch = epochRef.current;
    try {
      const r = await fetch(
        `/api/hud/social/frame?platform=${encodeURIComponent(plat)}`,
        { cache: "no-store", signal: AbortSignal.timeout(15000) }
      );
      const data = await r.json();
      if (epoch !== epochRef.current) return;
      if (r.ok && data && data.ok && data.image_b64) {
        setFrameB64(data.image_b64);
        if (data.url) setLiveUrl(data.url);
        setIsConn(Boolean(data.connected));
        setSessionHealth(data.session_health || "unverified");
        setFrameError("");
      } else {
        setFrameError(data?.error || "The live frame is unavailable. Use Refresh to reconnect.");
      }
    } catch {
      if (epoch === epochRef.current) setFrameError("The live stream is unavailable. The image may be stale; wait for reconnection.");
    } finally {
      inFlightRef.current = false;
      if (epoch === epochRef.current) setLoading(false);
    }
  }, []);

  useEffect(() => {
    epochRef.current += 1;
    setFrameB64("");
    setLiveUrl("");
    setErrMsg("");
    setFrameError("");
    if (!socialHud || !socialHud.active) {
      setFrameB64("");
      return;
    }
    setLoading(true);
    setIsConn(Boolean(socialHud.connected));
    setSessionHealth(socialHud.session_health || "unverified");
    boostFps();
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | null = null;

    const loop = async () => {
      if (cancelled || !socialHud?.active) return;
      await fetchFrame(socialHud.platform);
      if (cancelled) return;
      const delay = Date.now() < activeBoostUntilRef.current ? 240 : 650;
      timer = setTimeout(loop, delay);
    };
    loop();

    return () => {
      cancelled = true;
      epochRef.current += 1;
      if (timer) clearTimeout(timer);
    };
  }, [socialHud?.active, socialHud?.platform, socialHud?.opened_at, boostFps, fetchFrame]);

  const sendInteract = useCallback(
    (payload: Record<string, unknown>): Promise<boolean> => {
      if (!socialHud) return Promise.resolve(false);
      const epoch = epochRef.current;
      const run = async () => {
        if (epoch !== epochRef.current) return false;
        boostFps();
        try {
          const r = await fetch("/api/hud/social/interact", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            signal: AbortSignal.timeout(20000),
            body: JSON.stringify({ platform: socialHud.platform, layout: socialHud.layout,
                                   opened_at: socialHud.opened_at, ...payload }),
          });
          const data = await r.json();
          if (!r.ok || !data?.ok) throw new Error(data?.error || "HUD interaction failed.");
          if (epoch === epochRef.current) {
            setErrMsg("");
            await fetchFrame(socialHud.platform);
          }
          return true;
        } catch (err) {
          if (epoch === epochRef.current) setErrMsg(
            `${err instanceof Error ? err.message : "HUD interaction failed."} It may have applied; inspect the chat before retrying a send.`
          );
          return false;
        }
      };
      // Preserve click -> focus -> typing -> Enter order, even under latency.
      const task = queueRef.current.then(run, run);
      queueRef.current = task;
      return task;
    },
    [socialHud, boostFps, fetchFrame]
  );

  const insertQuickText = async (submit: boolean) => {
    if (inputBusyRef.current || !quickText) return;
    inputBusyRef.current = true;
    setInputBusy(true);
    const text = quickText;
    try {
      if (await sendInteract({ kind: "type", text, submit })) {
        setQuickText(current => current === text ? "" : current);
      }
    } finally {
      inputBusyRef.current = false;
      setInputBusy(false);
    }
  };

  if (!socialHud || !socialHud.active) return null;

  const PRIMARY = theme.primary;
  const SECONDARY = theme.secondary;
  const isWide = socialHud.layout === "wide";

  const onViewportClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const el = viewportRef.current;
    if (!el || frameError) return;
    el.focus();
    const rect = el.getBoundingClientRect();
    const nx = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const ny = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));
    setRipple({ x: e.clientX - rect.left, y: e.clientY - rect.top, id: Date.now() });
    sendInteract({ kind: "click", nx, ny });
  };

  const onViewportWheel = (e: React.WheelEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (frameError) return;
    sendInteract({
      kind: "wheel",
      deltaX: e.deltaX,
      deltaY: Math.max(-780, Math.min(780, e.deltaY * 1.3)),
    });
  };

  const onViewportKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (frameError || e.metaKey || e.ctrlKey || e.altKey) return;
    if (
      [
        "Enter",
        "Backspace",
        "Tab",
        "Escape",
        "ArrowDown",
        "ArrowUp",
        "ArrowLeft",
        "ArrowRight",
      ].includes(e.key)
    ) {
      e.preventDefault();
      sendInteract({ kind: "key", key: e.key });
      return;
    }
    if (e.key.length === 1) {
      e.preventDefault();
      sendInteract({ kind: "type", text: e.key, submit: false });
    }
  };

  const onQuickSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickText || frameError) return;
    void insertQuickText(true);
  };

  const pillBtn: React.CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 4,
    padding: "4px 8px",
    borderRadius: 999,
    border: `1px solid ${PRIMARY}35`,
    background: "rgba(255,255,255,0.03)",
    color: "rgba(240,237,232,0.88)",
    fontFamily: "var(--font-mono)",
    fontSize: 9.5,
    letterSpacing: "0.08em",
    cursor: "pointer",
  };

  return (
    <div
      data-testid="hud-social-viewport"
      style={{
        position: "fixed",
        right: 20,
        top: 64,
        bottom: 84,
        width: isWide ? "min(860px, calc(100vw - 40px))" : "min(416px, calc(100vw - 32px))",
        zIndex: 88,
        display: "flex",
        flexDirection: "column",
        borderRadius: 18,
        background: "rgba(6, 12, 22, 0.92)",
        backdropFilter: "blur(24px)",
        border: `1px solid ${PRIMARY}55`,
        boxShadow: `0 22px 60px rgba(0,0,0,0.68), 0 0 36px ${PRIMARY}18`,
        overflow: "hidden",
      }}
    >
      {(errMsg || frameError) && (
        <div role="alert" style={{ padding: "9px 12px", background: "#482b18", color: "#ffcc92", fontSize: 12 }}>
          {errMsg || frameError}
        </div>
      )}
      {/* Top Header: Platform + Live Status + Controls */}
      <div
        style={{
          padding: "9px 12px 7px",
          borderBottom: `1px solid ${PRIMARY}26`,
          display: "flex",
          flexDirection: "column",
          gap: 7,
          background: "rgba(255,255,255,0.02)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 8,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
            <span
              title={isConn ? "Live signed-in session" : sessionHealth === "login_required" ? "Sign in inside this HUD" : sessionHealth === "challenge_required" ? "Complete Instagram security verification inside this HUD" : "Session not live-verified yet"}
              style={{
                width: 7,
                height: 7,
                borderRadius: "50%",
                background: isConn ? GREEN : AMBER,
                boxShadow: `0 0 8px ${isConn ? GREEN : AMBER}`,
              }}
            />
            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: 10.5,
                fontWeight: 700,
                letterSpacing: "0.14em",
                color: PRIMARY,
              }}
            >
              {(socialHud.label || socialHud.platform).toUpperCase()} · HUD LIVE
            </span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
            <button
              type="button"
              title="Toggle Compact / Wide HUD View"
              onClick={() =>
                sendInteract({
                  kind: "layout",
                  mode: isWide ? "mobile" : "wide",
                })
              }
              style={pillBtn}
            >
              {isWide ? <Minimize2 size={11} /> : <Maximize2 size={11} />}
              {isWide ? "APP" : "WIDE"}
            </button>
            <button
              type="button"
              title="Pop out to standalone window"
              onClick={() => sendInteract({ kind: "popout" })}
              style={pillBtn}
            >
              <ExternalLink size={11} />
            </button>
            <button
              type="button"
              title="Close HUD panel"
              onClick={() => closeSocialHud()}
              style={{ ...pillBtn, borderColor: "rgba(255,91,121,0.4)", color: "#ff8098" }}
            >
              <X size={12} />
            </button>
          </div>
        </div>

        {/* Platform Switcher + View Tabs + Quick Reel Controls */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 6,
            flexWrap: "wrap",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 4, flexWrap: "wrap" }}>
            {PLATFORMS.map((p) => {
              const active = p.key === socialHud.platform;
              return (
                <button
                  key={p.key}
                  type="button"
                  onClick={async () => {
                    const result = await openSocialHud(p.key, "feed", socialHud.layout);
                    if (!result.ok) setErrMsg(result.error || "Could not open the social HUD.");
                  }}
                  style={{
                    ...pillBtn,
                    padding: "3px 7px",
                    fontSize: 9,
                    borderColor: active ? PRIMARY : "rgba(255,255,255,0.12)",
                    background: active ? `${PRIMARY}26` : "rgba(255,255,255,0.02)",
                    color: active ? "#ffffff" : "rgba(240,237,232,0.65)",
                  }}
                >
                  {p.short}
                </button>
              );
            })}
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
            {VIEWS.map((v) => {
              const active = socialHud.view === v.key;
              return (
                <button
                  key={v.key}
                  type="button"
                  onClick={() => sendInteract({ kind: "navigate", view: v.key })}
                  style={{
                    ...pillBtn,
                    padding: "3px 7px",
                    fontSize: 9,
                    borderColor: active ? SECONDARY : `${SECONDARY}44`,
                    background: active ? `${SECONDARY}24` : "transparent",
                    color: active ? "#ffffff" : SECONDARY,
                  }}
                >
                  {v.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Live Interactive Viewport */}
      <div
        ref={viewportRef}
        tabIndex={0}
        onClick={onViewportClick}
        onWheel={onViewportWheel}
        onKeyDown={onViewportKeyDown}
        style={{
          position: "relative",
          flex: 1,
          minHeight: 0,
          background: "#040811",
          cursor: "pointer",
          outline: "none",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          overflow: "hidden",
          userSelect: "none",
        }}
      >
        {frameB64 ? (
          <img
            src={`data:image/jpeg;base64,${frameB64}`}
            alt={socialHud.label}
            draggable={false}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "fill",
              display: "block",
            }}
          />
        ) : (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 10,
              padding: 24,
              textAlign: "center",
              color: "rgba(240,237,232,0.75)",
              fontFamily: "var(--font-mono)",
              fontSize: 11,
            }}
          >
            <RefreshCw size={18} style={{ color: PRIMARY }} />
            <div>
              {(errMsg || frameError)
                ? (errMsg || frameError)
                : loading
                ? `Connecting live ${socialHud.label} stream inside HUD…`
                : `Preparing ${socialHud.label}…`}
            </div>
          </div>
        )}

        {/* Click Feedback Ripple */}
        {ripple && (
          <span
            key={ripple.id}
            style={{
              position: "absolute",
              left: ripple.x - 12,
              top: ripple.y - 12,
              width: 24,
              height: 24,
              borderRadius: "50%",
              border: `2px solid ${PRIMARY}`,
              background: `${PRIMARY}33`,
              pointerEvents: "none",
              opacity: 0.75,
            }}
          />
        )}

        {/* Floating Quick Reel / Feed Overlay Controls */}
        <div
          onClick={(e) => e.stopPropagation()}
          style={{
            position: "absolute",
            right: 8,
            bottom: 10,
            display: "flex",
            flexDirection: "column",
            gap: 5,
          }}
        >
          <button
            type="button"
            title="Previous Reel / Scroll Up"
            onClick={() => sendInteract({ kind: "navigate", view: "previous" })}
            style={{ ...pillBtn, padding: 6, background: "rgba(6,12,22,0.82)" }}
          >
            <ChevronUp size={13} />
          </button>
          <button
            type="button"
            title="Next Reel / Scroll Down"
            onClick={() => sendInteract({ kind: "navigate", view: "next" })}
            style={{ ...pillBtn, padding: 6, background: "rgba(6,12,22,0.82)" }}
          >
            <ChevronDown size={13} />
          </button>
          <button
            type="button"
            title="Like Active Post / Reel"
            onClick={() => sendInteract({ kind: "navigate", view: "like" })}
            style={{
              ...pillBtn,
              padding: 6,
              background: "rgba(6,12,22,0.82)",
              color: "#ff5b79",
              borderColor: "rgba(255,91,121,0.45)",
            }}
          >
            <Heart size={13} />
          </button>
        </div>
      </div>

      {/* Bottom Quick-Type / DM / Search / Login Bar */}
      <form
        onSubmit={onQuickSend}
        style={{
          display: "flex",
          alignItems: "center",
          gap: 6,
          padding: "8px 10px",
          borderTop: `1px solid ${PRIMARY}26`,
          background: "rgba(255,255,255,0.025)",
        }}
      >
        <input
          type="text"
          value={quickText}
          onChange={(e) => setQuickText(e.target.value)}
          placeholder={
            liveUrl.toLowerCase().includes("login")
              ? "Click field above, then type username / password / 2FA…"
              : "Click input above or type DM / @search & press Enter…"
          }
          style={{
            flex: 1,
            background: "rgba(0,0,0,0.35)",
            color: "#f0ede8",
            border: `1px solid ${PRIMARY}38`,
            borderRadius: 999,
            padding: "6px 11px",
            fontSize: 11,
            fontFamily: "var(--font-mono)",
            outline: "none",
          }}
        />
        <button
          type="button"
          title="Insert text without pressing Enter"
          disabled={inputBusy || Boolean(frameError)}
          onClick={() => void insertQuickText(false)}
          style={{ ...pillBtn, padding: "6px 9px" }}
        >
          TYPE
        </button>
        <button
          type="submit"
          disabled={inputBusy || Boolean(frameError) || !quickText}
          title="Type & press Enter / Send"
          style={{
            ...pillBtn,
            padding: "6px 10px",
            background: `${PRIMARY}28`,
            borderColor: PRIMARY,
            color: "#ffffff",
          }}
        >
          <Send size={11} />
        </button>
      </form>
    </div>
  );
}
