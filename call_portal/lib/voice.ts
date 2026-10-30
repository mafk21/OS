export type BrowserVoice = Pick<SpeechSynthesisVoice,"name"|"lang"|"default"|"localService">;

const NATURAL=/natural|neural|premium|enhanced|samantha|ava|aria|jenny|guy|google|microsoft|siri/i;
const POOR=/compact|espeak|festival|robot|whisper|zarvox|bells|bubbles|cellos|organ|trinoids|wobble/i;

export function voiceQuality(voice:BrowserVoice,language:string):number{
 const lang=language.toLowerCase(),base=lang.split("-")[0],vlang=voice.lang.toLowerCase();
 return (vlang===lang?45:vlang.startsWith(base)?28:-30)+(voice.localService?8:2)+(voice.default?5:0)+(NATURAL.test(voice.name)?35:0)-(POOR.test(voice.name)?100:0);
}

/** Only expose voices likely to be intelligible in the device language. */
export function clearVoices<T extends BrowserVoice>(voices:T[],language:string):T[]{
 const ranked=[...voices].sort((a,b)=>voiceQuality(b,language)-voiceQuality(a,language)||a.name.localeCompare(b.name));
 const approved=ranked.filter(v=>voiceQuality(v,language)>=28&&!POOR.test(v.name));
 const natural=approved.filter(v=>NATURAL.test(v.name));
 // If natural/enhanced voices exist, do not let a user accidentally select a
 // noticeably robotic fallback. Otherwise keep only the best few system voices.
 return (natural.length?natural:approved.length?approved:ranked.filter(v=>voiceQuality(v,language)>0).slice(0,1)).slice(0,6);
}

export function voiceLabel(voice:BrowserVoice,language:string):string{
 return `${voice.name} · ${voice.lang}${NATURAL.test(voice.name)?" · Natural":" · Clear"}`;
}

export function detectedLanguage(text:string,fallback:string):string{
 if(/[\u0600-\u06ff]/.test(text))return"ar";
 if(/[\u0400-\u04ff]/.test(text))return"ru";
 if(/[\u3040-\u30ff]/.test(text))return"ja";
 if(/[\uac00-\ud7af]/.test(text))return"ko";
 if(/[\u4e00-\u9fff]/.test(text))return"zh";
 if(/[\u0370-\u03ff]/.test(text))return"el";
 return fallback||"en-US";
}

export function speechText(input:string):string{
 return String(input||"")
  .replace(/https?:\/\/\S+/gi," link ")
  .replace(/[*_`#>|~]+/g," ")
  .replace(/\b(?:https?|www)\b/gi," ")
  .replace(/([.!?]){2,}/g,"$1")
  .replace(/\s+([,.;:!?])/g,"$1")
  .replace(/\s+/g," ")
  .trim();
}

/** Mobile speech engines often truncate long utterances. Sentence-sized chunks
 * sound more natural and survive backgrounding better. */
export function speechChunks(input:string,max=160):string[]{
 const text=speechText(input); if(!text)return[];
 const sentences=text.match(/[^.!?]+[.!?]+|[^.!?]+$/g)||[text],out:string[]=[];
 for(const sentence of sentences){
  const clean=sentence.trim(); if(clean.length<=max){out.push(clean);continue}
  const words=clean.split(" ");let part="";
  for(const word of words){if(part&&part.length+word.length+1>max){out.push(part);part=word}else part+=(part?" ":"")+word}
  if(part)out.push(part);
 }
 return out;
}
