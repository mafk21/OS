"use client";

import { useEffect, useState } from "react";
import ApexWorld from "@/components/ApexWorld";
import ApexOverviewPanel from "@/components/ApexOverviewPanel";
import DualMonitorConsole from "@/components/DualMonitorConsole";
import { JarvisProvider, useJarvis } from "@/components/JarvisBridge";
import JarvisHudOverlays from "@/components/JarvisHudOverlays";

function HudShell() {
  const { theme, backgroundMode } = useJarvis();
  const [viewMode, setViewMode] = useState<"world" | "console">("world");

  useEffect(() => {
    try {
      const params = new URLSearchParams(window.location.search);
      if (params.get("view") === "console") {
        setViewMode("console");
      }
    } catch {}
  }, []);

  if (viewMode === "console") {
    return <DualMonitorConsole />;
  }

  return (
    <main
      id="main"
      style={{
        background: backgroundMode ? "#03070d" : theme.pageBg,
        color: "#f0ede8",
        position: "relative",
        overflow: "hidden",
        transition: "background 0.45s ease",
      }}
    >
      <div
        style={{
          opacity: backgroundMode ? 0 : 1,
          pointerEvents: backgroundMode ? "none" : "auto",
          transition: "opacity 0.24s ease",
        }}
      >
        <ApexOverviewPanel />

        <section
          style={{ position: "relative", height: "100vh", minHeight: 620 }}
        >
          <ApexWorld />
        </section>
      </div>

      <JarvisHudOverlays />
    </main>
  );
}

export default function Home() {
  return (
    <JarvisProvider>
      <HudShell />
    </JarvisProvider>
  );
}
