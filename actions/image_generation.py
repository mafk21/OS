"""Image Generation — Phase 6.5: \"make a picture...\" via OpenAI DALL-E / Gemini Imagen / local SD."""
import base64
import pathlib
import time


def _try_openai_image(full: str, prompt: str, player=None) -> str | None:
    try:
        from core.openai_compat import openai_generate_image
        out, _err = openai_generate_image(full)
        if out is not None:
            if player:
                try:
                    player.show_content("IMAGE", f"Generated → {out}\n{prompt}")
                except Exception:
                    pass
            return f"Image saved → {out} — {prompt}"
    except Exception:
        pass
    return None


def _try_gemini_image(full: str, prompt: str, key: str, player=None) -> str | None:
    try:
        from google import genai
        client = genai.Client(api_key=key)
        result = client.models.generate_content(model="gemini-2.0-flash-exp", contents=[full])
        text = getattr(result, "text", "") or ""
        for cand in getattr(result, "candidates", []) or []:
            for part in getattr(cand, "content", {}).parts or []:
                blob = getattr(part, "inline_data", None)
                if blob and getattr(blob, "data", None):
                    out = pathlib.Path(f"memory/generated_{int(time.time())}.png")
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(
                        blob.data
                        if isinstance(blob.data, bytes)
                        else base64.b64decode(blob.data)
                    )
                    if player:
                        try:
                            player.show_content("IMAGE", f"Generated → {out}\n{prompt}")
                        except Exception:
                            pass
                    return f"Image saved → {out} — {prompt}"
        if text:
            return f"Gemini response (no image inline): {text[:400]}"
    except Exception:
        pass
    return None


def image_generation(parameters: dict, player=None, **_):
    prompt = str(parameters.get("prompt") or parameters.get("text") or "").strip()
    if not prompt:
        return "Need prompt: e.g. {prompt:'a cat in space, watercolor'}"
    style = str(parameters.get("style", "")).strip()
    full = prompt + (f", {style} style" if style else "")

    import memory.config_manager as cm
    gkey = cm.get_gemini_key() or ""
    okey = cm.get_openai_key() or ""
    pref = cm.get_provider()

    if okey and (pref == "openai" or not gkey):
        res = _try_openai_image(full, prompt, player=player)
        if res:
            return res

    if gkey:
        res = _try_gemini_image(full, prompt, gkey, player=player)
        if res and res.startswith("Image saved"):
            return res
        if okey:
            oai_res = _try_openai_image(full, prompt, player=player)
            if oai_res:
                return oai_res
        if res:
            return res

    # Local SD fallback stub
    try:
        import diffusers  # type: ignore
        return "Local Stable Diffusion available — implement pipeline here (diffusers). Prompt: " + full
    except ImportError:
        pass
    return (
        f"Image generation stub for: '{full}'. "
        "Configure openai_api_key (DALL-E 3), gemini_api_key (Imagen), or install diffusers for local SD."
    )


TOOL={
    "name":"image_generation",
    "description":"Image Generation: \"make a picture...\" via Gemini imagen or local SD. Needs prompt, optional style.",
    "parameters":{"type":"OBJECT","properties":{"prompt":{"type":"STRING","description":"Image description"},"text":{"type":"STRING"},"style":{"type":"STRING","description":"watercolor|photoreal|anime|etc"}},"required":["prompt"]},
    "handler":image_generation
}
