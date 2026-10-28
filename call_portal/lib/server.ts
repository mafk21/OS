import { createClient } from "@supabase/supabase-js";
import { timingSafeEqual } from "crypto";

export function db() {
  const url=process.env.SUPABASE_URL, key=process.env.SUPABASE_SERVICE_ROLE_KEY;
  if(!url||!key) throw new Error("Server is not configured");
  return createClient(url,key,{auth:{persistSession:false,autoRefreshToken:false}});
}
function same(a:string,b:string){const x=Buffer.from(a),y=Buffer.from(b);return x.length===y.length&&timingSafeEqual(x,y)}
export function pairing(req:Request){return !!process.env.PAIRING_CODE&&same(req.headers.get("x-pairing-code")||"",process.env.PAIRING_CODE)}
export function sender(req:Request){const raw=(req.headers.get("authorization")||"").replace(/^Bearer\s+/i,"");return !!process.env.CALL_SECRET&&same(raw,process.env.CALL_SECRET)}
export function clean(v:unknown,max=2000){return String(v??"").trim().slice(0,max)}
