"use client";

import React, { useCallback, useEffect, useState } from "react";
import {
  Code2,
  FileCode,
  Folder,
  FolderTree,
  GitCompare,
  Play,
  RefreshCw,
  Square,
  TerminalSquare,
  X,
} from "lucide-react";
import { TerminalSession, useJarvis } from "./JarvisBridge";

type TreeEntry = {
  path: string;
  name: string;
  type: "dir" | "file";
  depth: number;
  size: number;
};

type DiffFile = {
  path: string;
  status: string;
  additions: number;
  deletions: number;
  patch: string;
};

const GREEN = "#3be38a";
const RED = "#ff5d6c";

export default function DevWorkspaceModal() {
  const {
    devModalOpen,
    setDevModalOpen,
    terminalSessions,
    setTerminalSessions,
    theme,
  } = useJarvis();

  const [tab, setTab] = useState<"terminal" | "tree" | "diffs">("terminal");
  const [rootDir, setRootDir] = useState("");
  const [cmdInput, setCmdInput] = useState("");
  const [stdinInput, setStdinInput] = useState("");
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);

  const [treeEntries, setTreeEntries] = useState<TreeEntry[]>([]);
  const [treeFilter, setTreeFilter] = useState("");
  const [activeFilePath, setActiveFilePath] = useState("");
  const [activeFileContent, setActiveFileContent] = useState("");

  const [diffFiles, setDiffFiles] = useState<DiffFile[]>([]);
  const [activeDiff, setActiveDiff] = useState<DiffFile | null>(null);

  const refresh = useCallback(async () => {
    try {
      const q = rootDir.trim()
        ? `?root_dir=${encodeURIComponent(rootDir.trim())}`
        : "";
      const r = await fetch(`/api/hud/dev${q}`);
      if (!r.ok) return;
      const j = await r.json();
      if (Array.isArray(j.sessions)) {
        setTerminalSessions(j.sessions as TerminalSession[]);
      }
      if (j.tree?.entries) {
        setTreeEntries(j.tree.entries);
        if (!rootDir && j.tree.root) setRootDir(j.tree.root);
      }
      if (j.diffs?.files) {
        setDiffFiles(j.diffs.files);
        setActiveDiff((prev) => prev || j.diffs.files[0] || null);
      }
    } catch {}
  }, [rootDir, setTerminalSessions]);

  useEffect(() => {
    if (devModalOpen) refresh();
  }, [devModalOpen, refresh]);

  if (!devModalOpen) return null;

  const PRIMARY = theme.primary;
  const SECONDARY = theme.secondary;

  const activeSession: TerminalSession | null =
    terminalSessions.find((s) => s.id === selectedSessionId) ||
    terminalSessions[0] ||
    null;

  const onRunCmd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!cmdInput.trim()) return;
    const cmd = cmdInput.trim();
    setCmdInput("");
    const r = await fetch("/api/hud/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "dev_run", command: cmd, cwd: rootDir }),
    });
    const j = await r.json();
    if (j.session) {
      setSelectedSessionId(j.session.id);
      if (Array.isArray(j.sessions)) setTerminalSessions(j.sessions);
    }
  };

  const onStopSession = async (sid: string) => {
    await fetch("/api/hud/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "dev_stop", session_id: sid }),
    });
  };

  const onSendStdin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeSession || !stdinInput) return;
    const txt = stdinInput;
    setStdinInput("");
    await fetch("/api/hud/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "dev_stdin",
        session_id: activeSession.id,
        text: txt,
      }),
    });
  };

  const openFile = async (relPath: string) => {
    setActiveFilePath(relPath);
    const r = await fetch("/api/hud/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "dev_read_file",
        root_dir: rootDir,
        path: relPath,
      }),
    });
    const j = await r.json();
    if (j.file) setActiveFileContent(j.file.content || "");
  };

  const filteredTree = treeFilter.trim()
    ? treeEntries.filter((e) =>
        e.path.toLowerCase().includes(treeFilter.toLowerCase())
      )
    : treeEntries;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Live Dev Terminal, Codebase Map & Diffs"
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 84,
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
          width: "min(1040px, 96vw)",
          height: "min(760px, 91vh)",
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
            padding: "14px 20px",
            borderBottom: `1px solid ${PRIMARY}26`,
          }}
        >
          <Code2 size={17} color={PRIMARY} />
          <div style={{ flex: 1 }}>
            <div
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: 11,
                letterSpacing: "0.24em",
                color: PRIMARY,
              }}
            >
              DEV WORKSPACE · LIVE STREAMING TERMINAL, CODEBASE MAP & DIFFS
            </div>
            <div
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: 10,
                color: "rgba(240,237,232,0.5)",
                marginTop: 2,
              }}
            >
              Root: {rootDir || "."}
            </div>
          </div>
          <button
            type="button"
            onClick={refresh}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 5,
              padding: "5px 11px",
              borderRadius: 999,
              border: `1px solid ${PRIMARY}44`,
              background: "transparent",
              color: PRIMARY,
              fontFamily: "var(--font-mono)",
              fontSize: 9.5,
              cursor: "pointer",
            }}
          >
            <RefreshCw size={11} /> REFRESH
          </button>
          <button
            type="button"
            onClick={() => setDevModalOpen(false)}
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
            padding: "10px 20px",
            borderBottom: "1px solid rgba(255,255,255,0.07)",
          }}
        >
          {(
            [
              {
                id: "terminal",
                label: `LIVE TERMINAL (${terminalSessions.length})`,
                icon: TerminalSquare,
              },
              {
                id: "tree",
                label: `CODEBASE MAP (${treeEntries.length})`,
                icon: FolderTree,
              },
              {
                id: "diffs",
                label: `COLORIZED DIFFS (${diffFiles.length})`,
                icon: GitCompare,
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
        </div>

        {/* Body */}
        <div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
          {tab === "terminal" && (
            <div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column", padding: "14px 20px", gap: 10 }}>
              <form onSubmit={onRunCmd} style={{ display: "flex", gap: 8 }}>
                <input
                  value={cmdInput}
                  onChange={(e) => setCmdInput(e.target.value)}
                  placeholder="Run streaming shell command (e.g. pytest -v, git status, npm run build)…"
                  style={{
                    flex: 1,
                    padding: "9px 13px",
                    borderRadius: 9,
                    border: `1px solid ${PRIMARY}44`,
                    background: "rgba(0,0,0,0.45)",
                    color: "#f0ede8",
                    fontFamily: "var(--font-mono)",
                    fontSize: 12,
                    outline: "none",
                  }}
                />
                <button
                  type="submit"
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 5,
                    padding: "9px 16px",
                    borderRadius: 9,
                    border: `1px solid ${PRIMARY}77`,
                    background: `${PRIMARY}22`,
                    color: PRIMARY,
                    fontFamily: "var(--font-mono)",
                    fontSize: 10,
                    cursor: "pointer",
                  }}
                >
                  <Play size={12} /> RUN
                </button>
              </form>

              <div style={{ flex: 1, minHeight: 0, display: "grid", gridTemplateColumns: "240px 1fr", gap: 12 }}>
                <div style={{ overflowY: "auto", display: "flex", flexDirection: "column", gap: 6 }}>
                  {terminalSessions.map((s) => {
                    const sel = activeSession?.id === s.id;
                    const col =
                      s.status === "running"
                        ? PRIMARY
                        : s.status === "completed"
                        ? GREEN
                        : RED;
                    return (
                      <div
                        key={s.id}
                        onClick={() => setSelectedSessionId(s.id)}
                        style={{
                          padding: "8px 10px",
                          borderRadius: 9,
                          border: `1px solid ${sel ? PRIMARY : "rgba(255,255,255,0.09)"}`,
                          background: sel ? `${PRIMARY}14` : "rgba(255,255,255,0.025)",
                          cursor: "pointer",
                        }}
                      >
                        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                          <span style={{ fontFamily: "var(--font-mono)", fontSize: 9, color: col }}>
                            {s.status.toUpperCase()}
                          </span>
                          <span style={{ flex: 1 }} />
                          {s.status === "running" && (
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation();
                                onStopSession(s.id);
                              }}
                              style={{
                                background: "none",
                                border: "none",
                                color: RED,
                                cursor: "pointer",
                              }}
                            >
                              <Square size={11} />
                            </button>
                          )}
                        </div>
                        <div
                          style={{
                            fontFamily: "var(--font-mono)",
                            fontSize: 10.5,
                            marginTop: 3,
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            whiteSpace: "nowrap",
                          }}
                        >
                          $ {s.command}
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    borderRadius: 12,
                    border: "1px solid rgba(255,255,255,0.1)",
                    background: "rgba(0,0,0,0.58)",
                    overflow: "hidden",
                  }}
                >
                  <pre
                    style={{
                      flex: 1,
                      margin: 0,
                      padding: 14,
                      overflowY: "auto",
                      fontFamily: "var(--font-mono)",
                      fontSize: 11.5,
                      lineHeight: 1.55,
                      color: "#e6edf3",
                      whiteSpace: "pre-wrap",
                    }}
                  >
                    {activeSession
                      ? activeSession.output || "Waiting for output…"
                      : "Run a command above (or invoke shell_agent by voice) to stream live stdout/stderr here."}
                  </pre>
                  {activeSession?.status === "running" && (
                    <form
                      onSubmit={onSendStdin}
                      style={{
                        display: "flex",
                        gap: 8,
                        padding: 8,
                        borderTop: "1px solid rgba(255,255,255,0.08)",
                      }}
                    >
                      <input
                        value={stdinInput}
                        onChange={(e) => setStdinInput(e.target.value)}
                        placeholder="Send stdin line to running process…"
                        style={{
                          flex: 1,
                          padding: "6px 10px",
                          borderRadius: 6,
                          border: "1px solid rgba(255,255,255,0.14)",
                          background: "rgba(0,0,0,0.45)",
                          color: "#f0ede8",
                          fontFamily: "var(--font-mono)",
                          fontSize: 11.5,
                        }}
                      />
                      <button
                        type="button"
                        onClick={() => onStopSession(activeSession.id)}
                        style={{
                          padding: "6px 12px",
                          borderRadius: 6,
                          border: `1px solid ${RED}66`,
                          background: `${RED}1f`,
                          color: RED,
                          fontFamily: "var(--font-mono)",
                          fontSize: 9.5,
                          cursor: "pointer",
                        }}
                      >
                        STOP
                      </button>
                    </form>
                  )}
                </div>
              </div>
            </div>
          )}

          {tab === "tree" && (
            <div style={{ flex: 1, minHeight: 0, display: "grid", gridTemplateColumns: "310px 1fr" }}>
              <div
                style={{
                  borderRight: "1px solid rgba(255,255,255,0.08)",
                  padding: 12,
                  overflowY: "auto",
                  display: "flex",
                  flexDirection: "column",
                  gap: 6,
                }}
              >
                <input
                  value={treeFilter}
                  onChange={(e) => setTreeFilter(e.target.value)}
                  placeholder="Filter files…"
                  style={{
                    padding: "7px 10px",
                    borderRadius: 8,
                    border: "1px solid rgba(255,255,255,0.14)",
                    background: "rgba(0,0,0,0.35)",
                    color: "#f0ede8",
                    fontSize: 11.5,
                  }}
                />
                {filteredTree.map((e) => (
                  <button
                    key={e.path}
                    type="button"
                    onClick={() => e.type === "file" && openFile(e.path)}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 6,
                      padding: "4px 8px",
                      paddingLeft: 8 + e.depth * 12,
                      borderRadius: 6,
                      border: "none",
                      background:
                        activeFilePath === e.path ? `${PRIMARY}22` : "transparent",
                      color:
                        e.type === "dir"
                          ? SECONDARY
                          : activeFilePath === e.path
                          ? PRIMARY
                          : "rgba(240,237,232,0.82)",
                      fontFamily: "var(--font-mono)",
                      fontSize: 11,
                      textAlign: "left",
                      cursor: e.type === "file" ? "pointer" : "default",
                    }}
                  >
                    {e.type === "dir" ? <Folder size={12} /> : <FileCode size={12} />}
                    <span
                      style={{
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {e.name}
                    </span>
                  </button>
                ))}
              </div>
              <pre
                style={{
                  margin: 0,
                  padding: 16,
                  overflowY: "auto",
                  background: "rgba(0,0,0,0.48)",
                  fontFamily: "var(--font-mono)",
                  fontSize: 11.5,
                  lineHeight: 1.55,
                  color: "#e6edf3",
                  whiteSpace: "pre-wrap",
                }}
              >
                {activeFilePath
                  ? `// ${activeFilePath}\n\n${activeFileContent}`
                  : "Select any file in the Codebase Map on the left to inspect its source."}
              </pre>
            </div>
          )}

          {tab === "diffs" && (
            <div style={{ flex: 1, minHeight: 0, display: "grid", gridTemplateColumns: "300px 1fr" }}>
              <div
                style={{
                  borderRight: "1px solid rgba(255,255,255,0.08)",
                  padding: 12,
                  overflowY: "auto",
                  display: "flex",
                  flexDirection: "column",
                  gap: 6,
                }}
              >
                {diffFiles.length === 0 ? (
                  <div style={{ fontSize: 11.5, color: "rgba(240,237,232,0.45)", padding: 14 }}>
                    Working tree clean — no uncommitted file changes.
                  </div>
                ) : (
                  diffFiles.map((df) => (
                    <button
                      key={df.path}
                      type="button"
                      onClick={() => setActiveDiff(df)}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                        padding: "8px 10px",
                        borderRadius: 8,
                        border: `1px solid ${
                          activeDiff?.path === df.path
                            ? PRIMARY
                            : "rgba(255,255,255,0.08)"
                        }`,
                        background:
                          activeDiff?.path === df.path
                            ? `${PRIMARY}18`
                            : "rgba(255,255,255,0.02)",
                        color: "#f0ede8",
                        fontFamily: "var(--font-mono)",
                        fontSize: 11,
                        textAlign: "left",
                        cursor: "pointer",
                      }}
                    >
                      <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis" }}>
                        {df.path}
                      </span>
                      <span style={{ color: GREEN, fontSize: 10 }}>+{df.additions}</span>
                      <span style={{ color: RED, fontSize: 10 }}>-{df.deletions}</span>
                    </button>
                  ))
                )}
              </div>

              <div
                style={{
                  overflowY: "auto",
                  padding: 14,
                  background: "rgba(0,0,0,0.52)",
                  fontFamily: "var(--font-mono)",
                  fontSize: 11.5,
                  lineHeight: 1.55,
                }}
              >
                {activeDiff ? (
                  (activeDiff.patch || "").split("\n").map((ln, idx) => {
                    const isAdd = ln.startsWith("+") && !ln.startsWith("+++");
                    const isDel = ln.startsWith("-") && !ln.startsWith("---");
                    const isHunk = ln.startsWith("@@");
                    return (
                      <div
                        key={idx}
                        style={{
                          padding: "1px 8px",
                          background: isAdd
                            ? "rgba(59, 227, 138, 0.13)"
                            : isDel
                            ? "rgba(255, 93, 108, 0.14)"
                            : isHunk
                            ? `${PRIMARY}14`
                            : "transparent",
                          color: isAdd
                            ? GREEN
                            : isDel
                            ? RED
                            : isHunk
                            ? PRIMARY
                            : "rgba(230,237,243,0.85)",
                          whiteSpace: "pre-wrap",
                        }}
                      >
                        {ln || " "}
                      </div>
                    );
                  })
                ) : (
                  <div style={{ color: "rgba(240,237,232,0.45)" }}>
                    No modified files to display.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
