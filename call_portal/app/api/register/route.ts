import { NextResponse } from "next/server";
import { db, pairing } from "../../../lib/server";
export async function POST(req:Request){
 if(!pairing(req)) return NextResponse.json({error:"Invalid pairing code"},{status:401});
 const body=await req.json().catch(()=>null), sub=body?.subscription;
 if(!sub?.endpoint||!sub?.keys?.p256dh||!sub?.keys?.auth) return NextResponse.json({error:"Invalid push subscription"},{status:400});
 const {error}=await db().from("jarvis_call_subscriptions").upsert({endpoint:String(sub.endpoint),p256dh:String(sub.keys.p256dh),auth:String(sub.keys.auth),user_agent:(req.headers.get("user-agent")||"").slice(0,500),updated_at:new Date().toISOString()},{onConflict:"endpoint"});
 return error?NextResponse.json({error:"Registration failed"},{status:500}):NextResponse.json({ok:true});
}
