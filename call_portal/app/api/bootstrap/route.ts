import { NextResponse } from "next/server";
import { pairing } from "../../../lib/server";

/** One-time native-client bootstrap. The pairing code proves physical/browser
 * ownership; the sender secret is then stored owner-only by the JARVIS host. */
export async function POST(req: Request) {
  if (!pairing(req)) return NextResponse.json({ error: "Invalid pairing code" }, { status: 401 });
  const secret = process.env.CALL_SECRET;
  if (!secret) return NextResponse.json({ error: "Server is not configured" }, { status: 503 });
  return NextResponse.json({ call_secret: secret }, { headers: { "Cache-Control": "no-store" } });
}
