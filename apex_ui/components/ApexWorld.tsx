"use client";

import dynamic from "next/dynamic";
import { useEffect, useRef, useState } from "react";
import ApexHeroOrb from "./ApexHeroOrb";
import ReasoningWebJs from "./ReasoningWeb";
import ShaderBackgroundJs from "./ShaderBackground";
import OrbStatusBar from "./OrbStatusBar";
import { useJarvis } from "./JarvisBridge";
import { WorkerOrbsLayer } from "./WorkerOrbsLayer";

const ApexMaleHumanoid = dynamic(() => import("./ApexMaleHumanoid"), {
  ssr: false,
});

export type NodeSel = { name: string; key: string; color: string };

const ReasoningWeb = ReasoningWebJs as unknown as React.ComponentType<{
  state?: string;
  trace?: unknown;
  mode?: string;
  coreless?: boolean;
  persona?: "male" | "female";
  onSelect?: (n: NodeSel) => void;
  light?: boolean;
}>;
const ShaderBackground = ShaderBackgroundJs as unknown as React.ComponentType<{
  opacity?: number;
  voiceActive?: boolean;
  gold?: boolean;
  female?: boolean;
}>;
const OrbStatusBarComp = OrbStatusBar as unknown as React.ComponentType<{
  state?: string;
  rawState?: string;
  level?: number;
  subtitle?: { role: string; text: string } | null;
}>;

type AgentInfo = {
  role: string;
  caps: string[];
  asks?: string[];
  status: "online" | "standby" | "integration";
};

export const ROSTER: { key: string; name: string; color: string }[] = [
  { key: "chief_of_staff", name: "Chief of staff", color: "#00e5ff" },
  { key: "memory", name: "Memory", color: "#00e5ff" },
  { key: "strategist", name: "Strategist", color: "#00e5ff" },
  { key: "researcher", name: "Researcher", color: "#00e5ff" },
  { key: "finance", name: "Finance", color: "#00e5ff" },
  { key: "editor", name: "Editor", color: "#00e5ff" },
  { key: "sales", name: "Sales", color: "#f5a623" },
  { key: "marketing", name: "Marketing", color: "#f5a623" },
  { key: "ops", name: "Ops", color: "#f5a623" },
  { key: "social_media", name: "Social", color: "#f5a623" },
  { key: "engineering", name: "Engineering", color: "#f5a623" },
  { key: "design", name: "Design", color: "#f5a623" },
  { key: "developer", name: "Developer", color: "#f5a623" },
  { key: "analytics", name: "Analytics", color: "#7f9bb3" },
  { key: "crm", name: "CRM", color: "#7f9bb3" },
  { key: "calendar", name: "Calendar", color: "#7f9bb3" },
  { key: "email", name: "Email", color: "#7f9bb3" },
  { key: "drive", name: "Drive", color: "#7f9bb3" },
];

export const INFO: Record<string, AgentInfo> = {
  chief_of_staff: {
    role: "Core orchestrator · Morning Briefing & Focus",
    status: "online",
    caps: [
      "Routes every voice & text command to the right JARVIS tool",
      "Delivers daily morning briefings, weather & top priorities",
      "Focus Guardian deep-work sessions & distraction control",
    ],
    asks: ["Give me my morning briefing", "Start a 25 minute focus session"],
  },
  memory: {
    role: "Long-term memory · Smart Notes & Lectures",
    status: "online",
    caps: [
      "Persistent semantic recall of facts, preferences & past sessions",
      "Smart Notes vault with instant tagging and search",
      "Lecture Capture & structured takeaway extraction",
    ],
    asks: ["What do you remember about me?", "List my recent smart notes"],
  },
  strategist: {
    role: "Autonomous multi-step planner",
    status: "online",
    caps: [
      "Breaks complex goals into verified sequential tool steps",
      "Tracks session context across multi-turn reasoning",
      "Proactive follow-through and undoable execution",
    ],
    asks: ["Plan my priorities for today", "Summarize what we worked on"],
  },
  researcher: {
    role: "Live Web Search & YouTube Intelligence",
    status: "online",
    caps: [
      "Real-time DuckDuckGo & web page extraction",
      "YouTube video search, HUD playback & transcript summaries",
      "Fact-checked synthesis with live sources",
    ],
    asks: ["Search the web for latest AI news", "Summarize this topic for me"],
  },
  finance: {
    role: "Spreadsheets & quantitative analysis",
    status: "online",
    caps: [
      "Generates formatted Excel (.xlsx) workbooks on disk",
      "Budget, pricing & numerical sanity checks",
      "CSV and tabular document inspection",
    ],
    asks: ["Create an Excel expense tracker on my Desktop"],
  },
  editor: {
    role: "Clipboard Intelligence & Document Processor",
    status: "online",
    caps: [
      "Reads, rewrites, translates & cleans clipboard text or code",
      "Processes PDF, DOCX and PPTX documents locally",
      "Drafts crisp emails, summaries and reports",
    ],
    asks: ["Summarize what is on my clipboard", "Polish my clipboard text"],
  },
  sales: {
    role: "Messaging & Phone Relay",
    status: "online",
    caps: [
      "WhatsApp automation & quick message drafting",
      "Encrypted LAN phone dashboard & remote voice relay",
      "Follow-up reminders and contact coordination",
    ],
    asks: ["Open phone remote connection"],
  },
  marketing: {
    role: "Content & Briefing Studio",
    status: "online",
    caps: [
      "Brainstorms hooks, scripts and structured outlines",
      "Combines live web research with local notes",
      "Exports clean drafts straight to files or clipboard",
    ],
    asks: ["Draft a short launch announcement"],
  },
  ops: {
    role: "OS & Device Management",
    status: "online",
    caps: [
      "Opens & closes real desktop apps, PowerShell, Terminal & Explorer",
      "Controls system volume, brightness, Wi-Fi, window snapping & shortcuts",
      "Unforgeable HUD confirmation gate for shutdown & restart",
    ],
    asks: ["Open PowerShell", "What windows are open right now?"],
  },
  social_media: {
    role: "Playwright Browser Automation",
    status: "online",
    caps: [
      "Drives a real browser: navigate, click, type & read pages",
      "Opens websites, dashboards and web apps by voice",
      "Extracts live page state back into conversation",
    ],
    asks: ["Open GitHub in the browser", "Search Google for Three.js docs"],
  },
  engineering: {
    role: "System Doctor & Hardware Telemetry",
    status: "online",
    caps: [
      "Live CPU, RAM, disk, battery, network & NVIDIA GPU diagnostics",
      "Top resource-hog process inspection & health checks",
      "Smart home (Tuya) & 3D printer MQTT hooks",
    ],
    asks: ["Run a full system health check", "How much RAM and CPU am I using?"],
  },
  design: {
    role: "Screen Vision, Camera & Region Capture",
    status: "online",
    caps: [
      "Instant full-screen or rubber-band region vision analysis",
      "Live webcam awareness piped into Gemini Live",
      "Reads UI errors, diagrams and visual layouts on screen",
    ],
    asks: ["What is on my screen right now?"],
  },
  developer: {
    role: "Code Helper & Terminal Execution",
    status: "online",
    caps: [
      "Inspects git status, diffs, branches & project structure",
      "Runs safe shell/Python diagnostics and explains tracebacks",
      "Assists with debugging, refactoring and test runs",
    ],
    asks: ["Check git status of this project", "Help debug clipboard error"],
  },
  analytics: {
    role: "System & Session Telemetry",
    status: "integration",
    caps: [
      "Monitors real-time voice latency, echo guard & model health",
      "Tracks live tool executions across the session",
    ],
    asks: ["Give me a system performance report"],
  },
  crm: {
    role: "Personal Context & Preferences",
    status: "integration",
    caps: [
      "Adapts to your workflow, projects and communication style",
      "Persists custom preferences across restarts",
    ],
  },
  calendar: {
    role: "Google Calendar & Reminders",
    status: "integration",
    caps: [
      "Reads upcoming schedule & creates calendar events",
      "Local desktop timers and reminders",
    ],
    asks: ["Set a reminder in 10 minutes to stretch"],
  },
  email: {
    role: "Gmail Integration",
    status: "integration",
    caps: [
      "Triages unread inbox threads & drafts replies via OAuth",
      "Summarizes important messages on request",
    ],
  },
  drive: {
    role: "File Controller & Local Storage",
    status: "integration",
    caps: [
      "Finds, creates, moves, renames & safely recycles local files",
      "Full undo stack for reversible file & setting actions",
    ],
    asks: ["List files in my Downloads folder"],
  },
};

const STATUS_LINE: Record<AgentInfo["status"], { color: string; text: string }> = {
  online: {
    color: "#34d399",
    text: "Online · JARVIS routes to this capability automatically",
  },
  standby: { color: "#c9a84c", text: "Standby · Available on demand" },
  integration: { color: "#7f9bb3", text: "Integrated · Wired into JARVIS core" },
};

export function AgentOverview({
  sel,
  onClose,
}: {
  sel: NodeSel;
  onClose: () => void;
}) {
  const { sendText, fireLocalTrace } = useJarvis();
  const [pos, setPos] = useState<{ x: number; y: number } | null>(null);
  const dragRef = useRef<{ sx: number; sy: number } | null>(null);
  const info = INFO[sel.key] ?? {
    role: "Specialist",
    status: "online" as const,
    caps: ["Part of the JARVIS core"],
  };
  const c = sel.color;
  const status = STATUS_LINE[info.status];

  useEffect(() => {
    setPos({
      x: Math.max(8, window.innerWidth / 2 - 175),
      y: Math.max(86, window.innerHeight * 0.16),
    });
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const panelRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!pos) return;
    const opener = document.activeElement as HTMLElement | null;
    panelRef.current?.querySelector<HTMLElement>("button")?.focus();
    return () => {
      if (opener && document.contains(opener)) opener.focus();
    };
  }, [pos]);

  const onMouseDown = (e: React.MouseEvent) => {
    if (!pos) return;
    dragRef.current = { sx: e.clientX - pos.x, sy: e.clientY - pos.y };
    const move = (ev: MouseEvent) => {
      if (dragRef.current) {
        setPos({
          x: ev.clientX - dragRef.current.sx,
          y: ev.clientY - dragRef.current.sy,
        });
      }
    };
    const up = () => {
      dragRef.current = null;
      document.removeEventListener("mousemove", move);
      document.removeEventListener("mouseup", up);
    };
    document.addEventListener("mousemove", move);
    document.addEventListener("mouseup", up);
  };

  if (!pos) return null;
  return (
    <div
      ref={panelRef}
      role="dialog"
      aria-modal="true"
      aria-label={`${sel.name} overview`}
      style={{
        position: "fixed",
        left: pos.x,
        top: pos.y,
        width: "min(356px, 92vw)",
        zIndex: 60,
        background: "rgba(4,3,12,0.92)",
        backdropFilter: "blur(24px)",
        border: `1px solid ${c}44`,
        borderRadius: 16,
        boxShadow: `0 0 40px ${c}18, 0 8px 32px rgba(0,0,0,0.6)`,
        overflow: "hidden",
      }}
    >
      <div
        onMouseDown={onMouseDown}
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          padding: "14px 16px",
          borderBottom: `1px solid ${c}22`,
          cursor: "grab",
          userSelect: "none",
          background: `linear-gradient(135deg, ${c}0a 0%, transparent 100%)`,
        }}
      >
        <div
          style={{
            width: 36,
            height: 36,
            borderRadius: "50%",
            background: `${c}14`,
            border: `1px solid ${c}44`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
          }}
        >
          <span
            style={{
              width: 10,
              height: 10,
              borderRadius: "50%",
              background: c,
              boxShadow: `0 0 10px ${c}`,
            }}
          />
        </div>
        <div>
          <div
            style={{
              fontSize: 13,
              fontWeight: 600,
              letterSpacing: "0.08em",
              color: c,
            }}
          >
            {sel.name.toUpperCase()}
          </div>
          <div
            style={{
              fontSize: 10,
              color: "rgba(255,255,255,0.42)",
              letterSpacing: "0.05em",
              textTransform: "uppercase",
            }}
          >
            {info.role}
          </div>
        </div>
        <button
          onClick={onClose}
          aria-label="Close"
          style={{
            marginLeft: "auto",
            background: "none",
            border: "none",
            color: "rgba(255,255,255,0.35)",
            cursor: "pointer",
            fontSize: 18,
            lineHeight: 1,
            padding: "6px 8px",
            transition: "color 0.2s",
          }}
          onMouseEnter={(e) =>
            (e.currentTarget.style.color = "rgba(255,255,255,0.8)")
          }
          onMouseLeave={(e) =>
            (e.currentTarget.style.color = "rgba(255,255,255,0.35)")
          }
        >
          ×
        </button>
      </div>

      <div
        style={{
          padding: "14px 16px",
          display: "flex",
          flexDirection: "column",
          gap: 16,
        }}
      >
        <div>
          <div
            style={{
              fontSize: 9,
              letterSpacing: "0.14em",
              color: `${c}99`,
              marginBottom: 8,
              fontFamily: "var(--font-mono)",
            }}
          >
            WHAT JARVIS HANDLES HERE
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
            {info.caps.map((cap) => (
              <div
                key={cap}
                style={{ display: "flex", alignItems: "flex-start", gap: 7 }}
              >
                <div
                  style={{
                    width: 3,
                    height: 3,
                    borderRadius: "50%",
                    background: `${c}99`,
                    marginTop: 6,
                    flexShrink: 0,
                  }}
                />
                <span
                  style={{
                    fontSize: 11.5,
                    color: "rgba(255,255,255,0.68)",
                    lineHeight: 1.5,
                  }}
                >
                  {cap}
                </span>
              </div>
            ))}
          </div>
        </div>

        {info.asks && info.asks.length > 0 && (
          <div>
            <div
              style={{
                fontSize: 9,
                letterSpacing: "0.14em",
                color: `${c}99`,
                marginBottom: 8,
                fontFamily: "var(--font-mono)",
              }}
            >
              CLICK TO RUN WITH JARVIS
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {info.asks.map((task) => (
                <button
                  key={task}
                  type="button"
                  onClick={() => {
                    fireLocalTrace([sel.key]);
                    sendText(task, sel.key);
                    onClose();
                  }}
                  style={{
                    padding: "5px 11px",
                    background: `${c}12`,
                    border: `1px solid ${c}38`,
                    borderRadius: 20,
                    fontSize: 10.5,
                    color: `${c}ee`,
                    cursor: "pointer",
                    fontFamily: "inherit",
                    transition: "all 0.18s",
                  }}
                >
                  {task} ↗
                </button>
              ))}
            </div>
          </div>
        )}

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 7,
            borderTop: `1px solid ${c}1a`,
            paddingTop: 12,
          }}
        >
          <span
            style={{
              width: 7,
              height: 7,
              borderRadius: "50%",
              background: status.color,
              boxShadow: `0 0 8px ${status.color}`,
            }}
          />
          <span
            style={{
              fontSize: 9.5,
              letterSpacing: "0.08em",
              color: "rgba(255,255,255,0.48)",
              textTransform: "uppercase",
            }}
          >
            {status.text}
          </span>
        </div>
      </div>
    </div>
  );
}

export default function ApexWorld() {
  const {
    activePersona,
    theme,
    orbState,
    rawState,
    lastSubtitle,
    trace,
    tapOrb,
    fireLocalTrace,
  } = useJarvis();
  const [selected, setSelected] = useState<NodeSel | null>(null);
  const [reduced, setReduced] = useState(false);
  const [cam, setCam] = useState({ x: 0, y: 0, zoom: 1, tiltX: 0, tiltY: 0 });
  const [maleWebVisible, setMaleWebVisible] = useState(true);
  const [humanoidPulse, setHumanoidPulse] = useState(0);

  const isMale = activePersona === "male";

  const handleCoreTap = () => {
    if (isMale) {
      setHumanoidPulse((p) => p + 1);
    }
    tapOrb();
  };

  const openAgent = (n: NodeSel) => {
    fireLocalTrace([n.key]);
    setSelected(n);
  };

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const apply = () => setReduced(mq.matches);
    apply();
    mq.addEventListener("change", apply);
    return () => mq.removeEventListener("change", apply);
  }, []);

  // Keyboard 3D World Navigation (WASD / Arrow pan+tilt, +/- zoom, 0/Home reset)
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const el = e.target as HTMLElement | null;
      if (
        el &&
        (el.tagName === "INPUT" ||
          el.tagName === "TEXTAREA" ||
          el.tagName === "SELECT" ||
          el.isContentEditable)
      ) {
        return;
      }
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      switch (e.key) {
        case "ArrowLeft":
        case "a":
        case "A":
          setCam((c) => ({
            ...c,
            x: Math.min(180, c.x + 22),
            tiltY: Math.max(-14, c.tiltY - 2),
          }));
          break;
        case "ArrowRight":
        case "d":
        case "D":
          setCam((c) => ({
            ...c,
            x: Math.max(-180, c.x - 22),
            tiltY: Math.min(14, c.tiltY + 2),
          }));
          break;
        case "ArrowUp":
        case "w":
        case "W":
          setCam((c) => ({
            ...c,
            y: Math.min(140, c.y + 18),
            tiltX: Math.min(12, c.tiltX + 1.8),
          }));
          break;
        case "ArrowDown":
        case "s":
        case "S":
          setCam((c) => ({
            ...c,
            y: Math.max(-140, c.y - 18),
            tiltX: Math.max(-12, c.tiltX - 1.8),
          }));
          break;
        case "+":
        case "=":
          setCam((c) => ({ ...c, zoom: Math.min(1.36, +(c.zoom + 0.08).toFixed(2)) }));
          break;
        case "-":
        case "_":
          setCam((c) => ({ ...c, zoom: Math.max(0.8, +(c.zoom - 0.08).toFixed(2)) }));
          break;
        case "0":
        case "Home":
          setCam({ x: 0, y: 0, zoom: 1, tiltX: 0, tiltY: 0 });
          break;
        default:
          break;
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const camShifted =
    cam.x !== 0 || cam.y !== 0 || cam.zoom !== 1 || cam.tiltX !== 0 || cam.tiltY !== 0;

  const webState =
    orbState === "thinking"
      ? "processing"
      : orbState === "speaking"
      ? "speaking"
      : orbState === "listening"
      ? "listening"
      : "standby";

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        overflow: "hidden",
        userSelect: "none",
      }}
    >
      <div
        aria-hidden="true"
        style={{
          position: "absolute",
          inset: 0,
          background: isMale ? "#02050a" : theme.worldBg,
          transition: "background 0.65s ease",
        }}
      />

      {!reduced && !isMale && (
        <div
          aria-hidden="true"
          style={{ position: "absolute", inset: 0, zIndex: 0 }}
        >
          <ShaderBackground
            opacity={0.14}
            voiceActive={orbState === "speaking"}
            gold={false}
            female={activePersona === "female"}
          />
        </div>
      )}

      <div
        aria-hidden="true"
        style={{
          position: "absolute",
          inset: 0,
          zIndex: 1,
          pointerEvents: "none",
          mixBlendMode: "screen",
          background: isMale
            ? `radial-gradient(circle at 50% 44%, rgba(${theme.orbGlowRgb},${
                orbState === "speaking" ? 0.09 : 0.04
              }) 0%, rgba(8,17,31,0) 56%)`
            : `radial-gradient(circle at 50% 42%, rgba(${
                theme.orbGlowRgb
              },${
                orbState === "speaking" ? 0.3 : orbState === "listening" ? 0.22 : 0.16
              }) 0%, rgba(${theme.orbGlow2Rgb},0.09) 30%, rgba(8,17,31,0) 62%)`,
          transition: "background 0.6s ease",
        }}
      />

      <div
        style={{
          position: "absolute",
          inset: 0,
          zIndex: 2,
          transform: camShifted
            ? `perspective(1200px) translate3d(${cam.x}px, ${cam.y}px, 0) scale(${cam.zoom}) rotateX(${cam.tiltX}deg) rotateY(${cam.tiltY}deg)`
            : undefined,
          transition: "transform 0.28s cubic-bezier(0.22, 1, 0.36, 1)",
          transformStyle: "preserve-3d",
        }}
      >
        {isMale && (
          <div
            style={{
              position: "absolute",
              inset: 0,
              zIndex: 2,
              pointerEvents: "none",
            }}
          >
            <ApexMaleHumanoid
              state={orbState}
              trace={trace}
              reducedMotion={reduced}
              constellationVisible={maleWebVisible}
              onToggleConstellation={() => setMaleWebVisible((v) => !v)}
              pulseSignal={humanoidPulse}
            />
          </div>
        )}

        {(!isMale || maleWebVisible) && (
          <div
            aria-hidden="true"
            style={{
              position: "absolute",
              inset: 0,
              zIndex: isMale ? 1 : undefined,
              opacity: isMale ? 0.72 : undefined,
              pointerEvents: "none",
            }}
          >
            <ReasoningWeb
              key={activePersona}
              persona={activePersona}
              state={webState}
              trace={trace}
              mode="full"
              coreless
              onSelect={(n: NodeSel) => {
                openAgent(n);
              }}
            />
          </div>
        )}

        {!isMale && (
          <div
            style={{
              position: "absolute",
              left: "50%",
              top: "50%",
              width: "min(560px, 58vw)",
              height: "min(500px, 56vw, 70vh)",
              transform: "translate(-50%, -50%)",
              zIndex: 3,
              pointerEvents: "none",
            }}
          >
            <ApexHeroOrb
              state={orbState}
              interactive={false}
              primaryColor={theme.primary}
              primaryBright={theme.primaryBright}
              secondaryColor={theme.secondary}
              secondaryBright={theme.secondaryBright}
            />
          </div>
        )}

        <div
          role="button"
          tabIndex={0}
          aria-label="JARVIS core - tap to interrupt or wake"
          onClick={handleCoreTap}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              handleCoreTap();
            }
          }}
          onMouseDown={(e) => e.preventDefault()}
          style={{
            position: "absolute",
            left: "50%",
            top: isMale ? "46%" : "50%",
            transform: "translate(-50%, -50%)",
            width: isMale ? "min(250px, 26vw)" : "min(340px, 36vw)",
            height: isMale ? "min(310px, 40vh)" : "min(340px, 36vw)",
            borderRadius: "50%",
            zIndex: 4,
            cursor: "pointer",
            background: "transparent",
            border: "none",
            userSelect: "none",
          }}
        />

        <WorkerOrbsLayer />
      </div>

      {camShifted && (
        <button
          type="button"
          onClick={() => setCam({ x: 0, y: 0, zoom: 1, tiltX: 0, tiltY: 0 })}
          style={{
            position: "fixed",
            left: 16,
            bottom: isMale ? 54 : 18,
            zIndex: 35,
            padding: "5px 11px",
            borderRadius: 999,
            border: `1px solid ${theme.primary}44`,
            background: "rgba(5, 11, 22, 0.78)",
            color: theme.primary,
            fontFamily: "var(--font-mono)",
            fontSize: 9.5,
            letterSpacing: "0.1em",
            cursor: "pointer",
          }}
        >
          CAM {Math.round(cam.zoom * 100)}% · PRESS 0 TO RESET
        </button>
      )}

      <nav className="visually-hidden" aria-label="JARVIS agents">
        <ul>
          {ROSTER.map((a) => (
            <li key={a.key}>
              <button
                type="button"
                onClick={() =>
                  openAgent({
                    key: a.key,
                    name: a.name,
                    color:
                      a.color === "#00e5ff"
                        ? theme.primary
                        : a.color === "#f5a623"
                        ? theme.secondary
                        : theme.toolNode,
                  })
                }
              >
                {a.name} - {INFO[a.key]?.role ?? "Specialist"}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      <OrbStatusBarComp
        state={orbState}
        rawState={rawState}
        subtitle={lastSubtitle}
      />

      {selected && (
        <AgentOverview sel={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  );
}
