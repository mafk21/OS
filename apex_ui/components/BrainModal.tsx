"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  Brain,
  Clock,
  Download,
  Edit3,
  FileText,
  Pin,
  Plus,
  Search,
  Shield,
  Sparkles,
  Trash2,
  Upload,
  X,
} from "lucide-react";
import { useJarvis } from "./JarvisBridge";

type MemoryItem = {
  category: string;
  key: string;
  value: string;
  updated: string;
  source?: string;
  confidence?: number | null;
  status?: string;
  sensitivity?: string;
  pinned?: boolean;
  expires_at?: string | null;
};

type TimelineTurn = {
  id: number;
  role: string;
  speaker: string;
  channel: string;
  content: string;
  created_at: string;
};

type EpochItem = {
  id: number;
  summary: string;
  created_at: string;
};

type BrainFileItem = {
  id: number;
  filename: string;
  mime_type: string;
  size_bytes: number;
  chunk_count: number;
  preview: string;
  created_at: string;
  full_text?: string;
};

type OutputItem = {
  id: number;
  title: string;
  category: string;
  content: string;
  pinned: number;
  created_at: string;
};

type TabKey = "memories" | "timeline" | "files" | "outputs";

const GREEN = "#34d399";
const RED = "#ff5b79";
const CATEGORIES = [
  "preferences",
  "identity",
  "projects",
  "relationships",
  "wishes",
  "notes",
] as const;

export default function BrainModal() {
  const {
    assistantName,
    theme,
    privacy,
    brainModalOpen,
    setBrainModalOpen,
    updatePrivacy,
    showContentCard,
    fireLocalTrace,
  } = useJarvis();

  const PRIMARY = theme.primary;
  const SECONDARY = theme.secondary;

  const [tab, setTab] = useState<TabKey>("memories");
  const [query, setQuery] = useState("");
  const [channelFilter, setChannelFilter] = useState("");

  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [timeline, setTimeline] = useState<TimelineTurn[]>([]);
  const [epochs, setEpochs] = useState<EpochItem[]>([]);
  const [files, setFiles] = useState<BrainFileItem[]>([]);
  const [outputs, setOutputs] = useState<OutputItem[]>([]);
  const [loading, setLoading] = useState(false);

  // Add / edit memory states
  const [newCat, setNewCat] = useState<string>("preferences");
  const [newKey, setNewKey] = useState("");
  const [newVal, setNewVal] = useState("");
  const [editId, setEditId] = useState<string | null>(null);
  const [editVal, setEditVal] = useState("");

  // Knowledge file upload / paste states
  const [dragging, setDragging] = useState(false);
  const [noteTitle, setNoteTitle] = useState("");
  const [noteBody, setNoteBody] = useState("");
  const [expandedFile, setExpandedFile] = useState<BrainFileItem | null>(null);
  const [expandedOutId, setExpandedOutId] = useState<number | null>(null);
  const [statusMsg, setStatusMsg] = useState("");

  const fileInputRef = useRef<HTMLInputElement>(null);
  const importInputRef = useRef<HTMLInputElement>(null);

  const applySnap = useCallback((b: Record<string, unknown> | undefined) => {
    if (!b || typeof b !== "object") return;
    if (Array.isArray(b.memories)) setMemories(b.memories as MemoryItem[]);
    if (Array.isArray(b.timeline)) {
      setTimeline([...(b.timeline as TimelineTurn[])].reverse());
    }
    if (Array.isArray(b.epochs)) setEpochs(b.epochs as EpochItem[]);
    if (Array.isArray(b.files)) setFiles(b.files as BrainFileItem[]);
    if (Array.isArray(b.outputs)) setOutputs(b.outputs as OutputItem[]);
  }, []);

  const refreshBrain = useCallback(async () => {
    setLoading(true);
    try {
      const r = await fetch("/api/hud/brain");
      if (r.ok) {
        const d = await r.json();
        applySnap(d.brain);
      }
    } catch {}
    setLoading(false);
  }, [applySnap]);

  useEffect(() => {
    if (brainModalOpen) {
      fireLocalTrace(["memory", "editor"]);
      refreshBrain();
    }
  }, [brainModalOpen, fireLocalTrace, refreshBrain]);

  useEffect(() => {
    if (!brainModalOpen) return;
    const t = setTimeout(async () => {
      if (!query.trim() && !channelFilter) {
        refreshBrain();
        return;
      }
      try {
        const r = await fetch("/api/hud/action", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            action: "brain_search",
            query,
            channel: channelFilter,
          }),
        });
        if (r.ok) {
          const d = await r.json();
          if (Array.isArray(d.memories)) setMemories(d.memories);
          if (Array.isArray(d.timeline)) setTimeline(d.timeline);
          if (Array.isArray(d.files)) setFiles(d.files);
          if (Array.isArray(d.outputs)) setOutputs(d.outputs);
        }
      } catch {}
    }, 180);
    return () => clearTimeout(t);
  }, [query, channelFilter, brainModalOpen, refreshBrain]);

  if (!brainModalOpen) return null;

  const postBrain = async (payload: Record<string, unknown>) => {
    const r = await fetch("/api/hud/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const d = await r.json();
    if (d.brain) applySnap(d.brain);
    return d;
  };

  const onAddMemory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKey.trim() || !newVal.trim()) return;
    await postBrain({
      action: "brain_save_memory",
      category: newCat,
      key: newKey.trim(),
      value: newVal.trim(),
    });
    setNewKey("");
    setNewVal("");
    setStatusMsg("Saved memory ✓");
    setTimeout(() => setStatusMsg(""), 2000);
  };

  const onSaveEdit = async (m: MemoryItem) => {
    if (!editVal.trim()) return;
    await postBrain({
      action: "brain_save_memory",
      category: m.category,
      key: m.key,
      value: editVal.trim(),
    });
    setEditId(null);
  };

  const onPin = async (m: MemoryItem) => {
    await postBrain({ action: "brain_pin_memory", category: m.category, key: m.key, pinned: !m.pinned });
  };

  const onForget = async (m: MemoryItem) => {
    await postBrain({
      action: "brain_forget_memory",
      category: m.category,
      key: m.key,
    });
  };

  const uploadBrowserFiles = async (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;
    for (const f of Array.from(fileList)) {
      const dataUrl = await new Promise<string>((resolve) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result || ""));
        reader.readAsDataURL(f);
      });
      await postBrain({
        action: "brain_upload_file",
        filename: f.name,
        content: dataUrl,
        is_base64: true,
      });
    }
    setStatusMsg("Indexed knowledge file(s) into Brain ✓");
    setTimeout(() => setStatusMsg(""), 2400);
  };

  const onSaveNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noteBody.trim()) return;
    const fname = (noteTitle.trim() || "brain_note") + (noteTitle.includes(".") ? "" : ".md");
    await postBrain({
      action: "brain_upload_file",
      filename: fname,
      content: noteBody,
      is_base64: false,
    });
    setNoteTitle("");
    setNoteBody("");
    setStatusMsg("Added note to Brain ✓");
    setTimeout(() => setStatusMsg(""), 2000);
  };

  const onViewFile = async (f: BrainFileItem) => {
    if (expandedFile?.id === f.id) {
      setExpandedFile(null);
      return;
    }
    const d = await postBrain({ action: "brain_read_file", file_id: f.id });
    if (d.file) setExpandedFile(d.file as BrainFileItem);
  };

  const onExportJson = () => {
    window.open("/api/hud/brain/export", "_blank", "noopener,noreferrer");
  };

  const onImportJson = async (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;
    try {
      const raw = await fileList[0].text();
      const parsed = JSON.parse(raw);
      await postBrain({ action: "brain_import_json", payload: parsed });
      setStatusMsg("Imported Brain backup ✓");
      setTimeout(() => setStatusMsg(""), 2500);
    } catch {
      setStatusMsg("Invalid JSON export file.");
    }
  };

  const downloadOutputMd = (o: OutputItem) => {
    const blob = new Blob([`# ${o.title}\n\n${o.content}`], {
      type: "text/markdown;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${o.title.toLowerCase().replace(/[^a-z0-9]+/g, "_") || "output"}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const inputStyle: React.CSSProperties = {
    background: theme.inputBg,
    color: "#f0ede8",
    border: `1px solid ${theme.primaryBorder}`,
    borderRadius: 8,
    padding: "8px 10px",
    fontSize: 12,
    outline: "none",
    fontFamily: "var(--font-mono)",
  };

  const pillBtn = (active = false, accent = PRIMARY): React.CSSProperties => ({
    display: "inline-flex",
    alignItems: "center",
    gap: 6,
    fontFamily: "var(--font-mono)",
    fontSize: 10,
    letterSpacing: "0.14em",
    textTransform: "uppercase",
    padding: "6px 12px",
    borderRadius: 999,
    border: `1px solid ${active ? accent : "rgba(240,237,232,0.18)"}`,
    background: active ? `${accent}24` : "rgba(255,255,255,0.03)",
    color: active ? accent : "rgba(240,237,232,0.78)",
    cursor: "pointer",
  });

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="JARVIS Brain and Forever Timeline"
      onClick={() => setBrainModalOpen(false)}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 86,
        background: "rgba(2, 6, 14, 0.78)",
        backdropFilter: "blur(13px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 14,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: "min(880px, 96vw)",
          height: "min(86vh, 760px)",
          background: theme.panelBg,
          border: `1px solid ${PRIMARY}55`,
          borderRadius: 22,
          padding: "20px 22px 16px",
          boxShadow: `0 0 64px ${PRIMARY}26, 0 24px 68px rgba(0,0,0,0.88)`,
          display: "flex",
          flexDirection: "column",
          gap: 13,
        }}
      >
        {/* Header */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 10,
            flexWrap: "wrap",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
            <Brain size={18} style={{ color: PRIMARY }} />
            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: 11.5,
                letterSpacing: "0.22em",
                color: PRIMARY,
                fontWeight: 600,
              }}
            >
              {assistantName.toUpperCase()} · THE BRAIN & FOREVER TIMELINE
            </span>
            {statusMsg && (
              <span
                style={{
                  fontSize: 11,
                  color: GREEN,
                  fontFamily: "var(--font-mono)",
                }}
              >
                {statusMsg}
              </span>
            )}
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
            <button type="button" onClick={onExportJson} style={pillBtn()}>
              <Download size={11} /> EXPORT JSON
            </button>
            <button
              type="button"
              onClick={() => importInputRef.current?.click()}
              style={pillBtn()}
            >
              <Upload size={11} /> IMPORT JSON
            </button>
            <input
              ref={importInputRef}
              type="file"
              accept=".json,application/json"
              style={{ display: "none" }}
              onChange={(e) => onImportJson(e.target.files)}
            />
            <button
              type="button"
              onClick={() => setBrainModalOpen(false)}
              aria-label="Close Brain drawer"
              style={{
                background: "none",
                border: "none",
                color: "rgba(255,255,255,0.55)",
                cursor: "pointer",
                marginLeft: 4,
              }}
            >
              <X size={19} />
            </button>
          </div>
        </div>

        {/* Search + Tabs Row */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 10,
            flexWrap: "wrap",
          }}
        >
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            <button
              type="button"
              onClick={() => setTab("memories")}
              style={pillBtn(tab === "memories")}
            >
              <Sparkles size={11} /> MEMORIES ({memories.length})
            </button>
            <button
              type="button"
              onClick={() => setTab("timeline")}
              style={pillBtn(tab === "timeline")}
            >
              <Clock size={11} /> TIMELINE ({timeline.length})
            </button>
            <button
              type="button"
              onClick={() => setTab("files")}
              style={pillBtn(tab === "files")}
            >
              <FileText size={11} /> KNOWLEDGE FILES ({files.length})
            </button>
            <button
              type="button"
              onClick={() => setTab("outputs")}
              style={pillBtn(tab === "outputs")}
            >
              <Pin size={11} /> OUTPUTS ({outputs.length})
            </button>
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 7,
              background: theme.inputBg,
              border: `1px solid ${theme.primaryBorder}`,
              borderRadius: 999,
              padding: "5px 12px",
              minWidth: 230,
              flex: "0 1 280px",
            }}
          >
            <Search size={13} style={{ color: PRIMARY }} />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search Brain & Timeline..."
              style={{
                background: "transparent",
                border: "none",
                color: "#f0ede8",
                fontSize: 12,
                outline: "none",
                width: "100%",
              }}
            />
          </div>
        </div>

        {/* Main Scrollable Tab Body */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            gap: 10,
            paddingRight: 4,
          }}
        >
          {loading && (
            <div style={{ fontSize: 12, color: "rgba(240,237,232,0.5)" }}>
              Syncing Brain...
            </div>
          )}

          {/* ── TAB 1: MEMORIES ── */}
          {tab === "memories" && (
            <>
              <form
                onSubmit={onAddMemory}
                style={{
                  display: "grid",
                  gridTemplateColumns: "130px 150px 1fr auto",
                  gap: 7,
                  alignItems: "center",
                }}
              >
                <select
                  value={newCat}
                  onChange={(e) => setNewCat(e.target.value)}
                  style={inputStyle}
                >
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
                <input
                  type="text"
                  value={newKey}
                  onChange={(e) => setNewKey(e.target.value)}
                  placeholder="Key (e.g. role, coffee)"
                  style={inputStyle}
                />
                <input
                  type="text"
                  value={newVal}
                  onChange={(e) => setNewVal(e.target.value)}
                  placeholder="What should JARVIS remember?"
                  style={inputStyle}
                />
                <button type="submit" style={pillBtn(true)}>
                  <Plus size={12} /> SAVE
                </button>
              </form>

              {memories.length > 0 && (
                <div style={{ display: "flex", justifyContent: "flex-end" }}>
                  <button
                    type="button"
                    onClick={() => postBrain({ action: "brain_clear_memories" })}
                    style={pillBtn(false, RED)}
                  >
                    <Trash2 size={11} /> FORGET ALL MEMORIES
                  </button>
                </div>
              )}

              {memories.length === 0 ? (
                <div
                  style={{
                    padding: 28,
                    textAlign: "center",
                    color: "rgba(240,237,232,0.5)",
                    fontSize: 12.5,
                  }}
                >
                  No personal memories stored yet. Talk naturally with {assistantName} or
                  add facts above — you can edit or forget anything in one click.
                </div>
              ) : (
                memories.map((m) => {
                  const idKey = `${m.category}/${m.key}`;
                  const isEditing = editId === idKey;
                  return (
                    <div
                      key={idKey}
                      style={{
                        borderRadius: 12,
                        padding: "11px 14px",
                        background: "rgba(255,255,255,0.03)",
                        border: `1px solid ${PRIMARY}26`,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        gap: 10,
                      }}
                    >
                      <div style={{ flex: 1 }}>
                        <div
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: 8,
                            marginBottom: 4,
                          }}
                        >
                          <span
                            style={{
                              fontFamily: "var(--font-mono)",
                              fontSize: 9.5,
                              padding: "2px 7px",
                              borderRadius: 999,
                              background: `${SECONDARY}22`,
                              color: SECONDARY,
                              textTransform: "uppercase",
                            }}
                          >
                            {m.category}
                          </span>
                          <span
                            style={{
                              fontFamily: "var(--font-mono)",
                              fontSize: 11,
                              color: PRIMARY,
                              fontWeight: 600,
                            }}
                          >
                            {m.key.replace(/_/g, " ")}
                          </span>
                          {m.updated && (
                            <span
                              style={{
                                fontSize: 10,
                                color: "rgba(240,237,232,0.42)",
                              }}
                            >
                              {m.updated}
                            </span>
                          )}
                        </div>

                        {isEditing ? (
                          <div style={{ display: "flex", gap: 6 }}>
                            <input
                              type="text"
                              value={editVal}
                              onChange={(e) => setEditVal(e.target.value)}
                              style={{ ...inputStyle, flex: 1 }}
                            />
                            <button
                              type="button"
                              onClick={() => onSaveEdit(m)}
                              style={pillBtn(true, GREEN)}
                            >
                              SAVE
                            </button>
                            <button
                              type="button"
                              onClick={() => setEditId(null)}
                              style={pillBtn()}
                            >
                              CANCEL
                            </button>
                          </div>
                        ) : (
                          <div
                            style={{
                              fontSize: 12.5,
                              color: "rgba(240,237,232,0.88)",
                              lineHeight: 1.45,
                            }}
                          >
                            {m.value}
                            <div style={{ marginTop: 5, color: "rgba(240,237,232,.42)", fontSize: 9, fontFamily: "var(--font-mono)" }}>
                              {m.status || "active"} · {m.source || "legacy"}{typeof m.confidence === "number" ? ` · ${Math.round(m.confidence * 100)}% confidence` : ""}{m.pinned ? " · pinned" : ""}
                            </div>
                          </div>
                        )}
                      </div>

                      {!isEditing && (
                        <div style={{ display: "flex", gap: 6 }}>
                          <button type="button" onClick={() => void onPin(m)} style={{ ...pillBtn(), color: m.pinned ? PRIMARY : undefined }} title={m.pinned ? "Unpin memory" : "Pin memory"}>
                            <Pin size={11} />
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              setEditId(idKey);
                              setEditVal(m.value);
                            }}
                            style={pillBtn()}
                            title="Correct memory"
                          >
                            <Edit3 size={11} />
                          </button>
                          <button
                            type="button"
                            onClick={() => onForget(m)}
                            style={{ ...pillBtn(), borderColor: `${RED}55`, color: RED }}
                            title="Forget this memory"
                          >
                            <Trash2 size={11} /> FORGET
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </>
          )}

          {/* ── TAB 2: FOREVER TIMELINE ── */}
          {tab === "timeline" && (
            <>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 8,
                  flexWrap: "wrap",
                }}
              >
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {[
                    ["", "ALL CHANNELS"],
                    ["voice", "🎙 VOICE"],
                    ["text", "⌨ TEXT"],
                    ["telegram", "✈ TELEGRAM"],
                  ].map(([val, lbl]) => (
                    <button
                      key={val}
                      type="button"
                      onClick={() => setChannelFilter(val)}
                      style={pillBtn(channelFilter === val)}
                    >
                      {lbl}
                    </button>
                  ))}
                </div>

                {timeline.length > 0 && (
                  <button
                    type="button"
                    onClick={() => postBrain({ action: "brain_clear_timeline" })}
                    style={{ ...pillBtn(), borderColor: `${RED}55`, color: RED }}
                  >
                    <Trash2 size={11} /> CLEAR TIMELINE
                  </button>
                )}
              </div>

              {epochs.length > 0 && (
                <div
                  style={{
                    borderRadius: 12,
                    padding: "10px 13px",
                    background: `${SECONDARY}12`,
                    border: `1px solid ${SECONDARY}44`,
                    fontSize: 11.5,
                    color: "rgba(240,237,232,0.82)",
                  }}
                >
                  <div
                    style={{
                      fontFamily: "var(--font-mono)",
                      fontSize: 9.5,
                      letterSpacing: "0.14em",
                      color: SECONDARY,
                      marginBottom: 4,
                    }}
                  >
                    COMPRESSED EPOCH DIGESTS ({epochs.length})
                  </div>
                  {epochs.slice(0, 3).map((ep) => (
                    <div key={ep.id} style={{ marginBottom: 3 }}>
                      • {ep.summary}
                    </div>
                  ))}
                </div>
              )}

              {timeline.length === 0 ? (
                <div
                  style={{
                    padding: 28,
                    textAlign: "center",
                    color: "rgba(240,237,232,0.5)",
                    fontSize: 12.5,
                  }}
                >
                  Your Forever Timeline is empty. Spoken, typed, and Telegram
                  exchanges roll on continuously here across restarts.
                </div>
              ) : (
                timeline.map((t) => (
                  <div
                    key={t.id}
                    style={{
                      borderRadius: 12,
                      padding: "10px 13px",
                      background:
                        t.role === "user"
                          ? "rgba(255,255,255,0.04)"
                          : `${PRIMARY}0d`,
                      border: `1px solid ${
                        t.role === "user"
                          ? "rgba(255,255,255,0.1)"
                          : `${PRIMARY}33`
                      }`,
                      display: "flex",
                      justifyContent: "space-between",
                      gap: 10,
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 8,
                          fontSize: 10.5,
                          fontFamily: "var(--font-mono)",
                          color: t.role === "user" ? SECONDARY : PRIMARY,
                          marginBottom: 3,
                        }}
                      >
                        <span>{t.speaker || t.role.toUpperCase()}</span>
                        <span
                          style={{
                            padding: "1px 6px",
                            borderRadius: 999,
                            background: "rgba(255,255,255,0.07)",
                            color: "rgba(240,237,232,0.65)",
                            fontSize: 9,
                          }}
                        >
                          {t.channel.toUpperCase()}
                        </span>
                        <span style={{ color: "rgba(240,237,232,0.4)" }}>
                          {t.created_at}
                        </span>
                      </div>
                      <div
                        style={{
                          fontSize: 12.5,
                          color: "rgba(240,237,232,0.88)",
                          lineHeight: 1.48,
                          whiteSpace: "pre-wrap",
                        }}
                      >
                        {t.content}
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() =>
                        postBrain({ action: "brain_delete_turn", id: t.id })
                      }
                      style={{
                        background: "none",
                        border: "none",
                        color: "rgba(255,91,121,0.7)",
                        cursor: "pointer",
                        alignSelf: "flex-start",
                      }}
                      title="Delete turn"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                ))
              )}
            </>
          )}

          {/* ── TAB 3: KNOWLEDGE FILES ── */}
          {tab === "files" && (
            <>
              <div
                onDragOver={(e) => {
                  e.preventDefault();
                  setDragging(true);
                }}
                onDragLeave={() => setDragging(false)}
                onDrop={(e) => {
                  e.preventDefault();
                  setDragging(false);
                  uploadBrowserFiles(e.dataTransfer.files);
                }}
                onClick={() => fileInputRef.current?.click()}
                style={{
                  borderRadius: 14,
                  padding: "18px 16px",
                  border: `1.5px dashed ${
                    dragging ? PRIMARY : "rgba(240,237,232,0.25)"
                  }`,
                  background: dragging
                    ? `${PRIMARY}16`
                    : "rgba(255,255,255,0.02)",
                  textAlign: "center",
                  cursor: "pointer",
                }}
              >
                <Upload
                  size={18}
                  style={{ color: PRIMARY, margin: "0 auto 6px" }}
                />
                <div style={{ fontSize: 12.5, color: "#f0ede8" }}>
                  Drop reference files here or click to upload (`.md`, `.txt`,
                  `.pdf`, `.csv`, `.json`, `.py`)
                </div>
                <div
                  style={{
                    fontSize: 11,
                    color: "rgba(240,237,232,0.52)",
                    marginTop: 2,
                  }}
                >
                  Automatically chunked & indexed for instant voice & text recall
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  style={{ display: "none" }}
                  onChange={(e) => uploadBrowserFiles(e.target.files)}
                />
              </div>

              <form
                onSubmit={onSaveNote}
                style={{
                  display: "grid",
                  gridTemplateColumns: "180px 1fr auto",
                  gap: 7,
                }}
              >
                <input
                  type="text"
                  value={noteTitle}
                  onChange={(e) => setNoteTitle(e.target.value)}
                  placeholder="Note title (optional)"
                  style={inputStyle}
                />
                <input
                  type="text"
                  value={noteBody}
                  onChange={(e) => setNoteBody(e.target.value)}
                  placeholder="Or paste knowledge / SOP / reference text directly..."
                  style={inputStyle}
                />
                <button type="submit" style={pillBtn(true)}>
                  <Plus size={12} /> ADD NOTE
                </button>
              </form>

              {files.map((f) => (
                <div
                  key={f.id}
                  style={{
                    borderRadius: 12,
                    padding: "11px 14px",
                    background: "rgba(255,255,255,0.03)",
                    border: `1px solid ${PRIMARY}26`,
                    display: "flex",
                    flexDirection: "column",
                    gap: 6,
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      gap: 8,
                    }}
                  >
                    <div>
                      <span
                        style={{
                          fontFamily: "var(--font-mono)",
                          fontSize: 11.5,
                          color: PRIMARY,
                          fontWeight: 600,
                        }}
                      >
                        {f.filename}
                      </span>
                      <span
                        style={{
                          fontSize: 10.5,
                          color: "rgba(240,237,232,0.48)",
                          marginLeft: 10,
                        }}
                      >
                        {f.chunk_count} chunk(s) ·{" "}
                        {Math.max(1, Math.round(f.size_bytes / 1024))} KB ·{" "}
                        {f.created_at}
                      </span>
                    </div>

                    <div style={{ display: "flex", gap: 6 }}>
                      <button
                        type="button"
                        onClick={() => onViewFile(f)}
                        style={pillBtn(expandedFile?.id === f.id)}
                      >
                        {expandedFile?.id === f.id ? "HIDE" : "READ"}
                      </button>
                      <button
                        type="button"
                        onClick={() =>
                          postBrain({ action: "brain_delete_file", file_id: f.id })
                        }
                        style={{ ...pillBtn(), borderColor: `${RED}55`, color: RED }}
                      >
                        <Trash2 size={11} />
                      </button>
                    </div>
                  </div>
                  <div
                    style={{
                      fontSize: 11.5,
                      color: "rgba(240,237,232,0.7)",
                      whiteSpace: "pre-wrap",
                    }}
                  >
                    {expandedFile?.id === f.id
                      ? expandedFile.full_text || f.preview
                      : f.preview}
                  </div>
                </div>
              ))}
            </>
          )}

          {/* ── TAB 4: GENERATED OUTPUTS ── */}
          {tab === "outputs" && (
            <>
              {outputs.length === 0 ? (
                <div
                  style={{
                    padding: 28,
                    textAlign: "center",
                    color: "rgba(240,237,232,0.5)",
                    fontSize: 12.5,
                  }}
                >
                  Every research report, briefing, digest, and code review{" "}
                  {assistantName} produces is automatically archived here.
                </div>
              ) : (
                outputs.map((o) => {
                  const isExp = expandedOutId === o.id;
                  return (
                    <div
                      key={o.id}
                      style={{
                        borderRadius: 12,
                        padding: "11px 14px",
                        background: o.pinned
                          ? `${SECONDARY}12`
                          : "rgba(255,255,255,0.03)",
                        border: `1px solid ${
                          o.pinned ? `${SECONDARY}66` : `${PRIMARY}26`
                        }`,
                        display: "flex",
                        flexDirection: "column",
                        gap: 7,
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          gap: 8,
                          flexWrap: "wrap",
                        }}
                      >
                        <div>
                          <span
                            style={{
                              fontFamily: "var(--font-mono)",
                              fontSize: 11.5,
                              color: o.pinned ? SECONDARY : PRIMARY,
                              fontWeight: 600,
                            }}
                          >
                            {o.pinned ? "📌 " : ""}
                            {o.title}
                          </span>
                          <span
                            style={{
                              fontSize: 10,
                              color: "rgba(240,237,232,0.45)",
                              marginLeft: 9,
                            }}
                          >
                            {o.created_at}
                          </span>
                        </div>

                        <div style={{ display: "flex", gap: 6 }}>
                          <button
                            type="button"
                            onClick={() =>
                              postBrain({ action: "brain_pin_output", id: o.id })
                            }
                            style={pillBtn(Boolean(o.pinned), SECONDARY)}
                          >
                            <Pin size={10} /> {o.pinned ? "PINNED" : "PIN"}
                          </button>
                          <button
                            type="button"
                            onClick={() =>
                              setExpandedOutId(isExp ? null : o.id)
                            }
                            style={pillBtn(isExp)}
                          >
                            {isExp ? "COLLAPSE" : "EXPAND"}
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              showContentCard({ title: o.title, text: o.content });
                              setBrainModalOpen(false);
                            }}
                            style={pillBtn()}
                          >
                            OPEN IN HUD
                          </button>
                          <button
                            type="button"
                            onClick={() => downloadOutputMd(o)}
                            style={pillBtn()}
                          >
                            <Download size={10} /> .MD
                          </button>
                          <button
                            type="button"
                            onClick={() =>
                              postBrain({ action: "brain_delete_output", id: o.id })
                            }
                            style={{ ...pillBtn(), borderColor: `${RED}55`, color: RED }}
                          >
                            <Trash2 size={10} />
                          </button>
                        </div>
                      </div>

                      <div
                        style={{
                          fontSize: 12,
                          color: "rgba(240,237,232,0.78)",
                          whiteSpace: "pre-wrap",
                          lineHeight: 1.5,
                        }}
                      >
                        {isExp ? o.content : o.content.slice(0, 260) + (o.content.length > 260 ? "…" : "")}
                      </div>
                    </div>
                  );
                })
              )}
            </>
          )}
        </div>

        {/* Privacy Governance Footer */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 8,
            paddingTop: 10,
            borderTop: "1px solid rgba(255,255,255,0.09)",
            flexWrap: "wrap",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              fontFamily: "var(--font-mono)",
              fontSize: 10,
              letterSpacing: "0.14em",
              color: "rgba(240,237,232,0.58)",
            }}
          >
            <Shield size={13} style={{ color: PRIMARY }} />
            LOCAL DATA GOVERNANCE:
          </div>

          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            <button
              type="button"
              onClick={() =>
                updatePrivacy({
                  personalization_enabled: !privacy.personalization_enabled,
                })
              }
              style={pillBtn(privacy.personalization_enabled, GREEN)}
            >
              PERSONALIZATION: {privacy.personalization_enabled ? "ON" : "PAUSED"}
            </button>
            <button
              type="button"
              onClick={() =>
                updatePrivacy({
                  adaptive_learning_enabled: !privacy.adaptive_learning_enabled,
                })
              }
              style={pillBtn(privacy.adaptive_learning_enabled, GREEN)}
            >
              ADAPTIVE LEARNING:{" "}
              {privacy.adaptive_learning_enabled ? "ON" : "PAUSED"}
            </button>
            <button
              type="button"
              onClick={() =>
                updatePrivacy({
                  timeline_persistence_enabled:
                    !privacy.timeline_persistence_enabled,
                })
              }
              style={pillBtn(privacy.timeline_persistence_enabled, GREEN)}
            >
              FOREVER TIMELINE:{" "}
              {privacy.timeline_persistence_enabled ? "ON" : "PAUSED"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
