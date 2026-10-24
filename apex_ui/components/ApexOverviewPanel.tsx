"use client";

import { useEffect, useState } from "react";
import {
  Terminal,
  Sliders,
  Scan,
  Smartphone,
  Mic,
  MicOff,
  Sparkles,
} from "lucide-react";
import { useJarvis } from "./JarvisBridge";

const WCODE: Record<number, string> = {
  0: "Clear",
  1: "Mainly clear",
  2: "Partly cloudy",
  3: "Overcast",
  45: "Fog",
  48: "Fog",
  51: "Drizzle",
  53: "Drizzle",
  55: "Drizzle",
  61: "Rain",
  63: "Rain",
  65: "Heavy rain",
  71: "Snow",
  73: "Snow",
  75: "Snow",
  80: "Showers",
  81: "Showers",
  82: "Showers",
  95: "Storm",
  96: "Storm",
  99: "Storm",
};

function Clock({ compact = false }: { compact?: boolean }) {
  const { assistantName, theme } = useJarvis();
  const ACCENT = theme.primary;
  const [now, setNow] = useState<Date | null>(null);
  const [wx, setWx] = useState<{
    temp: number | null;
    code: number | null;
    city: string;
  } | null>(null);

  useEffect(() => {
    setNow(new Date());
    const id = setInterval(() => setNow(new Date()), 15000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    let ok = true;
    const load = () =>
      fetch("/api/weather")
        .then((r) => (r.ok ? r.json() : null))
        .then((d) => {
          if (ok && d) {
            setWx({
              temp: d.current?.temperature_2m ?? null,
              code: d.current?.weather_code ?? null,
              city: d.city || assistantName,
            });
          }
        })
        .catch(() => {
          if (ok) setWx({ temp: null, code: null, city: assistantName });
        });
    load();
    const id = setInterval(load, 900000);
    return () => {
      ok = false;
      clearInterval(id);
    };
  }, [assistantName]);

  if (!now) return <div style={{ height: compact ? 30 : 48 }} />;
  const time = now.toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
  });
  const date = now.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });

  if (compact) {
    return (
      <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
        <span
          style={{
            fontSize: 18,
            fontWeight: 300,
            letterSpacing: "0.08em",
            color: "rgba(240,237,232,0.82)",
            lineHeight: 1,
          }}
        >
          {time}
        </span>
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: 9,
            letterSpacing: "0.22em",
            color: "rgba(180,215,240,0.48)",
            textTransform: "uppercase",
          }}
        >
          {date}
          {wx?.temp != null ? ` · ${Math.round(wx.temp)}°C` : ""}
        </span>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", alignItems: "flex-end", gap: 26, flexWrap: "wrap" }}>
      <div>
        <div
          style={{
            fontSize: 34,
            fontWeight: 300,
            letterSpacing: "0.04em",
            color: "#f0ede8",
            lineHeight: 1,
            textShadow: `0 0 22px ${ACCENT}44`,
          }}
        >
          {time}
        </div>
        <div
          style={{
            fontSize: 10.5,
            letterSpacing: "0.2em",
            color: "rgba(240,237,232,0.55)",
            marginTop: 4,
            textTransform: "uppercase",
          }}
        >
          {date}
        </div>
      </div>
      {wx && (
        <div>
          <div style={{ fontSize: 22, fontWeight: 300, color: `${ACCENT}ee` }}>
            {wx.temp != null ? Math.round(wx.temp) + "°C" : "ONLINE"}
          </div>
          <div
            style={{
              fontSize: 9.5,
              letterSpacing: "0.12em",
              color: "rgba(240,237,232,0.5)",
              marginTop: 2,
              textTransform: "uppercase",
            }}
          >
            {(wx.city || assistantName).toUpperCase()}
            {wx.city && wx.code != null ? " · " : ""}
            {wx.code != null ? (WCODE[wx.code] || "").toUpperCase() : ""}
          </div>
        </div>
      )}
    </div>
  );
}

export default function ApexOverviewPanel() {
  const [open, setOpen] = useState(false);
  const {
    assistantName,
    activePersona,
    theme,
    muted,
    toggleMute,
    setConsoleOpen,
    setSettingsOpen,
    setPersonaModalOpen,
    captureRegion,
    openRemoteQr,
  } = useJarvis();

  const ACCENT = theme.primary;
  const FIL = open ? 480 : 320;
  const FIL_CAP = "calc(100vw - 260px)";

  const tileStyle: React.CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: 11,
    padding: "10px 14px",
    background: theme.tileBg,
    border: `1px solid ${ACCENT}33`,
    borderRadius: 10,
    cursor: "pointer",
    textAlign: "left",
    backdropFilter: "blur(10px)",
    transition: "all .2s",
    color: "rgba(240,237,232,0.92)",
    width: "100%",
    fontFamily: "inherit",
  };

  const isMale = activePersona === "male";

  return (
    <div className="apex-overview" style={{ pointerEvents: "none" }}>
      {!isMale && (
        <div
          style={{
            position: "absolute",
            top: 14,
            left: 8,
            width: "min(520px, 94vw)",
            height: 240,
            pointerEvents: "none",
            background: `radial-gradient(ellipse 48% 70% at 46% 0%, ${ACCENT}${
              open ? "55" : "28"
            }, ${ACCENT}0a 46%, transparent 72%)`,
            filter: "blur(10px)",
            transition: "all .5s ease",
          }}
        />
      )}

      {isMale ? (
        <div
          onClick={() => setOpen((o) => !o)}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              setOpen((o) => !o);
            }
          }}
          role="button"
          tabIndex={0}
          aria-label="Toggle overview panel"
          aria-expanded={open}
          style={{
            marginLeft: 14,
            marginTop: 10,
            width: "fit-content",
            cursor: "pointer",
            pointerEvents: "auto",
            userSelect: "none",
            display: "flex",
            flexDirection: "column",
            gap: 4,
          }}
        >
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: 9,
              letterSpacing: "0.32em",
              color: open ? ACCENT : "rgba(180,222,248,0.52)",
              transition: "color .3s",
            }}
          >
            {assistantName.toUpperCase()}
          </span>
          <Clock compact />
        </div>
      ) : (
        <div
          onClick={() => setOpen((o) => !o)}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              setOpen((o) => !o);
            }
          }}
          role="button"
          tabIndex={0}
          aria-label="Toggle overview panel"
          aria-expanded={open}
          style={{
            position: "relative",
            height: 40,
            cursor: "pointer",
            pointerEvents: "auto",
            userSelect: "none",
          }}
        >
          <div
            style={{
              position: "absolute",
              top: 14,
              left: 8,
              width: `min(${FIL}px, ${FIL_CAP})`,
              height: 2,
              borderRadius: 2,
              background: theme.filamentLine,
              boxShadow: `0 0 10px ${ACCENT}, 0 0 26px ${ACCENT}${
                open ? ", 0 0 54px " + ACCENT : ""
              }`,
              transition: "all .5s ease",
            }}
          />
          <div
            style={{
              position: "absolute",
              top: 11,
              left: open ? `min(${FIL}px, ${FIL_CAP})` : 6,
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: theme.filamentDot,
              boxShadow: `0 0 10px ${ACCENT}, 0 0 18px ${ACCENT}`,
              transition: "left .5s ease, background .4s ease, box-shadow .4s ease",
              pointerEvents: "none",
            }}
          />
          <span
            style={{
              position: "absolute",
              top: 20,
              left: 10,
              fontFamily: "var(--font-mono)",
              fontSize: 9,
              letterSpacing: "0.34em",
              color: `rgba(${theme.filamentTextRgb},${open ? 0.92 : 0.64})`,
              transition: "color .4s",
            }}
          >
            {assistantName.toUpperCase()} · {activePersona.toUpperCase()} · OVERVIEW
          </span>
        </div>
      )}

      <div
        style={{
          paddingLeft: 14,
          paddingTop: isMale ? 0 : 6,
          width: "fit-content",
          pointerEvents: "auto",
        }}
      >
        {!isMale && <Clock />}

        {open && (
          <div
            style={{
              marginTop: 16,
              width: 268,
              display: "flex",
              flexDirection: "column",
              gap: 8,
            }}
          >
            <button
              type="button"
              style={tileStyle}
              onClick={() => {
                setPersonaModalOpen(true);
                setOpen(false);
              }}
            >
              <span style={{ display: "flex", color: ACCENT }}>
                <Sparkles size={16} />
              </span>
              <span style={{ flex: 1, fontSize: 11.5, letterSpacing: "0.05em" }}>
                Switch Male / Female Edition
              </span>
            </button>

            <button
              type="button"
              style={tileStyle}
              onClick={() => {
                toggleMute();
                setOpen(false);
              }}
            >
              <span style={{ display: "flex", color: muted ? "#ff5b79" : ACCENT }}>
                {muted ? <MicOff size={16} /> : <Mic size={16} />}
              </span>
              <span style={{ flex: 1, fontSize: 11.5, letterSpacing: "0.05em" }}>
                {muted ? "Unmute Microphone" : "Mute Microphone"}
              </span>
            </button>

            <button
              type="button"
              style={tileStyle}
              onClick={() => {
                setConsoleOpen((v) => !v);
                setOpen(false);
              }}
            >
              <span style={{ display: "flex", color: ACCENT }}>
                <Terminal size={16} />
              </span>
              <span style={{ flex: 1, fontSize: 11.5, letterSpacing: "0.05em" }}>
                Live Transcript & Logs
              </span>
            </button>

            <button
              type="button"
              style={tileStyle}
              onClick={() => {
                captureRegion();
                setOpen(false);
              }}
            >
              <span style={{ display: "flex", color: ACCENT }}>
                <Scan size={16} />
              </span>
              <span style={{ flex: 1, fontSize: 11.5, letterSpacing: "0.05em" }}>
                Capture Screen Region
              </span>
            </button>

            <button
              type="button"
              style={tileStyle}
              onClick={() => {
                setSettingsOpen(true);
                setOpen(false);
              }}
            >
              <span style={{ display: "flex", color: ACCENT }}>
                <Sliders size={16} />
              </span>
              <span style={{ flex: 1, fontSize: 11.5, letterSpacing: "0.05em" }}>
                Voice, Audio & HUD Settings
              </span>
            </button>

            <button
              type="button"
              style={tileStyle}
              onClick={() => {
                openRemoteQr();
                setOpen(false);
              }}
            >
              <span style={{ display: "flex", color: ACCENT }}>
                <Smartphone size={16} />
              </span>
              <span style={{ flex: 1, fontSize: 11.5, letterSpacing: "0.05em" }}>
                Connect Phone Remote
              </span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
