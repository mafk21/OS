import { NextResponse } from "next/server";
import { clean, db, pairing, sender } from "../../../../lib/server";
function allowed(req:Request){return pairing(req)||sender(req)}
export async function GET(req:Request,ctx:{params:Promise<{id:string}>}){
 if(!allowed(req)) return NextResponse.json({error:"Unauthorized"},{status:401}); const {id}=await ctx.params; const client=db();
 const {data:session}=await client.from("jarvis_call_sessions").select("id,status,reason,created_at,answered_at,ended_at,expires_at").eq("id",id).single();
 if(!session) return NextResponse.json({error:"Call not found"},{status:404});
 const {data:messages}=await client.from("jarvis_call_messages").select("id,sender,body,created_at").eq("session_id",id).order("id");
 return NextResponse.json({ok:true,session,messages:messages||[]});
}
export async function POST(req:Request,ctx:{params:Promise<{id:string}>}){
 if(!allowed(req)) return NextResponse.json({error:"Unauthorized"},{status:401}); const {id}=await ctx.params, body=await req.json().catch(()=>({})), action=clean(body.action,20), client=db();
 if(action==="answer"){await client.from("jarvis_call_sessions").update({status:"answered",answered_at:new Date().toISOString()}).eq("id",id).eq("status","ringing");}
 else if(action==="end"){await client.from("jarvis_call_sessions").update({status:"ended",ended_at:new Date().toISOString()}).eq("id",id);}
 else if(action==="reply"){const text=clean(body.message);if(!text)return NextResponse.json({error:"message required"},{status:400});await client.from("jarvis_call_messages").insert({session_id:id,sender:pairing(req)?"user":"jarvis",body:text});}
 else return NextResponse.json({error:"Unsupported action"},{status:400});
 return NextResponse.json({ok:true});
}
