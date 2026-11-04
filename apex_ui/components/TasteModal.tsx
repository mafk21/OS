"use client";

import { useMemo, useState } from "react";
import { X, Trash2, Plus, Sparkles } from "lucide-react";
import { useJarvis } from "./JarvisBridge";

const LABELS: Record<string, string> = {
  music: "Music", food: "Food", drinks: "Drinks", entertainment: "Movies, series & games",
  style: "Style & design", travel: "Travel", other: "Other",
};

export default function TasteModal() {
  const { tasteProfile, tasteModalOpen, setTasteModalOpen, updateTasteProfile, theme } = useJarvis();
  const firstRun = tasteProfile.prompt_pending;
  const open = firstRun || tasteModalOpen;
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [domain, setDomain] = useState("music");
  const [item, setItem] = useState("");
  const [sentiment, setSentiment] = useState("like");
  const [busy, setBusy] = useState(false);
  const grouped = useMemo(() => {
    const result: Record<string, typeof tasteProfile.entries> = {};
    for (const entry of tasteProfile.entries) (result[entry.domain] ||= []).push(entry);
    return result;
  }, [tasteProfile.entries]);
  if (!open) return null;

  const close = () => { if (!firstRun) setTasteModalOpen(false); };
  const saveOnboarding = async () => {
    setBusy(true);
    await updateTasteProfile("save_onboarding", { values: answers });
    setBusy(false); setTasteModalOpen(false);
  };
  const skip = async () => {
    setBusy(true); await updateTasteProfile("skip"); setBusy(false); setTasteModalOpen(false);
  };
  const add = async () => {
    if (!item.trim()) return;
    setBusy(true);
    await updateTasteProfile("add", { domain, item: item.trim(), sentiment, kind: "preference", contexts: [] });
    setItem(""); setBusy(false);
  };

  const inputStyle = {
    width: "100%", boxSizing: "border-box" as const, background: theme.inputBg,
    border: `1px solid ${theme.primaryBorder}`, borderRadius: 9, padding: "9px 10px",
    color: "#f0ede8", fontSize: 12, outline: "none",
  };
  const buttonStyle = {
    border: `1px solid ${theme.primaryBorder}`, borderRadius: 18, padding: "8px 13px",
    background: theme.barBg, color: theme.primary, cursor: "pointer", fontSize: 11,
    fontFamily: "var(--font-mono)", letterSpacing: ".08em",
  };

  return <div role="dialog" aria-modal="true" aria-label="JARVIS Taste Profile" onClick={close}
    style={{position:"fixed",inset:0,zIndex:92,background:"rgba(2,6,12,.82)",backdropFilter:"blur(12px)",display:"flex",alignItems:"center",justifyContent:"center",padding:16}}>
    <div onClick={e=>e.stopPropagation()} style={{width:"min(720px,96vw)",maxHeight:"88vh",overflowY:"auto",background:theme.panelBg,border:`1px solid ${theme.primary}55`,borderRadius:18,padding:22,boxShadow:`0 0 55px ${theme.primary}20`}}>
      <div style={{display:"flex",alignItems:"center",gap:10}}>
        <Sparkles size={18} color={theme.primary}/><div style={{flex:1}}>
          <div style={{color:theme.primary,fontFamily:"var(--font-mono)",fontSize:10,letterSpacing:".2em"}}>PERSONAL TASTE · PRIVATE & ENCRYPTED</div>
          <h2 style={{margin:"6px 0 0",fontSize:22,color:"#f0ede8"}}>{firstRun ? "What do you enjoy?" : "Taste Profile"}</h2>
        </div>
        {!firstRun && <button aria-label="Close" onClick={close} style={{background:"none",border:0,color:"#aaa",cursor:"pointer"}}><X/></button>}
      </div>
      <p style={{color:"rgba(240,237,232,.65)",fontSize:12,lineHeight:1.55}}>
        JARVIS uses only preferences you explicitly provide. They stay encrypted on this device, can be changed anytime, and are never used to infer sensitive traits.
      </p>

      {firstRun ? <>
        <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(210px,1fr))",gap:10}}>
          {["music","food","drinks","entertainment","style","travel"].map(key => <label key={key} style={{color:"rgba(240,237,232,.72)",fontSize:11}}>
            {LABELS[key]} you like
            <input value={answers[key]||""} onChange={e=>setAnswers({...answers,[key]:e.target.value})} placeholder="Separate items with commas" style={{...inputStyle,marginTop:5}}/>
          </label>)}
          <label style={{color:"rgba(240,237,232,.72)",fontSize:11}}>Things you dislike
            <input value={answers.dislikes||""} onChange={e=>setAnswers({...answers,dislikes:e.target.value})} placeholder="Anything you prefer to avoid" style={{...inputStyle,marginTop:5}}/>
          </label>
          <label style={{color:"rgba(240,237,232,.72)",fontSize:11}}>Food restrictions
            <input value={answers.restrictions||""} onChange={e=>setAnswers({...answers,restrictions:e.target.value})} placeholder="Optional — allergies, dietary rules" style={{...inputStyle,marginTop:5}}/>
          </label>
        </div>
        <div style={{display:"flex",justifyContent:"flex-end",gap:9,marginTop:18}}>
          <button disabled={busy} onClick={skip} style={{...buttonStyle,color:"rgba(240,237,232,.65)"}}>IGNORE FOR NOW</button>
          <button disabled={busy} onClick={saveOnboarding} style={{...buttonStyle,background:theme.primary,color:"#061016",fontWeight:700}}>{busy?"SAVING…":"SAVE MY TASTE"}</button>
        </div>
      </> : <>
        <div style={{display:"grid",gridTemplateColumns:"140px 1fr 120px auto",gap:8,alignItems:"end"}}>
          <label style={{fontSize:10,color:"#aaa"}}>CATEGORY<select value={domain} onChange={e=>setDomain(e.target.value)} style={{...inputStyle,marginTop:4}}>{tasteProfile.domains.map(d=><option key={d} value={d}>{LABELS[d]||d}</option>)}</select></label>
          <label style={{fontSize:10,color:"#aaa"}}>PREFERENCE<input value={item} onChange={e=>setItem(e.target.value)} onKeyDown={e=>{if(e.key==="Enter")add();}} style={{...inputStyle,marginTop:4}}/></label>
          <label style={{fontSize:10,color:"#aaa"}}>FEELING<select value={sentiment} onChange={e=>setSentiment(e.target.value)} style={{...inputStyle,marginTop:4}}>{["favorite","like","neutral","avoid","dislike"].map(x=><option key={x}>{x}</option>)}</select></label>
          <button disabled={busy||!item.trim()} onClick={add} style={buttonStyle}><Plus size={13}/></button>
        </div>
        <div style={{marginTop:18,display:"flex",flexDirection:"column",gap:12}}>
          {Object.entries(grouped).map(([key,entries])=><div key={key}><div style={{color:theme.primary,fontSize:10,fontFamily:"var(--font-mono)",letterSpacing:".15em",marginBottom:5}}>{(LABELS[key]||key).toUpperCase()}</div>
            {entries.map(entry=><div key={entry.id} style={{display:"flex",alignItems:"center",gap:8,padding:"7px 9px",borderBottom:"1px solid rgba(255,255,255,.06)",color:"#eee",fontSize:12}}>
              <span style={{opacity:.6,width:70}}>{entry.kind === "restriction" ? "restriction" : entry.sentiment}</span><span style={{flex:1}}>{entry.item}</span>
              <button aria-label={`Remove ${entry.item}`} onClick={()=>updateTasteProfile("remove",{entry_id:entry.id})} style={{background:"none",border:0,color:"#ff7b91",cursor:"pointer"}}><Trash2 size={13}/></button>
            </div>)}
          </div>)}
          {!tasteProfile.entries.length && <div style={{color:"#888",fontSize:12}}>No preferences saved yet.</div>}
        </div>
        <div style={{display:"flex",justifyContent:"space-between",marginTop:18}}>
          <button onClick={async()=>{if(window.confirm("Delete every saved taste preference?")) await updateTasteProfile("clear");}} style={{...buttonStyle,color:"#ff7b91",borderColor:"#ff7b9155"}}>CLEAR ALL</button>
          <button onClick={close} style={buttonStyle}>DONE</button>
        </div>
      </>}
    </div>
  </div>;
}
