import { NextResponse } from "next/server";
import webpush from "web-push";
import { clean, db, sender } from "../../../lib/server";
export async function POST(req:Request){
 if(!sender(req)) return NextResponse.json({error:"Unauthorized"},{status:401});
 const body=await req.json().catch(()=>({})), reason=clean(body.reason,240), message=clean(body.message);
 if(!message) return NextResponse.json({error:"message is required"},{status:400});
 const client=db(); const {data:session,error}=await client.from("jarvis_call_sessions").insert({reason}).select("id").single();
 if(error||!session) return NextResponse.json({error:"Could not create call"},{status:500});
 await client.from("jarvis_call_messages").insert({session_id:session.id,sender:"jarvis",body:message});
 webpush.setVapidDetails("mailto:"+(process.env.VAPID_EMAIL||"admin@example.com"),process.env.NEXT_PUBLIC_VAPID_KEY||"",process.env.VAPID_PRIVATE_KEY||"");
 const {data:subs}=await client.from("jarvis_call_subscriptions").select("id,endpoint,p256dh,auth"); let delivered=0;
 await Promise.all((subs||[]).map(async s=>{try{await webpush.sendNotification({endpoint:s.endpoint,keys:{p256dh:s.p256dh,auth:s.auth}},JSON.stringify({title:"JARVIS is calling",body:reason||"Tap to answer",url:`/?call=${session.id}`,sessionId:session.id}),{TTL:60,urgency:"high"});delivered++}catch(e:any){if(e?.statusCode===404||e?.statusCode===410) await client.from("jarvis_call_subscriptions").delete().eq("id",s.id)}}));
 return NextResponse.json({ok:true,session_id:session.id,notifications:delivered,url:`/?call=${session.id}`});
}
