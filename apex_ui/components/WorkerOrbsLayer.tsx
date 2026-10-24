"use client";

import React, { useEffect, useMemo, useState } from "react";
import {
  Activity,
  ChevronDown,
  ChevronRight,
  Plus,
  Square,
  Trash2,
  X,
} from "lucide-react";
import { useJarvis, WorkerItem } from "./JarvisBridge";

const GREEN = "#3be38a";
const RED = "#ff5d6c";

function liveElapsed(w: WorkerItem, nowSec: number): string {
  if (w.status === "completed" || w.status === "failed" || w.status === "cancelled") {
    return `${(w.elapsed_s || 0).toFixed(1)}s`;
  }
  const diff = Math.max(0, nowSec - (w.created_at || nowSec));
  return `${diff.toFixed(1)}s`;
}

/**
 * 3D Orbiting Satellite Worker Orbs rendered inside ApexWorld around the core orb.
 * Automatically adopts Male (Cyan/Gold) or Female (Rose/Orchid) palette.
 */
export function WorkerOrbsLayer() {
  const { workers, theme, cancelWorker } = useJarvis();
  const [angleTick, setAngleTick] = useState(0);
  const [nowSec, setNowSec] = useState(() => Date.now() / 1000);
  const [inspectedId, setInspectedId] = useState<string | null>(null);

  // Show active/pending workers + recently completed workers (< 14s old) in orbit
  const orbitWorkers = useMemo(() => {
    return workers
      .filter((w) => {
        if (w.status === "in_progress" || w.status === "pending") return true;
        return nowSec - (w.updated_at || 0) < 14;
      })
      .slice(0, 8);
  }, [workers, nowSec]);

  useEffect(() => {
    if (orbitWorkers.length === 0) return;
    const id = setInterval(() => {
      setAngleTick((t) => (t + 0.018) % (Math.PI * 2));
      setNowSec(Date.now() / 1000);
    }, 50);
    return () => clearInterval(id);
  }, [orbitWorkers.length]);

  // Also refresh nowSec lightly so recently finished orbs age out cleanly
  useEffect(() => {
    const id = setInterval(() => setNowSec(Date.now() / 1000), 1500);
    return () => clearInterval(id);
  }, []);

  if (orbitWorkers.length === 0) return null;

  const inspected = orbitWorkers.find((w) => w.id === inspectedId) || null;

  return (
    <div
      aria-label="Active worker orbs"
      style={{
        position: "absolute",
        inset: 0,
        zIndex: 5,
        pointerEvents: "none",
      }}
    >
      {/* SVG radial energy tether lines to the central core */}
      <svg
        width="100%"
        height="100%"
        viewBox="-500 -500 1000 1000"
        preserveAspectRatio="xMidYMid meet"
        style={{ position: "absolute", inset: 0, overflow: "visible" }}
      >
        {orbitWorkers.map((w, idx) => {
          const base = (idx / Math.max(1, orbitWorkers.length)) * Math.PI * 2;
          const speed = w.status === "in_progress" ? 1 : 0.35;
          const theta = base + angleTick * speed;
          const rx = 265 + (idx % 2) * 38;
          const ry = 175 + (idx % 2) * 26;
          const x = Math.cos(theta) * rx;
          const y = Math.sin(theta) * ry;
          const color =
            w.status === "failed" || w.status === "cancelled"
              ? RED
              : w.status === "completed"
              ? GREEN
              : idx % 2 === 0
              ? theme.primary
              : theme.secondary;
          return (
            <line
              key={w.id}
              x1={0}
              y1={0}
              x2={x}
              y2={y}
              stroke={color}
              strokeOpacity={w.status === "in_progress" ? 0.38 : 0.18}
              strokeWidth={w.status === "in_progress" ? 1.5 : 1}
              strokeDasharray={w.status === "pending" ? "4 5" : undefined}
            />
          );
        })}
      </svg>

      {/* Orbiting 3D glowing satellite nodes */}
      {orbitWorkers.map((w, idx) => {
        const base = (idx / Math.max(1, orbitWorkers.length)) * Math.PI * 2;
        const speed = w.status === "in_progress" ? 1 : 0.35;
        const theta = base + angleTick * speed;
        const rxPct = 25 + (idx % 2) * 4;
        const ryPct = 24 + (idx % 2) * 3.5;
        const leftPct = 50 + Math.cos(theta) * rxPct;
        const topPct = 50 + Math.sin(theta) * ryPct;
        const depthScale = 0.86 + (Math.sin(theta) + 1) * 0.14;
        const color =
          w.status === "failed" || w.status === "cancelled"
            ? RED
            : w.status === "completed"
            ? GREEN
            : idx % 2 === 0
            ? theme.primary
            : theme.secondary;

        return (
          <button
            key={w.id}
            type="button"
            onClick={() => setInspectedId(inspectedId === w.id ? null : w.id)}
            style={{
              position: "absolute",
              left: `${leftPct}%`,
              top: `${topPct}%`,
              transform: `translate(-50%, -50%) scale(${depthScale.toFixed(3)})`,
              pointerEvents: "auto",
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "6px 11px 6px 7px",
              borderRadius: 999,
              border: `1px solid ${color}77`,
              background: "rgba(5, 11, 22, 0.84)",
              backdropFilter: "blur(12px)",
              boxShadow: `0 0 22px ${color}44`,
              cursor: "pointer",
              color: "#f0ede8",
            }}
          >
            <span
              style={{
                width: 16,
                height: 16,
                borderRadius: "50%",
                background: `radial-gradient(circle at 32% 32%, #ffffff, ${color} 62%, rgba(0,0,0,0.85) 100%)`,
                boxShadow: `0 0 14px ${color}`,
                flexShrink: 0,
              }}
            />
            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: 9.5,
                letterSpacing: "0.08em",
                maxWidth: 150,
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {w.title}
            </span>
            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: 9,
                color,
              }}
            >
              {liveElapsed(w, nowSec)}
            </span>
          </button>
        );
      })}

      {/* Quick Worker Orb Inspector Popover */}
      {inspected && (
        <div
          style={{
            position: "fixed",
            left: "50%",
            bottom: 86,
            transform: "translateX(-50%)",
            width: "min(430px, 92vw)",
            pointerEvents: "auto",
            padding: "13px 16px",
            borderRadius: 14,
            background: theme.drawerBg,
            border: `1px solid ${theme.primary}55`,
            backdropFilter: "blur(22px)",
            boxShadow: "0 16px 48px rgba(0,0,0,0.7)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: 10,
                letterSpacing: "0.14em",
                color: theme.primary,
                flex: 1,
              }}
            >
              WORKER ORB · {inspected.id.toUpperCase()} ({inspected.status.toUpperCase()})
            </span>
            {(inspected.status === "in_progress" || inspected.status === "pending") && (
              <button
                type="button"
                onClick={() => cancelWorker(inspected.id)}
                style={{
                  padding: "3px 9px",
                  borderRadius: 999,
                  border: `1px solid ${RED}66`,
                  background: `${RED}1f`,
                  color: RED,
                  fontFamily: "var(--font-mono)",
                  fontSize: 9,
                  cursor: "pointer",
                }}
              >
                CANCEL
              </button>
            )}
            <button
              type="button"
              onClick={() => setInspectedId(null)}
              style={{
                background: "none",
                border: "none",
                color: "rgba(255,255,255,0.5)",
                cursor: "pointer",
              }}
            >
              <X size={14} />
            </button>
          </div>
          <div style={{ fontSize: 12, color: "#f0ede8", marginTop: 6 }}>
            {inspected.goal}
          </div>
          {inspected.steps.length > 0 && (
            <div
              style={{
                marginTop: 8,
                paddingTop: 8,
                borderTop: "1px solid rgba(255,255,255,0.08)",
                maxHeight: 110,
                overflowY: "auto",
                display: "flex",
                flexDirection: "column",
                gap: 4,
              }}
            >
              {inspected.steps.map((s) => (
                <div
                  key={s.step}
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: 10,
                    color: "rgba(240,237,232,0.72)",
                  }}
                >
                  #{s.step} {s.action} → {s.result}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * Left-side Live Activity Timeline HUD pill + drawer (Running · Queued · Completed).
 */
export function ActivityTimelineHud() {
  const {
    workers,
    activePersona,
    theme,
    activityOpen,
    setActivityOpen,
    spawnWorker,
    cancelWorker,
    clearCompletedWorkers,
  } = useJarvis();

  const [filter, setFilter] = useState<"all" | "running" | "queued" | "done">("all");
  const [goalInput, setGoalInput] = useState("");
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [nowSec, setNowSec] = useState(() => Date.now() / 1000);

  const runningCount = workers.filter((w) => w.status === "in_progress").length;
  const queuedCount = workers.filter((w) => w.status === "pending").length;
  const doneCount = workers.filter(
    (w) => w.status === "completed" || w.status === "failed" || w.status === "cancelled"
  ).length;

  useEffect(() => {
    if (!activityOpen && runningCount === 0) return;
    const id = setInterval(() => setNowSec(Date.now() / 1000), 250);
    return () => clearInterval(id);
  }, [activityOpen, runningCount]);

  const filtered = useMemo(() => {
    return workers.filter((w) => {
      if (filter === "running") return w.status === "in_progress";
      if (filter === "queued") return w.status === "pending";
      if (filter === "done") {
        return w.status === "completed" || w.status === "failed" || w.status === "cancelled";
      }
      return true;
    });
  }, [workers, filter]);

  const PRIMARY = theme.primary;
  const SECONDARY = theme.secondary;

  const onSpawn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goalInput.trim()) return;
    const g = goalInput.trim();
    setGoalInput("");
    await spawnWorker(g);
  };

  const showFloatingActivityPill =
    runningCount > 0 || queuedCount > 0 || activityOpen;

  return (
    <>
      {/* Compact Top-Left Below-Clock Activity Pill */}
      {showFloatingActivityPill && (
        <button
          type="button"
          onClick={() => setActivityOpen((o) => !o)}
          style={{
            position: "fixed",
            top: 124,
            left: 26,
            zIndex: 42,
            display: "inline-flex",
            alignItems: "center",
            gap: 7,
            padding: "5px 11px",
            borderRadius: 999,
            border: `1px solid ${
              runningCount > 0 ? `${PRIMARY}77` : "rgba(255,255,255,0.14)"
            }`,
            background: activityOpen ? `${PRIMARY}22` : theme.barBg,
            backdropFilter: "blur(14px)",
            color: runningCount > 0 || activityOpen ? PRIMARY : "rgba(240,237,232,0.8)",
            fontFamily: "var(--font-mono)",
            fontSize: 9.5,
            letterSpacing: "0.14em",
            cursor: "pointer",
          }}
        >
          <Activity size={12} />
          ACTIVITY
          {runningCount > 0 ? (
            <span style={{ color: GREEN }}>· {runningCount} RUNNING</span>
          ) : workers.length > 0 ? (
            <span style={{ opacity: 0.72 }}>· {workers.length}</span>
          ) : null}
        </button>
      )}

      {activityOpen && (
        <aside
          aria-label="Live worker activity timeline"
          style={{
            position: "fixed",
            top: showFloatingActivityPill ? 160 : 62,
            left: 24,
            width: "min(380px, 92vw)",
            maxHeight: "calc(100vh - 230px)",
            zIndex: 49,
            background: theme.drawerBg,
            border: `1px solid ${PRIMARY}38`,
            borderRadius: 16,
            backdropFilter: "blur(24px)",
            boxShadow: "0 14px 48px rgba(0,0,0,0.68)",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "11px 14px",
              borderBottom: `1px solid ${PRIMARY}22`,
            }}
          >
            <Activity size={13} color={PRIMARY} />
            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: 10,
                letterSpacing: "0.2em",
                color: PRIMARY,
                flex: 1,
              }}
            >
              PARALLEL WORKERS
            </span>
            {doneCount > 0 && (
              <button
                type="button"
                onClick={clearCompletedWorkers}
                title="Clear completed workers"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 4,
                  padding: "3px 8px",
                  borderRadius: 999,
                  border: "1px solid rgba(255,255,255,0.14)",
                  background: "transparent",
                  color: "rgba(240,237,232,0.62)",
                  fontFamily: "var(--font-mono)",
                  fontSize: 8.5,
                  cursor: "pointer",
                }}
              >
                <Trash2 size={10} />
                CLEAR DONE
              </button>
            )}
            <button
              type="button"
              onClick={() => setActivityOpen(false)}
              style={{
                background: "none",
                border: "none",
                color: "rgba(255,255,255,0.48)",
                cursor: "pointer",
              }}
            >
              <X size={15} />
            </button>
          </div>

          {/* Filter Tabs */}
          <div
            style={{
              display: "flex",
              gap: 5,
              padding: "8px 12px",
              borderBottom: "1px solid rgba(255,255,255,0.06)",
            }}
          >
            {(
              [
                { id: "all", label: `ALL (${workers.length})` },
                { id: "running", label: `RUN (${runningCount})` },
                { id: "queued", label: `QUEUE (${queuedCount})` },
                { id: "done", label: `DONE (${doneCount})` },
              ] as const
            ).map((f) => (
              <button
                key={f.id}
                type="button"
                onClick={() => setFilter(f.id)}
                style={{
                  flex: 1,
                  padding: "4px 6px",
                  borderRadius: 999,
                  border: `1px solid ${
                    filter === f.id ? `${PRIMARY}66` : "rgba(255,255,255,0.1)"
                  }`,
                  background: filter === f.id ? `${PRIMARY}1f` : "transparent",
                  color: filter === f.id ? PRIMARY : "rgba(240,237,232,0.6)",
                  fontFamily: "var(--font-mono)",
                  fontSize: 8.5,
                  letterSpacing: "0.08em",
                  cursor: "pointer",
                }}
              >
                {f.label}
              </button>
            ))}
          </div>

          {/* Spawn Worker Bar */}
          <form
            onSubmit={onSpawn}
            style={{
              display: "flex",
              gap: 6,
              padding: "8px 12px",
              borderBottom: "1px solid rgba(255,255,255,0.06)",
            }}
          >
            <input
              type="text"
              value={goalInput}
              onChange={(e) => setGoalInput(e.target.value)}
              placeholder="Spawn parallel worker goal…"
              style={{
                flex: 1,
                padding: "6px 10px",
                borderRadius: 8,
                border: "1px solid rgba(255,255,255,0.14)",
                background: "rgba(0,0,0,0.35)",
                color: "#f0ede8",
                fontSize: 11.5,
                outline: "none",
              }}
            />
            <button
              type="submit"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 4,
                padding: "6px 10px",
                borderRadius: 8,
                border: `1px solid ${SECONDARY}66`,
                background: `${SECONDARY}22`,
                color: SECONDARY,
                fontFamily: "var(--font-mono)",
                fontSize: 9.5,
                cursor: "pointer",
              }}
            >
              <Plus size={11} />
              SPAWN
            </button>
          </form>

          {/* Worker Timeline List */}
          <div
            style={{
              flex: 1,
              overflowY: "auto",
              padding: "10px 12px",
              display: "flex",
              flexDirection: "column",
              gap: 8,
            }}
          >
            {filtered.length === 0 ? (
              <div
                style={{
                  fontSize: 11.5,
                  color: "rgba(240,237,232,0.42)",
                  textAlign: "center",
                  padding: "22px 10px",
                }}
              >
                No workers in this view. Parallel tools and subagents fan out here
                and orbit the core in real time.
              </div>
            ) : (
              filtered.map((w) => {
                const statusColor =
                  w.status === "in_progress"
                    ? PRIMARY
                    : w.status === "pending"
                    ? SECONDARY
                    : w.status === "completed"
                    ? GREEN
                    : RED;
                const open = expandedId === w.id;
                return (
                  <div
                    key={w.id}
                    style={{
                      padding: "9px 11px",
                      borderRadius: 11,
                      background: "rgba(255,255,255,0.025)",
                      border: `1px solid ${statusColor}38`,
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <button
                        type="button"
                        onClick={() => setExpandedId(open ? null : w.id)}
                        style={{
                          background: "none",
                          border: "none",
                          color: statusColor,
                          padding: 0,
                          cursor: "pointer",
                          display: "inline-flex",
                        }}
                      >
                        {open ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
                      </button>
                      <span
                        style={{
                          fontFamily: "var(--font-mono)",
                          fontSize: 9,
                          padding: "1px 6px",
                          borderRadius: 999,
                          background: `${statusColor}22`,
                          color: statusColor,
                          textTransform: "uppercase",
                        }}
                      >
                        {w.status.replace("_", " ")}
                      </span>
                      <span
                        style={{
                          fontSize: 11.5,
                          color: "#f0ede8",
                          flex: 1,
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          whiteSpace: "nowrap",
                        }}
                      >
                        {w.title}
                      </span>
                      <span
                        style={{
                          fontFamily: "var(--font-mono)",
                          fontSize: 9.5,
                          color: "rgba(240,237,232,0.58)",
                        }}
                      >
                        {liveElapsed(w, nowSec)}
                      </span>
                      {(w.status === "in_progress" || w.status === "pending") && (
                        <button
                          type="button"
                          onClick={() => cancelWorker(w.id)}
                          title="Cancel worker"
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            justifyContent: "center",
                            width: 22,
                            height: 22,
                            borderRadius: 6,
                            border: `1px solid ${RED}55`,
                            background: `${RED}1a`,
                            color: RED,
                            cursor: "pointer",
                          }}
                        >
                          <Square size={9} />
                        </button>
                      )}
                    </div>

                    {open && (
                      <div
                        style={{
                          marginTop: 7,
                          paddingTop: 7,
                          borderTop: "1px solid rgba(255,255,255,0.06)",
                          fontSize: 11,
                          color: "rgba(240,237,232,0.75)",
                        }}
                      >
                        <div>{w.goal}</div>
                        {w.steps.map((s) => (
                          <div
                            key={s.step}
                            style={{
                              fontFamily: "var(--font-mono)",
                              fontSize: 10,
                              color: "rgba(240,237,232,0.6)",
                              marginTop: 3,
                            }}
                          >
                            #{s.step} {s.action} → {s.result}
                          </div>
                        ))}
                        {w.result && (
                          <div style={{ color: GREEN, marginTop: 4, fontSize: 10.5 }}>
                            Result: {w.result}
                          </div>
                        )}
                        {w.error && (
                          <div style={{ color: RED, marginTop: 4, fontSize: 10.5 }}>
                            Error: {w.error}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </aside>
      )}
    </>
  );
}
