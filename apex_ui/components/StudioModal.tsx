"use client";

import React, { useCallback, useEffect, useState } from "react";
import {
  BookOpen,
  Check,
  Palette,
  Plus,
  Sparkles,
  Shield,
  Trash2,
  UserCheck,
  Users,
  X,
} from "lucide-react";
import {
  CompanionSummary,
  ThemeCustomConfig,
  useJarvis,
} from "./JarvisBridge";
import SoulStudioPanel from "./SoulStudioPanel";

type InterviewQ = { id: string; question: string; options: string[] };
type LearnedRule = { id: string; rule: string; ts: string };
type SkillStudioItem = {
  name: string;
  description: string;
  body: string;
  builtin: boolean;
  resources: string[];
};
type ThemePreset = {
  id: string;
  name: string;
  description: string;
  primary: string;
  secondary: string;
};

type StudioSnapshot = {
  interview_questions: InterviewQ[];
  interview_answers: Record<string, string>;
  learned_rules: LearnedRule[];
  active_companion: CompanionSummary;
  companions: CompanionSummary[];
  skills: SkillStudioItem[];
  theme: ThemeCustomConfig & { presets: ThemePreset[] };
  available_tools: string[];
};

const GREEN = "#3be38a";
const RED = "#ff5d6c";

export default function StudioModal() {
  const {
    studioModalOpen,
    setStudioModalOpen,
    theme,
    maleVoices,
    femaleVoices,
    setThemeCustom,
  } = useJarvis();

  const [tab, setTab] = useState<"soul" | "companions" | "interview" | "skills" | "themes">(
    "soul"
  );
  const [data, setData] = useState<StudioSnapshot | null>(null);
  const [statusMsg, setStatusMsg] = useState("");

  // Interview draft
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [newRule, setNewRule] = useState("");

  // Companion builder draft
  const [compName, setCompName] = useState("");
  const [compRole, setCompRole] = useState("");
  const [compPersona, setCompPersona] = useState<"male" | "female">("male");
  const [compVoice, setCompVoice] = useState("Charon");
  const [compInstr, setCompInstr] = useState("");
  const [compTools, setCompTools] = useState<string[]>([]);

  // Skill author draft
  const [selectedSkill, setSelectedSkill] = useState<SkillStudioItem | null>(null);
  const [skillName, setSkillName] = useState("");
  const [skillDesc, setSkillDesc] = useState("");
  const [skillBody, setSkillBody] = useState(
    "## When to use\nTrigger on ...\n\n## Procedure\n1. Step one\n\n## Pitfalls\n- Watch out for ...\n\n## Verification\n- Confirm result"
  );
  const [customPri, setCustomPri] = useState("");
  const [customSec, setCustomSec] = useState("");

  const refresh = useCallback(async () => {
    try {
      const r = await fetch("/api/hud/studio");
      if (r.ok) {
        const j = await r.json();
        if (j.studio) {
          setData(j.studio);
          setAnswers(j.studio.interview_answers || {});
          setCustomPri(j.studio.theme?.custom_primary || "");
          setCustomSec(j.studio.theme?.custom_secondary || "");
        }
      }
    } catch {}
  }, []);

  useEffect(() => {
    if (studioModalOpen) {
      refresh();
      setStatusMsg("");
    }
  }, [studioModalOpen, refresh]);

  if (!studioModalOpen) return null;

  const PRIMARY = theme.primary;
  const SECONDARY = theme.secondary;

  const postAction = async (payload: Record<string, unknown>) => {
    const r = await fetch("/api/hud/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const j = await r.json();
    if (j.studio) setData(j.studio);
    if (j.theme) setThemeCustom(j.theme);
    return j;
  };

  const onSaveInterview = async () => {
    await postAction({ action: "studio_save_interview", answers });
    setStatusMsg("Behavior interview saved & synced to Brain.");
  };

  const onAddRule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRule.trim()) return;
    await postAction({ action: "studio_add_rule", rule: newRule.trim() });
    setNewRule("");
  };

  const onSaveCompanion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!compName.trim()) return;
    const j = await postAction({
      action: "studio_save_companion",
      companion: {
        name: compName.trim(),
        role: compRole.trim() || "Specialist Companion",
        persona: compPersona,
        voice: compVoice,
        instructions: compInstr.trim(),
        allowed_tools: compTools,
      },
    });
    if (j.ok) {
      setCompName("");
      setCompRole("");
      setCompInstr("");
      setCompTools([]);
      setStatusMsg(`Saved specialist companion "${j.companion?.name}".`);
    } else if (j.error) {
      setStatusMsg(j.error);
    }
  };

  const onSaveSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    const j = await postAction({
      action: "studio_save_skill",
      name: skillName,
      description: skillDesc,
      body: skillBody,
    });
    if (j.ok) {
      setStatusMsg(`Saved custom skill "${j.name}".`);
    } else if (j.error) {
      setStatusMsg(j.error);
    }
  };

  const toggleTool = (t: string) => {
    setCompTools((prev) =>
      prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t]
    );
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Companions, Behavior & Skills Studio"
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 82,
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
          <Sparkles size={17} color={PRIMARY} />
          <div style={{ flex: 1 }}>
            <div
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: 11,
                letterSpacing: "0.24em",
                color: PRIMARY,
              }}
            >
              STUDIO · COMPANIONS, BEHAVIOR, SKILLS & THEMES
            </div>
            <div style={{ fontSize: 11.5, color: "rgba(240,237,232,0.58)", marginTop: 2 }}>
              Active Companion: <strong>{data?.active_companion?.name || "JARVIS"}</strong> ·{" "}
              {data?.active_companion?.role || "Full-Access"}
            </div>
          </div>
          <button
            type="button"
            onClick={() => setStudioModalOpen(false)}
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
              { id: "soul", label: "SOUL", icon: Shield },
              { id: "companions", label: "COMPANIONS", icon: Users },
              { id: "interview", label: "BEHAVIOR INTERVIEW", icon: UserCheck },
              { id: "skills", label: "SKILLS STUDIO", icon: BookOpen },
              { id: "themes", label: "THEMES", icon: Palette },
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
          {tab === "soul" && <SoulStudioPanel primary={PRIMARY} secondary={SECONDARY} />}

          {tab === "companions" && (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
              {/* Existing Companions */}
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                <div
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: 10,
                    letterSpacing: "0.16em",
                    color: SECONDARY,
                  }}
                >
                  PERSISTENT SPECIALIST ROSTER
                </div>
                {(data?.companions || []).map((c) => {
                  const isActive = data?.active_companion?.id === c.id;
                  return (
                    <div
                      key={c.id}
                      style={{
                        padding: "12px 14px",
                        borderRadius: 12,
                        border: `1px solid ${
                          isActive ? `${PRIMARY}77` : "rgba(255,255,255,0.1)"
                        }`,
                        background: isActive ? `${PRIMARY}14` : "rgba(255,255,255,0.025)",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span style={{ fontWeight: 600, fontSize: 13 }}>{c.name}</span>
                        <span
                          style={{
                            fontFamily: "var(--font-mono)",
                            fontSize: 9,
                            padding: "2px 7px",
                            borderRadius: 999,
                            background: "rgba(255,255,255,0.08)",
                          }}
                        >
                          {c.persona.toUpperCase()} · {c.voice}
                        </span>
                        <span style={{ flex: 1 }} />
                        {!isActive ? (
                          <button
                            type="button"
                            onClick={() =>
                              postAction({
                                action: "studio_activate_companion",
                                companion_id: c.id,
                              })
                            }
                            style={{
                              padding: "4px 10px",
                              borderRadius: 999,
                              border: `1px solid ${PRIMARY}66`,
                              background: `${PRIMARY}1f`,
                              color: PRIMARY,
                              fontFamily: "var(--font-mono)",
                              fontSize: 9.5,
                              cursor: "pointer",
                            }}
                          >
                            ACTIVATE
                          </button>
                        ) : (
                          <span
                            style={{
                              fontFamily: "var(--font-mono)",
                              fontSize: 9.5,
                              color: GREEN,
                              display: "inline-flex",
                              alignItems: "center",
                              gap: 4,
                            }}
                          >
                            <Check size={11} /> ACTIVE
                          </span>
                        )}
                        {!c.builtin && (
                          <button
                            type="button"
                            onClick={() =>
                              postAction({
                                action: "studio_delete_companion",
                                companion_id: c.id,
                              })
                            }
                            style={{
                              background: "none",
                              border: "none",
                              color: RED,
                              cursor: "pointer",
                            }}
                          >
                            <Trash2 size={13} />
                          </button>
                        )}
                      </div>
                      <div style={{ fontSize: 11.5, color: "rgba(240,237,232,0.68)", marginTop: 4 }}>
                        {c.role}
                      </div>
                      {c.allowed_tools && c.allowed_tools.length > 0 && (
                        <div
                          style={{
                            fontFamily: "var(--font-mono)",
                            fontSize: 9.5,
                            color: SECONDARY,
                            marginTop: 5,
                          }}
                        >
                          Scoped tools ({c.allowed_tools.length}): {c.allowed_tools.join(", ")}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Create Specialist Companion */}
              <form
                onSubmit={onSaveCompanion}
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
                  + CREATE SPECIALIST COMPANION
                </div>
                <input
                  value={compName}
                  onChange={(e) => setCompName(e.target.value)}
                  placeholder="Name (e.g. ATHENA, ARCHIMEDES, VALKYRIE)"
                  style={{
                    padding: "8px 11px",
                    borderRadius: 8,
                    border: "1px solid rgba(255,255,255,0.14)",
                    background: "rgba(0,0,0,0.35)",
                    color: "#f0ede8",
                    fontSize: 12,
                  }}
                />
                <input
                  value={compRole}
                  onChange={(e) => setCompRole(e.target.value)}
                  placeholder="Specialist Role (e.g. Security & Code Auditor)"
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
                    value={compPersona}
                    onChange={(e) => {
                      const p = e.target.value === "female" ? "female" : "male";
                      setCompPersona(p);
                      setCompVoice(p === "female" ? "Aoede" : "Charon");
                    }}
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
                    <option value="male">Male Edition (Cyan/Gold)</option>
                    <option value="female">Female Edition (Rose/Orchid)</option>
                  </select>
                  <select
                    value={compVoice}
                    onChange={(e) => setCompVoice(e.target.value)}
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
                    {(compPersona === "female" ? femaleVoices : maleVoices).map((v) => (
                      <option key={v} value={v}>
                        Voice: {v}
                      </option>
                    ))}
                  </select>
                </div>
                <textarea
                  value={compInstr}
                  onChange={(e) => setCompInstr(e.target.value)}
                  rows={3}
                  placeholder="Specialist system instructions, focus areas & constraints…"
                  style={{
                    padding: "8px 11px",
                    borderRadius: 8,
                    border: "1px solid rgba(255,255,255,0.14)",
                    background: "rgba(0,0,0,0.35)",
                    color: "#f0ede8",
                    fontSize: 12,
                    resize: "vertical",
                  }}
                />
                <div style={{ fontSize: 11, color: "rgba(240,237,232,0.65)" }}>
                  Scoped Tool Permissions (leave unselected for all tools):
                </div>
                <div
                  style={{
                    maxHeight: 110,
                    overflowY: "auto",
                    display: "flex",
                    flexWrap: "wrap",
                    gap: 5,
                  }}
                >
                  {(data?.available_tools || []).map((t) => {
                    const on = compTools.includes(t);
                    return (
                      <button
                        key={t}
                        type="button"
                        onClick={() => toggleTool(t)}
                        style={{
                          padding: "3px 8px",
                          borderRadius: 999,
                          border: `1px solid ${on ? PRIMARY : "rgba(255,255,255,0.14)"}`,
                          background: on ? `${PRIMARY}24` : "transparent",
                          color: on ? PRIMARY : "rgba(240,237,232,0.65)",
                          fontFamily: "var(--font-mono)",
                          fontSize: 9.5,
                          cursor: "pointer",
                        }}
                      >
                        {t}
                      </button>
                    );
                  })}
                </div>
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
                  SAVE SPECIALIST COMPANION
                </button>
              </form>
            </div>
          )}

          {tab === "interview" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {(data?.interview_questions || []).map((q) => (
                <div
                  key={q.id}
                  style={{
                    padding: "12px 15px",
                    borderRadius: 12,
                    background: "rgba(255,255,255,0.025)",
                    border: "1px solid rgba(255,255,255,0.08)",
                  }}
                >
                  <div style={{ fontSize: 12.5, fontWeight: 600, marginBottom: 8 }}>
                    {q.question}
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 7 }}>
                    {q.options.map((opt) => {
                      const sel = answers[q.id] === opt;
                      return (
                        <button
                          key={opt}
                          type="button"
                          onClick={() => setAnswers((a) => ({ ...a, [q.id]: opt }))}
                          style={{
                            padding: "6px 12px",
                            borderRadius: 999,
                            border: `1px solid ${sel ? PRIMARY : "rgba(255,255,255,0.14)"}`,
                            background: sel ? `${PRIMARY}24` : "transparent",
                            color: sel ? PRIMARY : "rgba(240,237,232,0.75)",
                            fontSize: 11.5,
                            cursor: "pointer",
                          }}
                        >
                          {opt}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
              <button
                type="button"
                onClick={onSaveInterview}
                style={{
                  alignSelf: "flex-start",
                  padding: "9px 18px",
                  borderRadius: 999,
                  border: `1px solid ${PRIMARY}77`,
                  background: `${PRIMARY}22`,
                  color: PRIMARY,
                  fontFamily: "var(--font-mono)",
                  fontSize: 10.5,
                  cursor: "pointer",
                }}
              >
                SAVE BEHAVIOR INTERVIEW
              </button>

              {/* Learned Adaptive Rules */}
              <div
                style={{
                  marginTop: 8,
                  paddingTop: 14,
                  borderTop: "1px solid rgba(255,255,255,0.08)",
                }}
              >
                <div
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: 10,
                    letterSpacing: "0.16em",
                    color: SECONDARY,
                    marginBottom: 8,
                  }}
                >
                  ADAPTIVE LEARNED STYLE RULES ({data?.learned_rules?.length || 0})
                </div>
                <form onSubmit={onAddRule} style={{ display: "flex", gap: 8, marginBottom: 10 }}>
                  <input
                    value={newRule}
                    onChange={(e) => setNewRule(e.target.value)}
                    placeholder="Add custom rule (e.g. 'Never use emojis in status reports')…"
                    style={{
                      flex: 1,
                      padding: "8px 12px",
                      borderRadius: 8,
                      border: "1px solid rgba(255,255,255,0.14)",
                      background: "rgba(0,0,0,0.35)",
                      color: "#f0ede8",
                      fontSize: 12,
                    }}
                  />
                  <button
                    type="submit"
                    style={{
                      padding: "8px 14px",
                      borderRadius: 8,
                      border: `1px solid ${SECONDARY}66`,
                      background: `${SECONDARY}22`,
                      color: SECONDARY,
                      fontFamily: "var(--font-mono)",
                      fontSize: 10,
                      cursor: "pointer",
                    }}
                  >
                    <Plus size={12} /> ADD RULE
                  </button>
                </form>
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  {(data?.learned_rules || []).map((r) => (
                    <div
                      key={r.id}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 10,
                        padding: "8px 12px",
                        borderRadius: 9,
                        background: "rgba(255,255,255,0.025)",
                        border: "1px solid rgba(255,255,255,0.08)",
                      }}
                    >
                      <span style={{ flex: 1, fontSize: 12 }}>{r.rule}</span>
                      <span style={{ fontSize: 10, color: "rgba(240,237,232,0.45)" }}>{r.ts}</span>
                      <button
                        type="button"
                        onClick={() =>
                          postAction({ action: "studio_delete_rule", rule_id: r.id })
                        }
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
                  ))}
                </div>
              </div>
            </div>
          )}

          {tab === "skills" && (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1.25fr", gap: 18 }}>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <div
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: 10,
                    letterSpacing: "0.16em",
                    color: SECONDARY,
                  }}
                >
                  INSTALLED SKILL.MD PLAYBOOKS ({data?.skills?.length || 0})
                </div>
                {(data?.skills || []).map((s) => (
                  <div
                    key={s.name}
                    onClick={() => {
                      setSelectedSkill(s);
                      if (!s.builtin) {
                        setSkillName(s.name);
                        setSkillDesc(s.description);
                        setSkillBody(s.body);
                      }
                    }}
                    style={{
                      padding: "10px 12px",
                      borderRadius: 10,
                      border: `1px solid ${
                        selectedSkill?.name === s.name
                          ? PRIMARY
                          : "rgba(255,255,255,0.09)"
                      }`,
                      background: "rgba(255,255,255,0.025)",
                      cursor: "pointer",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <span
                        style={{
                          fontFamily: "var(--font-mono)",
                          fontSize: 11,
                          color: PRIMARY,
                          fontWeight: 600,
                        }}
                      >
                        {s.name}
                      </span>
                      <span
                        style={{
                          fontFamily: "var(--font-mono)",
                          fontSize: 8.5,
                          padding: "1px 6px",
                          borderRadius: 999,
                          background: s.builtin ? "rgba(255,255,255,0.08)" : `${SECONDARY}28`,
                          color: s.builtin ? "rgba(240,237,232,0.7)" : SECONDARY,
                        }}
                      >
                        {s.builtin ? "CORE" : "CUSTOM"}
                      </span>
                      <span style={{ flex: 1 }} />
                      {!s.builtin && (
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            postAction({ action: "studio_delete_skill", name: s.name });
                          }}
                          style={{
                            background: "none",
                            border: "none",
                            color: RED,
                            cursor: "pointer",
                          }}
                        >
                          <Trash2 size={12} />
                        </button>
                      )}
                    </div>
                    <div style={{ fontSize: 11, color: "rgba(240,237,232,0.62)", marginTop: 3 }}>
                      {s.description}
                    </div>
                  </div>
                ))}
              </div>

              <form
                onSubmit={onSaveSkill}
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
                  AUTHOR CUSTOM SKILL.MD PLAYBOOK
                </div>
                <input
                  value={skillName}
                  onChange={(e) => setSkillName(e.target.value)}
                  placeholder="slug-name (lowercase & hyphens, e.g. sprint-review)"
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
                <input
                  value={skillDesc}
                  onChange={(e) => setSkillDesc(e.target.value)}
                  placeholder="Trigger description (20-160 chars: what it does & when to invoke)"
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
                  value={skillBody}
                  onChange={(e) => setSkillBody(e.target.value)}
                  rows={10}
                  style={{
                    padding: "9px 11px",
                    borderRadius: 8,
                    border: "1px solid rgba(255,255,255,0.14)",
                    background: "rgba(0,0,0,0.35)",
                    color: "#f0ede8",
                    fontFamily: "var(--font-mono)",
                    fontSize: 11.5,
                    resize: "vertical",
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
                  VALIDATE & SAVE SKILL.MD
                </button>
              </form>
            </div>
          )}

          {tab === "themes" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))",
                  gap: 12,
                }}
              >
                {(data?.theme?.presets || []).map((p) => {
                  const active = data?.theme?.preset === p.id;
                  return (
                    <button
                      key={p.id}
                      type="button"
                      onClick={() =>
                        postAction({
                          action: "studio_save_theme",
                          preset: p.id,
                          custom_primary: "",
                          custom_secondary: "",
                        })
                      }
                      style={{
                        textAlign: "left",
                        padding: "14px",
                        borderRadius: 13,
                        border: `1px solid ${
                          active ? PRIMARY : "rgba(255,255,255,0.1)"
                        }`,
                        background: active ? `${PRIMARY}16` : "rgba(255,255,255,0.025)",
                        color: "#f0ede8",
                        cursor: "pointer",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span
                          style={{
                            width: 14,
                            height: 14,
                            borderRadius: "50%",
                            background: p.primary || PRIMARY,
                          }}
                        />
                        <span
                          style={{
                            width: 14,
                            height: 14,
                            borderRadius: "50%",
                            background: p.secondary || SECONDARY,
                          }}
                        />
                        <span style={{ fontWeight: 600, fontSize: 12.5 }}>{p.name}</span>
                      </div>
                      <div
                        style={{
                          fontSize: 11,
                          color: "rgba(240,237,232,0.62)",
                          marginTop: 6,
                        }}
                      >
                        {p.description}
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* Custom Hex Color Pickers */}
              <div
                style={{
                  marginTop: 8,
                  padding: 16,
                  borderRadius: 14,
                  background: "rgba(255,255,255,0.025)",
                  border: "1px solid rgba(255,255,255,0.09)",
                  display: "flex",
                  flexWrap: "wrap",
                  alignItems: "center",
                  gap: 14,
                }}
              >
                <span
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: 10,
                    letterSpacing: "0.14em",
                    color: SECONDARY,
                  }}
                >
                  CUSTOM ORB & HUD HEX PALETTE
                </span>
                <label style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 11.5 }}>
                  Primary:
                  <input
                    type="color"
                    value={customPri || PRIMARY}
                    onChange={(e) => setCustomPri(e.target.value)}
                    style={{ width: 30, height: 28, border: "none", background: "none", cursor: "pointer" }}
                  />
                  <input
                    value={customPri}
                    onChange={(e) => setCustomPri(e.target.value)}
                    placeholder="#00e5ff"
                    style={{
                      width: 92,
                      padding: "6px 8px",
                      borderRadius: 6,
                      border: "1px solid rgba(255,255,255,0.14)",
                      background: "rgba(0,0,0,0.35)",
                      color: "#f0ede8",
                      fontFamily: "var(--font-mono)",
                      fontSize: 11,
                    }}
                  />
                </label>
                <label style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 11.5 }}>
                  Secondary:
                  <input
                    type="color"
                    value={customSec || SECONDARY}
                    onChange={(e) => setCustomSec(e.target.value)}
                    style={{ width: 30, height: 28, border: "none", background: "none", cursor: "pointer" }}
                  />
                  <input
                    value={customSec}
                    onChange={(e) => setCustomSec(e.target.value)}
                    placeholder="#f5a623"
                    style={{
                      width: 92,
                      padding: "6px 8px",
                      borderRadius: 6,
                      border: "1px solid rgba(255,255,255,0.14)",
                      background: "rgba(0,0,0,0.35)",
                      color: "#f0ede8",
                      fontFamily: "var(--font-mono)",
                      fontSize: 11,
                    }}
                  />
                </label>
                <button
                  type="button"
                  onClick={() =>
                    postAction({
                      action: "studio_save_theme",
                      preset: data?.theme?.preset || "default",
                      custom_primary: customPri,
                      custom_secondary: customSec,
                    })
                  }
                  style={{
                    padding: "7px 14px",
                    borderRadius: 999,
                    border: `1px solid ${PRIMARY}66`,
                    background: `${PRIMARY}22`,
                    color: PRIMARY,
                    fontFamily: "var(--font-mono)",
                    fontSize: 10,
                    cursor: "pointer",
                  }}
                >
                  APPLY CUSTOM HEX
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
