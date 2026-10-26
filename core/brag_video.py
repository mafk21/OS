"""Local Brag-slim workflow adapter. No downloaded code, shell commands or publishing.

Story data -> deterministic motion frames + original soundtrack -> FFmpeg ->
verified MP4. Background jobs persist honest terminal state across restarts.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
import uuid
import wave

BASE = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent
OUTPUT_ROOT = BASE / "memory" / "generated_videos"
_JOBS: dict[str, threading.Event] = {}
_LOCK = threading.RLock()
FORMATS = {"landscape": (1920, 1080), "vertical": (1080, 1920), "square": (1080, 1080)}
TONES = {"default", "polished", "yc-parody", "chaotic", "deadpan", "cinematic", "app-store"}


def _atomic(path: Path, data: dict):
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def _clean(value, limit=180):
    value = re.sub(r"\s+", " ", str(value or "")).strip()
    value = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[private email]", value)
    value = re.sub(r"(?:sk-[\w-]{12,}|AIza[\w-]{20,}|gh[pousr]_[\w]{15,})", "[secret removed]", value)
    value = re.sub(r"https?://\S+", "[link omitted]", value)
    return value[:limit]


def inspect_project(project: str) -> dict:
    """Only explicit public metadata; no recursive crawl or application execution."""
    root = Path(project).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("project_path must be an existing local project directory.")
    result = {"project": str(root), "title": _clean(root.name, 70), "excerpt": "", "sources": []}
    for name in ("README.md", "readme.md", "README.txt", "package.json"):
        file = root / name
        if file.is_symlink() or not file.is_file() or file.stat().st_size > 256_000:
            continue
        # Respect ignored metadata in a Git repository; do not read private files.
        try:
            ignored = subprocess.run(["git", "check-ignore", "-q", "--", name], cwd=root,
                                     capture_output=True, timeout=3).returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            ignored = False
        if ignored:
            continue
        raw = file.read_text(encoding="utf-8", errors="replace")
        if name == "package.json":
            try:
                data = json.loads(raw)
                raw = str(data.get("description") or "")
                if not result["sources"]:
                    result["title"] = _clean(data.get("name") or root.name, 70)
            except (ValueError, AttributeError):
                continue
        else:
            heading = re.search(r"^#\s+(.+)$", raw, re.M)
            if heading:
                result["title"] = _clean(heading[1], 70)
            # Exclude fenced examples/config, links, images and markup, not code.
            raw = re.sub(r"```.*?```", "", raw, flags=re.S)
            raw = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", raw)
            raw = re.sub(r"<[^>]+>", "", raw)
        result["excerpt"] += _clean(raw, 5000) + "\n"
        result["sources"].append(name)
        if name != "package.json":
            break
    return result


def validate_request(params: dict) -> dict:
    source = inspect_project(str(params.get("project_path") or BASE))
    fmt = str(params.get("format") or "landscape").lower()
    if fmt not in FORMATS:
        raise ValueError("format must be landscape, vertical or square.")
    tone = str(params.get("tone") or "polished").lower()
    if tone not in TONES:
        raise ValueError("Choose a supported tone: " + ", ".join(sorted(TONES)))
    duration = float(params.get("duration", 20))
    if not math.isfinite(duration) or not 5 <= duration <= 30:
        raise ValueError("duration must be between 5 and 30 seconds.")
    quality = str(params.get("quality") or "final")
    if quality not in ("draft", "final"):
        raise ValueError("quality must be draft or final.")
    title = _clean(params.get("title") or source["title"], 70)
    hook = _clean(params.get("hook"), 150)
    highlights = params.get("highlights") or []
    if not isinstance(highlights, list) or any(not isinstance(v, str) for v in highlights):
        raise ValueError("highlights must be an array of short factual product statements.")
    highlights = [_clean(v, 150) for v in highlights if v.strip()][:3]
    if not hook:
        hook = title
    if not highlights:
        # Honest offline fallback: source COPY, not invented product claims.
        sentences = re.split(r"(?<=[.!?])\s+", source["excerpt"])
        highlights = [_clean(v.strip("#*| -"), 150) for v in sentences if len(v.strip()) > 20][:3]
    if not highlights:
        raise ValueError("No public product copy found. Provide hook and highlights, or add a public README.")
    images = []
    image_paths = params.get("image_paths") or []
    if not isinstance(image_paths, list) or any(not isinstance(v, str) for v in image_paths):
        raise ValueError("image_paths must be an array of local image paths.")
    for raw in image_paths:
        image = (Path(source["project"]) / str(raw)).resolve()
        if not image.is_relative_to(Path(source["project"])) or not image.is_file():
            raise ValueError("image_paths must refer to images inside the selected project.")
        if image.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp") or image.stat().st_size > 20_000_000:
            raise ValueError("Use PNG/JPEG/WebP product images smaller than 20 MB.")
        images.append(str(image))
        if len(images) == 3:
            break
    for flag in ("music", "sfx", "voice", "autoplay"):
        if flag in params and not isinstance(params[flag], bool):
            raise ValueError(flag + " must be a boolean.")
    return {"source": source, "title": title, "hook": hook, "highlights": highlights,
            "outro": _clean(params.get("outro") or title, 120), "format": fmt, "tone": tone,
            "duration": duration, "quality": quality, "image_paths": images,
            "music": params.get("music", True), "sfx": params.get("sfx", True),
            "voice": params.get("voice", False), "autoplay": params.get("autoplay", False)}


def ffmpeg_path():
    import imageio_ffmpeg
    path = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([path, "-version"], check=True, capture_output=True, timeout=10)
    return path


def doctor() -> dict:
    result = {"renderer": "JARVIS local Brag-slim adapter (not Hyperframes)", "ready": False}
    try:
        import PIL
        import numpy
        result.update(ffmpeg=ffmpeg_path(), pillow=PIL.__version__, numpy=numpy.__version__, ready=True)
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: install the existing requirements (Pillow, numpy, imageio-ffmpeg)."
    return result


def _job_file(job_id):
    if not re.fullmatch(r"[a-f0-9]{16}", str(job_id)):
        raise ValueError("Use a job_id returned by brag_video.")
    return OUTPUT_ROOT / job_id / "job.json"


def status(job_id):
    path = _job_file(job_id)
    if not path.is_file():
        raise ValueError("No such video job.")
    with _LOCK:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data["status"] in ("queued", "running") and job_id not in _JOBS:
            data.update(status="interrupted", stage="JARVIS restarted before this render finished")
            _atomic(path, data)
    return data


def cancel(job_id):
    data = status(job_id)
    with _LOCK:
        event = _JOBS.get(job_id)
        if event:
            event.set()
    return {"job_id": job_id, "status": "cancellation_requested" if event else data["status"]}


def _update(folder, **changes):
    with _LOCK:
        path = folder / "job.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data.update(changes, updated_at=time.time())
        _atomic(path, data)
    return data


class Cancelled(Exception):
    pass


def _check(event):
    if event.is_set():
        raise Cancelled("Render cancelled. No completed video was claimed.")


def _font(size):
    from PIL import ImageFont
    candidates = ["DejaVuSans.ttf", "Arial.ttf", "arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
                  str(Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "arial.ttf")]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    raise RuntimeError("No scalable font found. Install DejaVu Sans or Arial for readable video text.")


def _lines(draw, text, font, width):
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=font) > width and line:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + ([line] if line else [])


def make_frame(spec, t, size, photos):
    from PIL import Image, ImageDraw, ImageOps
    width, height = size
    background, foreground, accent = ("#0b1020", "#f8fafc", "#67e8f9")
    if spec["tone"] in ("deadpan", "yc-parody", "app-store"):
        background, foreground, accent = "#f6f3ec", "#172033", "#2455c3"
    frame = Image.new("RGB", size, background)
    draw = ImageDraw.Draw(frame)
    margin = int(min(size) * .085)
    scenes = [spec["hook"], *spec["highlights"], spec["outro"]]
    segment = spec["duration"] / len(scenes)
    index = min(int(t / segment), len(scenes) - 1)
    phase = (t - index * segment) / segment
    # Stagger through background, never crossfade two unreadable text layouts.
    reveal = min(1., max(0., phase / .16))
    leave = min(1., max(0., (1 - phase) / .10))
    ease = 1 - (1 - reveal) ** 3
    x = margin + int((1 - ease) * width * .07)
    draw.rounded_rectangle((margin, margin, width-margin, margin+max(3, height//160)), radius=3, fill=accent)
    small = _font(max(14, int(min(size) * .023)))
    draw.text((margin, margin*1.4), spec["title"], font=small, fill=foreground)
    text = scenes[index]
    max_width = width - 2 * margin
    box_height = height * (.29 if photos else .49)
    font_size = int(min(size) * (.068 if spec["tone"] != "cinematic" else .079))
    while True:
        font = _font(font_size)
        lines = _lines(draw, text, font, max_width)
        if (len(lines) * font_size * 1.28 <= box_height and
            all(draw.textlength(line, font=font) <= max_width for line in lines)):
            break
        font_size -= 1
        if font_size < 12:
            raise ValueError("Text cannot fit this format. Shorten the scene copy.")
    top = int(height * (.27 if not photos else .22))
    for i, line in enumerate(lines):
        draw.text((x, top+i*int(font_size*1.28)), line, font=font, fill=foreground)
    if photos:
        target = (width-2*margin, int(height*.32))
        picture = ImageOps.contain(photos[index % len(photos)], target)
        frame.paste(picture, (margin+(target[0]-picture.width)//2, int(height*.53)))
    label = "SOURCE COPY" if not photos else "PRODUCT VISUAL"
    draw.text((margin, height-margin*1.8), label, font=small, fill=accent)
    draw.text((margin, height-margin), f"{index+1:02d} / {len(scenes):02d}", font=small, fill=foreground)
    # Mix only with the empty background for a legible in/out reveal.
    return Image.blend(Image.new("RGB", size, background), frame, min(reveal, leave))


def _soundtrack(path, spec):
    import numpy as np
    rate = 24000
    t = np.arange(round(rate * spec["duration"]), dtype=np.float64) / rate
    sound = np.zeros(len(t))
    beat = 60 / (96 if spec["tone"] != "chaotic" else 132)
    if spec["music"]:
        # Original quiet minor-key bed; no copied/licensed upstream assets.
        for i, freq in enumerate((130.8128, 155.5635, 195.9977)):
            sound += .045 * np.sin(2*np.pi*freq*t + i*.4) * (.6+.4*np.cos(2*np.pi*t/(beat*8)))
        pulse = np.mod(t, beat)
        sound += .10 * np.sin(2*np.pi*55*t) * np.exp(-pulse*24)
    if spec["sfx"]:
        segment = spec["duration"] / (len(spec["highlights"])+2)
        for moment in np.arange(0, spec["duration"], segment):
            dt = np.maximum(0, t-moment)
            sound += .03*np.sin(2*np.pi*392*dt)*np.exp(-dt*25)*(t >= moment)
    sound *= np.minimum(1, t/.15) * np.minimum(1, (spec["duration"]-t)/.45)
    with wave.open(str(path), "wb") as out:
        out.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        out.writeframes((np.clip(sound, -.95, .95)*32767).astype("<i2").tobytes())


def _wait_process(proc, event, timeout):
    deadline = time.monotonic() + timeout
    try:
        while proc.poll() is None:
            _check(event)
            if time.monotonic() >= deadline:
                raise TimeoutError("Media subprocess exceeded its render timeout.")
            event.wait(.1)
        _check(event)
        if proc.returncode != 0:
            raise RuntimeError("FFmpeg failed. Inspect the job's work/encode.log or work/media.log.")
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=10)


def _media_command(args, event, log):
    with log.open("ab") as stream:
        proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=stream)
        _wait_process(proc, event, 120)


def render(spec, folder, event, progress):
    from PIL import Image
    ffmpeg = ffmpeg_path()
    work = folder / "work"
    work.mkdir()
    size = FORMATS[spec["format"]]
    if spec["quality"] == "draft":
        size = tuple(v//2 for v in size)
    fps = 30
    frames = round(spec["duration"]*fps)
    photos = []
    for path in spec["image_paths"]:
        with Image.open(path) as image:
            if image.width*image.height > 30_000_000:
                raise ValueError("Product image exceeds 30 megapixels.")
            photos.append(image.convert("RGB"))
    poster_time = spec["duration"] / (len(spec["highlights"])+2) * .5
    poster = make_frame(spec, poster_time, size, photos)
    poster.save(folder / "brag.jpg", quality=94)
    # Still checks from each settled scene and transition are kept for review.
    for i in range(len(spec["highlights"])+2):
        make_frame(spec, (i+.5)*spec["duration"]/(len(spec["highlights"])+2), size, photos).save(work/f"scene-{i+1}.jpg")
    narration = None
    if spec["voice"]:
        progress("narration", 4)
        from core.openai_compat import openai_tts_pcm24k
        script = ". ".join([spec["hook"], *spec["highlights"], spec["outro"]])
        pcm = openai_tts_pcm24k(script)
        if not pcm:
            raise RuntimeError("Narration requested but the configured OpenAI-compatible speech provider returned no audio. Configure speech or retry with voice=false.")
        if len(pcm) / 48000 > spec["duration"]:
            raise ValueError("Narration exceeds the requested duration. Shorten the copy or increase duration; speech was not silently cut.")
        narration = work / "narration.wav"
        with wave.open(str(narration), "wb") as out:
            out.setparams((1, 2, 24000, 0, "NONE", "not compressed"))
            out.writeframes(pcm)
    _check(event)
    silent = work / "picture.mp4"
    with (work / "encode.log").open("wb") as log:
        proc = subprocess.Popen([ffmpeg, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{size[0]}x{size[1]}",
            "-r", str(fps), "-i", "pipe:0", "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", str(silent)],
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=log)
        try:
            for n in range(frames):
                _check(event)
                frame = poster if n == 0 else make_frame(spec, n/fps, size, photos)
                proc.stdin.write(frame.tobytes())
                if n % 30 == 0:
                    progress("rendering", 5+int(80*n/frames))
            proc.stdin.close()
            _wait_process(proc, event, 120)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=10)
            if proc.stdin and not proc.stdin.closed:
                proc.stdin.close()
    _check(event)
    progress("mixing_audio", 88)
    args = [ffmpeg, "-y", "-v", "error", "-i", str(silent)]
    has_bed = spec["music"] or spec["sfx"]
    if has_bed:
        _soundtrack(work / "score.wav", spec)
        args += ["-i", str(work / "score.wav")]
    if narration:
        args += ["-i", str(narration)]
    if has_bed and narration:
        args += ["-filter_complex", "[1:a]volume=0.35[bed];[bed][2:a]amix=inputs=2:duration=longest[a]", "-map", "0:v", "-map", "[a]"]
    elif has_bed or narration:
        args += ["-map", "0:v", "-map", "1:a", "-af", "apad"]
    args += ["-c:v", "copy", "-c:a", "aac", "-t", str(spec["duration"]), "-movflags", "+faststart", str(folder/"brag.mp4")]
    _media_command(args, event, work/"media.log")
    _check(event)
    progress("verifying", 96)
    # Decode the WHOLE file. Existence/header checks alone aren't success.
    _media_command([ffmpeg, "-v", "error", "-xerror", "-i", str(folder/"brag.mp4"), "-f", "null", "-"],
                   event, work/"media.log")
    if (folder/"brag.mp4").stat().st_size < 1024:
        raise RuntimeError("Rendered video is unexpectedly empty.")
    return {"video": str(folder/"brag.mp4"), "poster": str(folder/"brag.jpg"), "width": size[0], "height": size[1], "fps": fps}


def start(params: dict, notify=None):
    spec = validate_request(params)
    ready = doctor()
    if not ready["ready"]:
        raise RuntimeError(ready["error"])
    job_id = uuid.uuid4().hex[:16]
    folder = OUTPUT_ROOT / job_id
    folder.mkdir(parents=True)
    scenes = [spec["hook"], *spec["highlights"], spec["outro"]]
    _atomic(folder/"plan.json", spec)
    storyboard = "\n".join(f"{i+1}. {spec['duration']/len(scenes):.2f}s — {line}" for i, line in enumerate(scenes))
    (folder/"brag-plan.md").write_text(f"# {spec['title']}\n\nTone: {spec['tone']}\nRenderer: JARVIS Brag-slim local adapter.\n"
        f"Source files: {', '.join(spec['source']['sources'])}\nVisuals: {'user-selected product images' if spec['image_paths'] else 'source-copy motion cards, not a captured product demo'}.\n\n{storyboard}\n", encoding="utf-8")
    (folder/"composition-brief.md").write_text(f"# Composition\n{spec['format']}, {spec['duration']} seconds, {spec['quality']}, 30 fps.\n"
        "Local deterministic Pillow frames; H.264/AAC MP4. Original synthesized score; no upstream music samples. Narration only if requested.\n", encoding="utf-8")
    (folder/"share-copy.txt").write_text(f"{spec['title']} — {spec['hook']}\n{spec['highlights'][0]}\n", encoding="utf-8")
    event = threading.Event()
    with _LOCK:
        _atomic(folder/"job.json", {"job_id": job_id, "status": "queued", "stage": "queued", "progress": 0, "created_at": time.time(), "directory": str(folder)})
        _JOBS[job_id] = event
    def worker():
        last_notice = [-10, ""]
        def progress(stage, percent):
            _check(event)
            data = _update(folder, status="running", stage=stage, progress=percent)
            if notify and (percent-last_notice[0] >= 10 or stage != last_notice[1]):
                last_notice[:] = [percent, stage]
                try:
                    notify(data, False)
                except Exception:
                    pass
        try:
            progress("preparing", 1)
            result = render(spec, folder, event, progress)
            _check(event)
            data = _update(folder, status="completed", stage="verified", progress=100, **result)
        except Cancelled as exc:
            (folder/"brag.mp4").unlink(missing_ok=True)
            data = _update(folder, status="cancelled", stage="cancelled", error=str(exc))
        except Exception as exc:
            (folder/"brag.mp4").unlink(missing_ok=True)
            data = _update(folder, status="failed", stage="failed", error=f"{type(exc).__name__}: {str(exc)[:350]}")
        finally:
            with _LOCK:
                _JOBS.pop(job_id, None)
        if notify:
            try:
                notify(data, spec["autoplay"])
            except Exception:
                pass  # Display failure cannot overwrite verified media status.
    threading.Thread(target=worker, name="brag-render-"+job_id, daemon=True).start()
    return {"job_id": job_id, "status": "queued", "directory": str(folder), "message": "Render started, not completed. Use status with this job_id."}
