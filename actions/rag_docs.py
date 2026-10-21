"""RAG & Document Generation — Phase 6.4: Obsidian vault sync, file_processor → RAG index, generate docs."""
import pathlib, json, hashlib

INDEX = pathlib.Path("memory/rag_index.json")

def _chunk(text: str, size: int = 800):
    words=text.split()
    cur=[]
    out=[]
    for w in words:
        cur.append(w)
        if len(" ".join(cur)) > size:
            out.append(" ".join(cur))
            cur=[]
    if cur: out.append(" ".join(cur))
    return out

def rag_docs(parameters: dict, player=None, **_):
    action=str(parameters.get("action","") or "").strip().lower()
    if action=="index":
        path=str(parameters.get("path") or parameters.get("vault") or "memory").strip()
        p=pathlib.Path(path).expanduser()
        if not p.exists(): return f"Path {p} not found"
        files=list(p.rglob("*.md"))[:100] + list(p.rglob("*.txt"))[:100]
        if not files: return f"No docs in {p}"
        idx=[]
        for f in files[:80]:
            try:
                txt=f.read_text(encoding="utf-8", errors="ignore")
                for i,ch in enumerate(_chunk(txt)):
                    idx.append({"file": str(f), "chunk": i, "text": ch[:1000], "hash": hashlib.md5(ch.encode()).hexdigest()[:8]})
            except: pass
        INDEX.parent.mkdir(parents=True, exist_ok=True)
        INDEX.write_text(json.dumps(idx, indent=2), encoding="utf-8")
        if player: player.write_log(f"[RAG] Indexed {len(idx)} chunks from {len(files)} files")
        return f"Indexed {len(idx)} chunks from {len(files)} files → {INDEX}"
    if action=="search":
        q=str(parameters.get("query") or parameters.get("q") or "").strip()
        if not q: return "Need query"
        if not INDEX.exists(): return "No index — run index first"
        idx=json.loads(INDEX.read_text())
        ql=q.lower().split()
        hits=[]
        for c in idx:
            score=sum(1 for w in ql if w in c["text"].lower())
            if score>0: hits.append((score,c))
        hits.sort(key=lambda x: x[0], reverse=True)
        top=hits[:8]
        if not top: return f"No hits for '{q}'"
        out="\n".join(f"  [{h[0]}] {h[1]['file']}#{h[1]['chunk']}: {h[1]['text'][:200]}" for h in top)
        if player: player.show_content("RAG SEARCH", out)
        return out
    if action=="generate":
        prompt=str(parameters.get("prompt") or parameters.get("topic") or "").strip()
        if not prompt: return "Need prompt/topic to generate doc"
        # Use provider for generation
        try:
            from core.provider import text as prov_text
            query=str(parameters.get("context","") or "")
            ctx=""
            if INDEX.exists():
                # cheap retrieval
                idx=json.loads(INDEX.read_text())
                ql=prompt.lower().split()
                hits=[]
                for c in idx:
                    score=sum(1 for w in ql if w in c["text"].lower())
                    if score>0: hits.append((score,c))
                hits.sort(key=lambda x: x[0], reverse=True)
                ctx="\n".join(h[1]["text"] for h in hits[:3])
            full_prompt=f"Generate a well-structured document for: {prompt}\n\nContext:\n{ctx[:3000]}\n\n{query[:1000]}"
            doc=prov_text(full_prompt, tier="smart", default="")
            if not doc: doc=f"# {prompt}\n\n(Draft — LLM unavailable, fill from context)\n\n{ctx[:2000]}"
            out_path=pathlib.Path(str(parameters.get("out", f"memory/generated_{int(__import__('time').time())}.md"))).expanduser()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(doc, encoding="utf-8")
            if player: player.show_content("GENERATED DOC", doc[:3000])
            return f"Generated → {out_path} ({len(doc)} chars)"
        except Exception as e: return f"Generate failed: {e}"
    return "RAG: index (path/vault), search (query), generate (prompt, out, context)"

TOOL={
    "name":"rag_docs",
    "description":"RAG & Document Generation: Obsidian vault sync, file_processor → RAG index, generate docs. Actions: index, search, generate.",
    "parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"index|search|generate"},"path":{"type":"STRING"},"vault":{"type":"STRING"},"query":{"type":"STRING"},"q":{"type":"STRING"},"prompt":{"type":"STRING","description":"Topic to generate"},"topic":{"type":"STRING"},"out":{"type":"STRING","description":"Output file path"},"context":{"type":"STRING"}},"required":["action"]},"handler":rag_docs
}
