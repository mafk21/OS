"use client";

import { useEffect, useState } from "react";
import ApexWorld from "./reference/ApexWorld";
import { useJarvis } from "./JarvisBridge";

/** Transport adapter only: the reference owns all visual layout and animation. */
export default function ApexReferenceWorld() {
  const { connected, orbState, trace, tapOrb, consoleOpen, setConsoleOpen } = useJarvis();

  const [female, setFemale] = useState(true);
  useEffect(() => {
    try { const saved=localStorage.getItem("apex.figure"); if(saved) setFemale(saved==="female"); } catch {}
  }, []);
  const selectFigure = (value: boolean) => { setFemale(value); try { localStorage.setItem("apex.figure", value?"female":"orb"); } catch {} };

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.ctrlKey && event.key === "Enter") {
        event.preventDefault();
        setConsoleOpen((open) => !open);
      } else if (event.key === "Escape" && consoleOpen) {
        setConsoleOpen(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [consoleOpen, setConsoleOpen]);

  return <>
  <div role="group" aria-label="Interface figure" style={{position:"fixed",right:"clamp(16px,3vw,40px)",bottom:24,zIndex:35,display:"flex",gap:3,padding:4,border:"1px solid #76d8f52b",borderRadius:24,background:"#07111fc9",backdropFilter:"blur(12px)"}}>
    {([false,true] as const).map(value=><button key={String(value)} aria-pressed={female===value} onClick={()=>selectFigure(value)} style={{border:0,borderRadius:20,padding:"9px 14px",fontFamily:"var(--font-mono)",fontSize:9,letterSpacing:".15em",cursor:"pointer",color:female===value?"#c5f5ff":"#6f879b",background:female===value?"#4abce51c":"transparent"}}>{value?"HUMAN · FEMALE":"APEX · ORB"}</button>)}
  </div>
  <ApexWorld
    female={female}
    liveState={connected ? (orbState === "listening" ? "idle" : orbState) : undefined}
    liveTrace={connected ? trace : undefined}
    onTap={tapOrb}
    onOpenControls={() => setConsoleOpen(true)}
  /></>;
}
