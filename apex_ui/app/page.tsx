"use client";

import ApexWorld from "@/components/ApexWorld";
import ApexOverviewPanel from "@/components/ApexOverviewPanel";
import { JarvisProvider, useJarvis } from "@/components/JarvisBridge";
import JarvisHudOverlays from "@/components/JarvisHudOverlays";

function HudShell() {
  const { theme } = useJarvis();
  return (
    <main
      id="main"
      style={{
        background: theme.pageBg,
        color: "#f0ede8",
        position: "relative",
        overflow: "hidden",
        transition: "background 0.6s ease",
      }}
    >
      <ApexOverviewPanel />

      <section
        style={{ position: "relative", height: "100vh", minHeight: 620 }}
      >
        <ApexWorld />
      </section>

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
