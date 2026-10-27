"use client";

import { useEffect } from "react";
import ApexWorld from "./reference/ApexWorld";
import { useJarvis } from "./JarvisBridge";

/** Transport adapter only: the reference owns all visual layout and animation. */
export default function ApexReferenceWorld() {
  const { connected, orbState, trace, tapOrb, consoleOpen, setConsoleOpen } = useJarvis();

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

  return <ApexWorld
    liveState={connected ? (orbState === "listening" ? "idle" : orbState) : undefined}
    liveTrace={connected ? trace : undefined}
    onTap={tapOrb}
    onOpenControls={() => setConsoleOpen(true)}
  />;
}
