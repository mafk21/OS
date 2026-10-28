import type { Metadata, Viewport } from "next";
import "./style.css";
export const metadata: Metadata = { title: "JARVIS Call", description: "Private voice calls from your JARVIS", manifest: "/manifest.webmanifest", appleWebApp: { capable: true, title: "JARVIS Call", statusBarStyle: "black-translucent" } };
export const viewport: Viewport = { themeColor: "#050b13" };
export default function Layout({children}:{children:React.ReactNode}) { return <html lang="en"><body>{children}</body></html>; }
