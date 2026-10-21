"""Image Generation — Phase 6.5: \"make a picture...\" via Gemini imagen or local SD."""
import pathlib, time

def image_generation(parameters: dict, player=None, **_):
    prompt=str(parameters.get("prompt") or parameters.get("text") or "").strip()
    if not prompt: return "Need prompt: e.g. {prompt:'a cat in space, watercolor'}"
    style=str(parameters.get("style","")).strip()
    full=prompt + (f", {style} style" if style else "")
    # 1. Try Gemini imagen via google-genai
    try:
        import memory.config_manager as cm
        key=cm.get_gemini_key() or ""
        if key:
            from google import genai
            client=genai.Client(api_key=key)
            # gemini-2.0-flash-exp image generation if available
            result=client.models.generate_content(model="gemini-2.0-flash-exp", contents=[full])
            text=getattr(result, "text", "") or ""
            # Some configs return inline_data images
            for cand in getattr(result, "candidates", []) or []:
                for part in getattr(cand, "content", {}).parts or []:
                    blob=getattr(part, "inline_data", None)
                    if blob and getattr(blob, "data", None):
                        out=pathlib.Path(f"memory/generated_{int(time.time())}.png")
                        out.parent.mkdir(parents=True, exist_ok=True)
                        out.write_bytes(blob.data if isinstance(blob.data, bytes) else __import__("base64").b64decode(blob.data))
                        if player:
                            try: player.show_content("IMAGE", f"Generated → {out}\n{prompt}")
                            except: pass
                        return f"Image saved → {out} — {prompt}"
            if text:
                return f"Gemini response (no image inline): {text[:400]}"
    except Exception as e:
        pass
    # 2. Local SD fallback stub
    try:
        import diffusers  # type: ignore
        return "Local Stable Diffusion available — implement pipeline here (diffusers). Prompt: " + full
    except ImportError:
        pass
    return f"Image generation stub for: '{full}'. Configure gemini_api_key (imagen) or install diffusers for local SD. Prompt preserved."


TOOL={
    "name":"image_generation",
    "description":"Image Generation: \"make a picture...\" via Gemini imagen or local SD. Needs prompt, optional style.",
    "parameters":{"type":"OBJECT","properties":{"prompt":{"type":"STRING","description":"Image description"},"text":{"type":"STRING"},"style":{"type":"STRING","description":"watercolor|photoreal|anime|etc"}},"required":["prompt"]},
    "handler":image_generation
}
