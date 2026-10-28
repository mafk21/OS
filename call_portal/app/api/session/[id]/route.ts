import { NextResponse } from "next/server";
import { clean, db, pairing, sender } from "../../../../lib/server";
function allowed(req:Request){return pairing(req)||sender(req)}
export async function GET(req:Request,ctx:{params:Promise<{id:string}>}){
 if(!allowed(req)) return NextResponse.json({error:"Unauthorized"},{status:401});
 const {id}=await ctx.params, client=db();
 const {data:session}=await client.from("jarvis_call_sessions").select("id,status,reason,created_at,answered_at,ended_at,expires_at").eq("id",id).single();
 if(!session) return NextResponse.json({error:"Call not found"},{status:404});
 const {data:messages}=await client.from("jarvis_call_messages").select("id,sender,body,created_at").eq("session_id",id).order("id");
 return NextResponse.json({ok:true,session,messages:messages||[]},{headers:{"Cache-Control":"no-store"}});
}
export async function POST(req:Request,ctx:{params:Promise<{id:string}>}){
 if(!allowed(req)) return NextResponse.json({error:"Unauthorized"},{status:401});
 const {id}=await ctx.params, body=await req.json().catch(()=>({})), action=clean(body.action,20), client=db();
 const {data:session}=await client.from("jarvis_call_sessions").select("status,expires_at").eq("id",id).single();
 if(!session) return NextResponse.json({error:"Call not found"},{status:404});
 const expired=session.expires_at&&new Date(session.expires_at).getTime()<=Date.now();
 if(action==="answer"){
  if(expired) return NextResponse.json({error:"This call has expired"},{status:409});
  if(session.status!=="ringing"&&session.status!=="answered") return NextResponse.json({error:"This call can no longer be answered"},{status:409});
  if(session.status==="ringing") await client.from("jarvis_call_sessions").update({status:"answered",answered_at:new Date().toISOString()}).eq("id",id).eq("status","ringing");
 } else if(action==="end"){
  if(session.status!=="ended") await client.from("jarvis_call_sessions").update({status:"ended",ended_at:new Date().toISOString()}).eq("id",id);
 } else if(action==="reply"){
  if(session.status!=="answered"||expired) return NextResponse.json({error:"The call is not active"},{status:409});
  const text=clean(body.message); if(!text) return NextResponse.json({error:"message required"},{status:400});
  const {error}=await client.from("jarvis_call_messages").insert({session_id:id,sender:pairing(req)?"user":"jarvis",body:text});
  if(error) return NextResponse.json({error:"Reply could not be saved"},{status:500});
 } else return NextResponse.json({error:"Unsupported action"},{status:400});
 return NextResponse.json({ok:true});
}
