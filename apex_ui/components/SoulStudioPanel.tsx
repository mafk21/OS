"use client";

import React, { useCallback, useEffect, useMemo, useState } from "react";
import { Activity, Brain, Clock3, Download, HeartHandshake, History, RotateCcw, Shield, Sparkles, Target, Trash2, type LucideIcon } from "lucide-react";

type Range = { value: number; minimum: number; maximum: number };
type Soul = {
  revision: number; schema_version: number; runtime_enabled: boolean; recovery?: string | null; degraded?: string | null;
  identity: Record<string, Range | string>;
  affect: { framing: string; dimensions: Record<string, { value: number; baseline: number; daily_delta: number; daily_cap: number }>; causes: string[] };
  relationship: { stage: string; claims: Array<{ id: string; kind: string; subject: string; value: string; status: string; confidence: number }>; contradictions: unknown[] };
  commitments?: string[];
  learned_traits: Array<{ id: string; name: string; value: string; status: string; confidence: number; evidence_count: number }>;
  initiative_policy: { enabled: boolean; timezone: string; quiet_start: string; quiet_end: string; daily_budget: number; interruptions_today: number; snooze_until?: string | null; topics: unknown[] };
  reflection_state: { enabled: boolean; last_run_at?: string | null; consecutive_failures: number };
  privacy: { relationship_learning: boolean; affect_enabled: boolean; reflection_enabled: boolean; initiative_enabled: boolean };
  history: Array<{ event: string; timestamp: string; revision: number; reason: string; source: string }>;
  context_preview: string;
};

type View = "identity" | "affect" | "relationship" | "commitments" | "initiative" | "traits" | "history" | "privacy";
const VIEWS: Array<{ id: View; label: string; icon: LucideIcon }> = [
  { id: "identity", label: "IDENTITY", icon: Sparkles }, { id: "affect", label: "EXPRESSIVE", icon: Activity },
  { id: "relationship", label: "RELATIONSHIP", icon: HeartHandshake }, { id: "commitments", label: "COMMITMENTS", icon: Target },
  { id: "initiative", label: "INITIATIVE", icon: Clock3 }, { id: "traits", label: "LEARNED", icon: Brain },
  { id: "history", label: "HISTORY", icon: History }, { id: "privacy", label: "PRIVACY", icon: Shield },
];

export default function SoulStudioPanel({ primary, secondary }: { primary: string; secondary: string }) {
  const [view, setView] = useState<View>("identity"); const [soul, setSoul] = useState<Soul | null>(null);
  const [loading, setLoading] = useState(true); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  const refresh = useCallback(async () => { setLoading(true); try { const r = await fetch("/api/hud/soul"); const j = await r.json(); if (!r.ok || !j.ok) throw new Error(j.error || "Soul unavailable"); setSoul(j.soul); setError(""); } catch (e) { setError(e instanceof Error ? e.message : "Soul unavailable"); } finally { setLoading(false); } }, []);
  useEffect(() => { refresh(); }, [refresh]);
  const mutate = async (payload: Record<string, unknown>) => { if (!soul && payload.operation !== "runtime") return; setBusy(true); try { const r = await fetch("/api/hud/soul", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...payload, expected_revision: soul?.revision }) }); const j = await r.json(); if (r.status === 409) { await refresh(); throw new Error("Soul changed elsewhere. Reloaded the latest revision."); } if (!r.ok || !j.ok) throw new Error(j.error || "Update failed"); setSoul(j.soul); setError(""); } catch (e) { setError(e instanceof Error ? e.message : "Update failed"); } finally { setBusy(false); } };
  const card: React.CSSProperties = { border: "1px solid rgba(255,255,255,.09)", background: "rgba(255,255,255,.025)", borderRadius: 12, padding: 14 };
  const button: React.CSSProperties = { border: `1px solid ${primary}66`, background: `${primary}18`, color: primary, borderRadius: 8, padding: "7px 11px", cursor: "pointer", fontFamily: "var(--font-mono)", fontSize: 10 };
  if (loading) return <div style={card}>LOADING SOUL STATE…</div>;
  if (!soul) return <div style={card}><div style={{ color: "#ff6875" }}>{error || "Soul state unavailable."}</div><button style={button} onClick={refresh}>RETRY</button></div>;
  const traitNames = ["warmth", "humor", "formality", "directness", "challenge", "initiative"];
  return <div className="soul-studio-layout" style={{ display: "grid", gridTemplateColumns: "180px minmax(0,1fr)", gap: 16, minHeight: 500 }}>
    <aside style={{ ...card, padding: 8, display: "flex", flexDirection: "column", gap: 5 }}>
      <div style={{ padding: 9, color: secondary, fontFamily: "var(--font-mono)", fontSize: 9, letterSpacing: ".15em" }}>BROTHER-GUARDIAN · REV {soul.revision}</div>
      {VIEWS.map(x => { const I=x.icon; const active=view===x.id; return <button key={x.id} onClick={()=>setView(x.id)} style={{ display:"flex", gap:8, alignItems:"center", padding:"9px 10px", borderRadius:8, border:`1px solid ${active?primary:"transparent"}`, background:active?`${primary}18`:"transparent", color:active?primary:"rgba(240,237,232,.68)", cursor:"pointer", fontSize:10, fontFamily:"var(--font-mono)" }}><I size={13}/>{x.label}</button>; })}
    </aside>
    <section style={{ minWidth: 0 }}>
      {(error || soul.recovery || soul.degraded) && <div style={{ ...card, marginBottom: 10, color: error ? "#ff6875" : "#f3bd58" }}>{error || soul.recovery || soul.degraded}</div>}
      {view === "identity" && <div style={{ display:"grid", gap:10 }}><div style={card}><b>{String(soul.identity.archetype)}</b><p style={{opacity:.68}}>{String(soul.identity.summary)}</p></div>{traitNames.map(name=>{const x=soul.identity[name] as Range; return <label key={name} style={card}><div style={{display:"flex",justifyContent:"space-between"}}><span>{name.toUpperCase()}</span><b style={{color:primary}}>{x.value.toFixed(2)}</b></div><input aria-label={name} type="range" min={x.minimum} max={x.maximum} step="0.01" value={x.value} onChange={e=>setSoul({...soul,identity:{...soul.identity,[name]:{...x,value:Number(e.target.value)}}})} onMouseUp={()=>mutate({operation:"identity",values:{[name]:(soul.identity[name] as Range).value}})} style={{width:"100%"}}/></label>})}</div>}
      {view === "affect" && <div style={{display:"grid",gridTemplateColumns:"repeat(2,minmax(0,1fr))",gap:10}}>{Object.entries(soul.affect.dimensions).map(([name,x])=><div key={name} style={card}><div style={{display:"flex",justifyContent:"space-between"}}><b>{name.toUpperCase()}</b><span style={{color:primary}}>{x.value.toFixed(2)}</span></div><div style={{height:5,background:"rgba(255,255,255,.08)",margin:"10px 0"}}><div style={{height:"100%",width:`${x.value*100}%`,background:primary}}/></div><small>baseline {x.baseline.toFixed(2)} · today {x.daily_delta>=0?"+":""}{x.daily_delta.toFixed(2)}</small></div>)}<div style={{...card,gridColumn:"1/-1"}}>{soul.affect.framing}<div style={{opacity:.6,marginTop:8}}>{soul.affect.causes.join(" · ")||"No recorded causes."}</div></div></div>}
      {view === "relationship" && <div style={{display:"grid",gap:8}}><div style={card}>STAGE · <b style={{color:primary}}>{soul.relationship.stage.toUpperCase()}</b> · {soul.relationship.contradictions.length} contradictions</div>{soul.relationship.claims.length===0?<div style={card}>No evidence-backed relationship claims yet.</div>:soul.relationship.claims.map(c=><div key={c.id} style={card}><div style={{display:"flex",justifyContent:"space-between"}}><b>{c.kind} · {c.subject}</b><span>{c.status} · {c.confidence.toFixed(2)}</span></div><p>{c.value}</p><button style={button} onClick={()=>mutate({operation:"forget_relationship",subject:c.subject})}><Trash2 size={11}/> FORGET SUBJECT</button></div>)}</div>}
      {view === "commitments" && <div style={{display:"grid",gap:8}}>{(soul.commitments||[]).length===0?<div style={card}>No active projected commitments.</div>:(soul.commitments||[]).map((x,i)=><div key={i} style={card}>{x}</div>)}</div>}
      {view === "initiative" && <div style={{display:"grid",gap:10}}><div style={card}><label><input type="checkbox" checked={soul.initiative_policy.enabled} onChange={e=>mutate({operation:"initiative",values:{enabled:e.target.checked}})}/> ENABLE INITIATIVE</label><div style={{marginTop:8}}>Used today: {soul.initiative_policy.interruptions_today}/{soul.initiative_policy.daily_budget}</div></div>{["timezone","quiet_start","quiet_end","daily_budget"].map(k=><label key={k} style={card}>{k.toUpperCase()}<input value={String((soul.initiative_policy as unknown as Record<string,unknown>)[k]??"")} onChange={e=>setSoul({...soul,initiative_policy:{...soul.initiative_policy,[k]:k==="daily_budget"?Number(e.target.value):e.target.value}})} onBlur={()=>mutate({operation:"initiative",values:{[k]:(soul.initiative_policy as unknown as Record<string,unknown>)[k]}})} style={{display:"block",width:"100%",marginTop:7}}/></label>)}</div>}
      {view === "traits" && <div style={{display:"grid",gap:8}}>{soul.learned_traits.length===0?<div style={card}>No learned traits.</div>:soul.learned_traits.map(t=><div key={t.id} style={card}><b>{t.name}</b><span style={{float:"right"}}>{t.status} · {t.confidence.toFixed(2)}</span><p>{t.value}</p>{t.status==="candidate"&&<div style={{display:"flex",gap:8}}><button style={button} onClick={()=>mutate({operation:"trait",trait_id:t.id,decision:"accept"})}>ACCEPT</button><button style={{...button,color:"#ff6875"}} onClick={()=>mutate({operation:"trait",trait_id:t.id,decision:"reject"})}>REJECT</button></div>}</div>)}</div>}
      {view === "history" && <div style={{display:"grid",gap:7}}>{soul.history.length===0?<div style={card}>No Soul mutations recorded.</div>:soul.history.slice().reverse().map((h,i)=><div key={i} style={card}><b>{h.event}</b><span style={{float:"right",opacity:.55}}>rev {h.revision}</span><div style={{opacity:.7,marginTop:5}}>{h.reason} · {h.timestamp}</div></div>)}</div>}
      {view === "privacy" && <div style={{display:"grid",gap:10}}><div style={card}><label><input type="checkbox" checked={soul.runtime_enabled} onChange={e=>mutate({operation:"runtime",enabled:e.target.checked})}/> SOUL RUNTIME</label></div>{Object.entries(soul.privacy).map(([k,v])=><label key={k} style={card}><input type="checkbox" checked={v} onChange={e=>mutate({operation:"privacy",values:{[k]:e.target.checked}})}/> {k.replaceAll("_"," ").toUpperCase()}</label>)}<div style={{...card,display:"flex",gap:8,flexWrap:"wrap"}}><button style={button} onClick={()=>window.open("/api/hud/soul/export","_blank")}><Download size={11}/> EXPORT</button><button style={button} onClick={()=>mutate({operation:"undo"})}><RotateCcw size={11}/> UNDO</button>{["affect","relationship","learned_traits","all"].map(x=><button key={x} style={{...button,color:x==="all"?"#ff6875":primary}} onClick={()=>window.confirm(`Reset ${x}?`)&&mutate({operation:"reset",scope:x})}>RESET {x.toUpperCase()}</button>)}</div><details style={card}><summary>CANONICAL CONTEXT PREVIEW</summary><pre style={{whiteSpace:"pre-wrap",fontSize:10,maxHeight:260,overflow:"auto"}}>{soul.context_preview}</pre></details></div>}
      {busy&&<div role="status" aria-live="polite" style={{position:"sticky",bottom:0,padding:8,background:"rgba(0,0,0,.8)",color:primary}}>SAVING REVISION…</div>}
    </section>
    <style jsx>{`@media (max-width: 700px) { .soul-studio-layout { grid-template-columns: minmax(0, 1fr) !important; } }`}</style>
  </div>;
}
