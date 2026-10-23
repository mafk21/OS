import ApexWorld from "@/components/ApexWorld";
import ApexOverviewPanel from "@/components/ApexOverviewPanel";
import { JarvisProvider } from "@/components/JarvisBridge";
import JarvisHudOverlays from "@/components/JarvisHudOverlays";

export default function Home() {
  return (
    <JarvisProvider>
      <main
        id="main"
        style={{
          background: "#04080f",
          color: "#f0ede8",
          position: "relative",
          overflow: "hidden",
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
    </JarvisProvider>
  );
}
