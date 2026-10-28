import type { Metadata } from "next";
import "./style.css";
export const metadata: Metadata = { title: "JARVIS Call", description: "Private voice calls from your JARVIS" };
export default function Layout({children}:{children:React.ReactNode}) { return <html lang="en"><body>{children}</body></html>; }
