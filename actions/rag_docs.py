"""RAG & Document Generation — Phase 6.4: Obsidian/folder indexing, ranked search & synthesis."""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
import time

INDEX = pathlib.Path("memory/rag_index.json")
SUPPORTED_EXTS = (".md", ".txt", ".rst", ".py", ".json", ".csv", ".html")
_SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"}


def _chunk(text: str, size: int = 800) -> list[str]:
    words = text.split()
    cur: list[str] = []
    out: list[str] = []
    cur_len = 0
    for w in words:
        cur.append(w)
        cur_len += len(w) + 1
        if cur_len > size:
            out.append(" ".join(cur))
            cur = []
            cur_len = 0
    if cur:
        out.append(" ".join(cur))
    return out


def _score_chunk(query: str, chunk_text: str, file_path: str = "") -> float:
    q_clean = query.strip().lower()
    terms = [t for t in re.findall(r"[a-z0-9_]+", q_clean) if len(t) >= 2]
    if not terms:
        return 0.0
    hay = chunk_text.lower()
    fname = pathlib.Path(file_path).name.lower()
    score = 0.0
    if q_clean in hay:
        score += 4.0
    for t in terms:
        cnt = hay.count(t)
        if cnt:
            score += 1.0 + min(cnt, 5) * 0.25
        if t in fname:
            score += 1.5
    return score


def rag_docs(parameters: dict, player=None, **_) -> str:
    action = str((parameters or {}).get("action", "") or "").strip().lower()

    if action == "index":
        path = str(parameters.get("path") or parameters.get("vault") or "memory").strip()
        p = pathlib.Path(path).expanduser()
        if not p.exists():
            return f"Path {p} not found"
        files: list[pathlib.Path] = []
        if p.is_file():
            files = [p]
        else:
            for candidate in p.rglob("*"):
                if len(files) >= 150:
                    break
                if not candidate.is_file():
                    continue
                if any(part in _SKIP_DIRS for part in candidate.parts):
                    continue
                if candidate.suffix.lower() in SUPPORTED_EXTS and candidate.resolve() != INDEX.resolve():
                    files.append(candidate)
        if not files:
            return f"No indexable documents ({', '.join(SUPPORTED_EXTS)}) in {p}"
        idx = []
        for f in files[:120]:
            try:
                txt = f.read_text(encoding="utf-8", errors="ignore")
                for i, ch in enumerate(_chunk(txt)):
                    idx.append({
                        "file": str(f),
                        "chunk": i,
                        "text": ch[:1000],
                        "hash": hashlib.sha256(ch.encode("utf-8", errors="ignore")).hexdigest()[:8],
                    })
            except Exception:
                pass
        INDEX.parent.mkdir(parents=True, exist_ok=True)
        INDEX.write_text(json.dumps(idx, indent=2), encoding="utf-8")
        if player and hasattr(player, "write_log"):
            player.write_log(f"[RAG] Indexed {len(idx)} chunks from {len(files)} files")
        return f"Indexed {len(idx)} chunks from {len(files)} files → {INDEX}"

    if action == "search":
        q = str(parameters.get("query") or parameters.get("q") or "").strip()
        if not q:
            return "Need query"
        if not INDEX.exists():
            return "No index — run action=index first"
        idx = json.loads(INDEX.read_text(encoding="utf-8"))
        hits = []
        for c in idx:
            sc = _score_chunk(q, c.get("text", ""), c.get("file", ""))
            if sc > 0:
                hits.append((sc, c))
        hits.sort(key=lambda x: x[0], reverse=True)
        top = hits[:8]
        if not top:
            return f"No hits for '{q}'"
        out = "\n".join(
            f"  [{sc:.1f}] {c['file']}#{c['chunk']}: {c['text'][:220]}"
            for sc, c in top
        )
        if player and hasattr(player, "show_content"):
            player.show_content("RAG SEARCH", out)
        return out

    if action == "generate":
        prompt = str(parameters.get("prompt") or parameters.get("topic") or "").strip()
        if not prompt:
            return "Need prompt/topic to generate doc"
        try:
            from core.provider import text as prov_text
            query = str(parameters.get("context", "") or "")
            ctx = ""
            if INDEX.exists():
                idx = json.loads(INDEX.read_text(encoding="utf-8"))
                hits = [
                    (_score_chunk(prompt, c.get("text", ""), c.get("file", "")), c)
                    for c in idx
                ]
                hits = [h for h in hits if h[0] > 0]
                hits.sort(key=lambda x: x[0], reverse=True)
                ctx = "\n\n".join(
                    f"[Source: {h[1]['file']}]\n{h[1]['text']}" for h in hits[:4]
                )
            full_prompt = (
                f"Generate a clear, well-structured Markdown document for: {prompt}\n\n"
                f"Retrieved local context:\n{ctx[:3500]}\n\n{query[:1000]}"
            )
            doc = prov_text(full_prompt, tier="smart", default="")
            if not doc:
                doc = f"# {prompt}\n\n(Draft — LLM unavailable, retrieved context below)\n\n{ctx[:2000]}"
            out_path = pathlib.Path(
                str(parameters.get("out", f"memory/generated_{int(time.time())}.md"))
            ).expanduser()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(doc, encoding="utf-8")
            if player and hasattr(player, "show_content"):
                player.show_content("GENERATED DOC", doc[:3000])
            return f"Generated → {out_path} ({len(doc)} chars)"
        except Exception as e:
            return f"Generate failed: {e}"

    return "RAG: index (path/vault), search (query), generate (prompt, out, context)"


TOOL = {
    "name": "rag_docs",
    "description": (
        "RAG & Document Generation: index local folders/Obsidian vaults "
        "(.md/.txt/.rst/.py/.json/.csv/.html), run ranked semantic/keyword "
        "search, and generate grounded Markdown documents. Actions: index, "
        "search, generate."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "index|search|generate"},
            "path": {"type": "STRING"},
            "vault": {"type": "STRING"},
            "query": {"type": "STRING"},
            "q": {"type": "STRING"},
            "prompt": {"type": "STRING", "description": "Topic to generate"},
            "topic": {"type": "STRING"},
            "out": {"type": "STRING", "description": "Output file path"},
            "context": {"type": "STRING"},
        },
        "required": ["action"],
    },
    "handler": rag_docs,
}
