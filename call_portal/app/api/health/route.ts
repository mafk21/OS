import { NextResponse } from "next/server";
import { db } from "../../../lib/server";

export async function GET(){
  try {
    const { count, error } = await db().from("jarvis_call_subscriptions").select("id", { count: "exact", head: true });
    if (error) throw error;
    return NextResponse.json({ ok: true, database: true, paired_devices: count || 0 }, { headers: { "Cache-Control": "no-store" } });
  } catch {
    return NextResponse.json({ ok: false, database: false, paired_devices: 0 }, { status: 503, headers: { "Cache-Control": "no-store" } });
  }
}
