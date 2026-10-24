"""
core/media_engine.py — Universal Multi-Platform Video & Audio Engine.

Supports downloading, stream resolution (for in-HUD & desktop playback),
metadata inspection, and caption/audio transcription + AI summarization across
Instagram (Reels, Posts, Stories, IGTV), YouTube (Videos, Shorts, Music),
Snapchat (Spotlight, Public Stories), TikTok, X / Twitter, Reddit, Facebook,
Twitch, Vimeo, Dailymotion, SoundCloud, Pinterest, LinkedIn, Bilibili, and
1,800+ additional extractors supported by `yt-dlp`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import mimetypes
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any, Callable
from urllib.parse import urlparse

import httpx

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

_URL_RE = re.compile(r"https?://[^\s<>\"')\]}]+", re.IGNORECASE)

_DIRECT_MEDIA_EXTS = {
    ".mp4",
    ".webm",
    ".mkv",
    ".mov",
    ".m4v",
    ".avi",
    ".m3u8",
    ".mpd",
    ".mp3",
    ".m4a",
    ".wav",
    ".ogg",
    ".flac",
    ".aac",
}

_PLATFORM_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Instagram", re.compile(r"(?:^|\.)instagram\.com|instagr\.am", re.I)),
    ("YouTube", re.compile(r"(?:^|\.)youtube\.com|youtu\.be|youtube-nocookie\.com", re.I)),
    ("Snapchat", re.compile(r"(?:^|\.)snapchat\.com|t\.snapchat\.com", re.I)),
    ("TikTok", re.compile(r"(?:^|\.)tiktok\.com|vm\.tiktok\.com|vt\.tiktok\.com", re.I)),
    ("X", re.compile(r"(?:^|\.)(?:x\.com|twitter\.com|t\.co)$", re.I)),
    ("Reddit", re.compile(r"(?:^|\.)(?:reddit\.com|redd\.it|v\.redd\.it)$", re.I)),
    ("Facebook", re.compile(r"(?:^|\.)(?:facebook\.com|fb\.watch|fb\.com)$", re.I)),
    ("Twitch", re.compile(r"(?:^|\.)twitch\.tv|clips\.twitch\.tv", re.I)),
    ("Vimeo", re.compile(r"(?:^|\.)vimeo\.com|player\.vimeo\.com", re.I)),
    ("Dailymotion", re.compile(r"(?:^|\.)dailymotion\.com|dai\.ly", re.I)),
    ("SoundCloud", re.compile(r"(?:^|\.)soundcloud\.com|on\.soundcloud\.com", re.I)),
    ("Pinterest", re.compile(r"(?:^|\.)pinterest\.[a-z.]+|pin\.it", re.I)),
    ("LinkedIn", re.compile(r"(?:^|\.)linkedin\.com|lnkd\.in", re.I)),
    ("Bilibili", re.compile(r"(?:^|\.)bilibili\.com|b23\.tv", re.I)),
    ("Rumble", re.compile(r"(?:^|\.)rumble\.com", re.I)),
    ("Loom", re.compile(r"(?:^|\.)loom\.com", re.I)),
    ("Streamable", re.compile(r"(?:^|\.)streamable\.com", re.I)),
)

_AUTH_ERROR_HINTS = (
    "login required",
    "sign in",
    "authentication",
    "cookies",
    "rate-limit",
    "not available for registered users",
    "private",
    "http error 401",
    "http error 403",
)


@dataclass
class ResolvedStream:
    ok: bool
    video_url: str = ""
    audio_url: str = ""
    title: str = ""
    uploader: str = ""
    platform: str = "Web"
    duration: int = 0
    webpage_url: str = ""
    thumbnail: str = ""
    http_headers: dict[str, str] = field(default_factory=dict)
    error: str = ""


@dataclass
class DownloadResult:
    ok: bool
    filepath: str = ""
    filename: str = ""
    filesize_bytes: int = 0
    title: str = ""
    uploader: str = ""
    platform: str = "Web"
    duration: int = 0
    webpage_url: str = ""
    audio_only: bool = False
    error: str = ""

    @property
    def filesize_mb(self) -> float:
        return round(self.filesize_bytes / (1024 * 1024), 2)


# ── Helpers: Platform, URL, Clipboard & FFmpeg Discovery ─────────────────────


def detect_platform(url_or_path: str) -> str:
    raw = (url_or_path or "").strip()
    if not raw:
        return "Web"
    if not raw.lower().startswith(("http://", "https://")):
        return "Local"
    try:
        host = (urlparse(raw).hostname or "").lower()
    except Exception:
        host = ""
    for label, pat in _PLATFORM_PATTERNS:
        if pat.search(host):
            return label
    if host.startswith("www."):
        host = host[4:]
    return host.split(".")[0].capitalize() if host else "Web"


def is_direct_media_url(url: str) -> bool:
    raw = (url or "").strip()
    if not raw.lower().startswith(("http://", "https://", "file://")):
        return False
    try:
        parsed = urlparse(raw)
        host = (parsed.hostname or "").lower()
        # Social/video platform pages are NEVER direct media files even if a query has .mp4
        for _label, pat in _PLATFORM_PATTERNS:
            if pat.search(host):
                return False
        ext = Path(parsed.path).suffix.lower()
        return ext in _DIRECT_MEDIA_EXTS
    except Exception:
        return False


def extract_url_from_text_or_clipboard(
    text: str = "",
    *,
    allow_clipboard: bool = True,
) -> str:
    """Return an http(s) URL from `text`, falling back to system clipboard if requested."""
    raw = (text or "").strip().strip('"').strip("'")
    m = _URL_RE.search(raw)
    if m:
        return m.group(0).rstrip(".,;!")

    if allow_clipboard:
        try:
            import pyperclip

            clip = (pyperclip.paste() or "").strip()
            mc = _URL_RE.search(clip)
            if mc:
                return mc.group(0).rstrip(".,;!")
        except Exception:
            pass
    return ""


def resolve_ffmpeg_path() -> str | None:
    """Locate system `ffmpeg` or bundled `imageio-ffmpeg` binary."""
    env_bin = os.environ.get("JARVIS_FFMPEG_PATH", "").strip()
    if env_bin and Path(env_bin).exists():
        return env_bin
    sys_ff = shutil.which("ffmpeg")
    if sys_ff:
        return sys_ff
    try:
        import imageio_ffmpeg

        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and Path(exe).exists():
            return str(exe)
    except Exception:
        pass
    return None


def sanitize_filename(name: str, max_len: int = 88) -> str:
    clean = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', " ", (name or "").strip())
    clean = re.sub(r"\s+", " ", clean).strip(" ._-")
    if not clean:
        clean = "video"
    return clean[:max_len].strip(" ._-") or "video"


def resolve_output_directory(dest_hint: str = "") -> Path:
    hint = (dest_hint or "").strip()
    home = Path.home()
    if not hint or hint.lower() in ("downloads", "download", "default"):
        target = home / "Downloads"
    elif hint.lower() in ("desktop", "my desktop"):
        target = home / "Desktop"
    elif hint.lower() in ("videos", "movies", "my videos"):
        target = home / "Videos"
    else:
        p = Path(hint).expanduser()
        target = p if p.is_absolute() else (home / p)
    target.mkdir(parents=True, exist_ok=True)
    return target


def _candidate_cookie_browsers(preferred: str = "") -> list[str]:
    env_pref = os.environ.get("JARVIS_YTDLP_COOKIES_FROM_BROWSER", "").strip().lower()
    explicit = (preferred or env_pref).strip().lower()
    if explicit:
        return [explicit]
    # Order common installed browsers for fallback retry ONLY when anonymous fails
    if os.name == "nt":
        return ["edge", "chrome", "brave", "firefox"]
    return ["chrome", "brave", "firefox", "safari", "chromium"]


def _needs_cookie_retry(err_msg: str) -> bool:
    low = (err_msg or "").lower()
    return any(h in low for h in _AUTH_ERROR_HINTS)


def _extract_with_ytdlp(
    query_or_url: str,
    base_opts: dict[str, Any],
    *,
    download: bool = False,
    cookies_browser: str = "",
) -> dict[str, Any]:
    import yt_dlp

    opts = dict(base_opts)
    opts.setdefault("http_headers", dict(DEFAULT_HEADERS))
    if cookies_browser:
        opts["cookiesfrombrowser"] = (cookies_browser,)

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(query_or_url, download=download)
    except Exception as first_exc:
        if cookies_browser or not _needs_cookie_retry(str(first_exc)):
            raise
        last_exc: Exception = first_exc
        info = None
        for browser in _candidate_cookie_browsers():
            retry_opts = dict(opts)
            retry_opts["cookiesfrombrowser"] = (browser,)
            try:
                with yt_dlp.YoutubeDL(retry_opts) as ydl:
                    info = ydl.extract_info(query_or_url, download=download)
                if info:
                    break
            except Exception as retry_exc:
                last_exc = retry_exc
                continue
        if info is None:
            raise last_exc from first_exc

    if info and info.get("entries"):
        entries = [e for e in info["entries"] if e]
        if entries:
            info = entries[0]
    return info or {}


# ── 1. Universal Playable Stream Resolution (HUD & Desktop Player) ───────────


def resolve_playable_stream(
    url_or_query: str,
    *,
    cookies_browser: str = "",
    max_height: int = 1080,
) -> ResolvedStream:
    """Resolve any URL (Instagram, YouTube, Snapchat, TikTok, X, Reddit, etc.) or search query into playable HTTP stream URLs."""
    raw = (url_or_query or "").strip()
    if not raw:
        return ResolvedStream(ok=False, error="No video URL or search query provided.")

    try:
        import yt_dlp  # noqa: F401
    except Exception:
        return ResolvedStream(
            ok=False,
            error="yt-dlp is not installed. Run: pip install -U yt-dlp",
        )

    is_url = raw.lower().startswith(("http://", "https://"))
    target = raw if is_url else f"ytsearch1:{raw}"

    opts: dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
    }

    try:
        info = _extract_with_ytdlp(
            target,
            opts,
            download=False,
            cookies_browser=cookies_browser,
        )
    except Exception as exc:
        return ResolvedStream(
            ok=False,
            platform=detect_platform(raw),
            webpage_url=raw if is_url else "",
            error=str(exc),
        )

    if not info:
        return ResolvedStream(ok=False, error="No playable video found.")

    webpage_url = str(info.get("webpage_url") or (raw if is_url else ""))
    platform = detect_platform(webpage_url or raw)
    title = str(info.get("title") or info.get("description") or raw).strip()[:120]
    uploader = str(info.get("uploader") or info.get("channel") or "").strip()
    duration = int(info.get("duration") or 0)
    thumbnail = str(info.get("thumbnail") or "")

    formats = [
        f
        for f in (info.get("formats") or [])
        if f.get("url") and str(f.get("protocol") or "https").startswith("http")
    ]

    def _has_v(f: dict[str, Any]) -> bool:
        v = f.get("vcodec")
        if v is None:
            # Instagram / Snapchat / TikTok progressive formats sometimes omit vcodec metadata
            return f.get("ext") in ("mp4", "webm", "mov") and f.get("acodec") != "only"
        return v != "none"

    def _has_a(f: dict[str, Any]) -> bool:
        a = f.get("acodec")
        if a is None:
            return f.get("ext") in ("mp4", "webm", "mov", "m4a", "mp3")
        return a != "none"

    def _score_video(f: dict[str, Any]) -> tuple[int, int, int, float]:
        ext_mp4 = 1 if f.get("ext") == "mp4" else 0
        h264 = 1 if str(f.get("vcodec") or "").startswith(("avc", "h264")) else 0
        h = int(f.get("height") or 0)
        capped_h = h if h <= max_height else max(0, max_height - (h - max_height))
        tbr = float(f.get("tbr") or f.get("vbr") or 0.0)
        return (ext_mp4, h264, capped_h, tbr)

    def _score_audio(f: dict[str, Any]) -> tuple[int, int, float]:
        lang_pref = int(f.get("language_preference") or 0)
        ext_m4a = 1 if f.get("ext") in ("m4a", "mp4", "aac") else 0
        abr = float(f.get("abr") or f.get("tbr") or 0.0)
        return (lang_pref, ext_m4a, abr)

    # 1. Prefer combined progressive video+audio (best for Instagram, Snapchat, TikTok, X, Vimeo & progressive MP4)
    combined_candidates = [
        f
        for f in formats
        if _has_v(f)
        and _has_a(f)
        and not str(f.get("protocol") or "").endswith("m3u8_native")
    ]
    if combined_candidates:
        best_comb = max(combined_candidates, key=_score_video)
        hdrs = dict(DEFAULT_HEADERS)
        hdrs.update(info.get("http_headers") or {})
        hdrs.update(best_comb.get("http_headers") or {})
        return ResolvedStream(
            ok=True,
            video_url=str(best_comb["url"]),
            audio_url="",
            title=title,
            uploader=uploader,
            platform=platform,
            duration=duration,
            webpage_url=webpage_url,
            thumbnail=thumbnail,
            http_headers={str(k): str(v) for k, v in hdrs.items()},
        )

    # 2. Split DASH video + audio (standard on modern YouTube & Reddit v.redd.it)
    vid_only = [
        f
        for f in formats
        if _has_v(f)
        and not _has_a(f)
        and not str(f.get("protocol") or "").endswith("m3u8_native")
    ]
    aud_only = [
        f
        for f in formats
        if _has_a(f)
        and not _has_v(f)
        and not str(f.get("protocol") or "").endswith("m3u8_native")
    ]

    if vid_only:
        within_cap = [
            f for f in vid_only if (int(f.get("height") or 0) or 720) <= max_height
        ]
        best_v = max(within_cap or vid_only, key=_score_video)
        best_a = max(aud_only, key=_score_audio) if aud_only else None
        hdrs = dict(DEFAULT_HEADERS)
        hdrs.update(info.get("http_headers") or {})
        hdrs.update(best_v.get("http_headers") or {})
        return ResolvedStream(
            ok=True,
            video_url=str(best_v["url"]),
            audio_url=str(best_a["url"]) if best_a else "",
            title=title,
            uploader=uploader,
            platform=platform,
            duration=duration,
            webpage_url=webpage_url,
            thumbnail=thumbnail,
            http_headers={str(k): str(v) for k, v in hdrs.items()},
        )

    # 3. Direct top-level `url` fallback (used by several single-stream extractors)
    direct_u = str(info.get("url") or "")
    if direct_u.startswith("http"):
        hdrs = dict(DEFAULT_HEADERS)
        hdrs.update(info.get("http_headers") or {})
        return ResolvedStream(
            ok=True,
            video_url=direct_u,
            audio_url="",
            title=title,
            uploader=uploader,
            platform=platform,
            duration=duration,
            webpage_url=webpage_url,
            thumbnail=thumbnail,
            http_headers={str(k): str(v) for k, v in hdrs.items()},
        )

    return ResolvedStream(
        ok=False,
        platform=platform,
        webpage_url=webpage_url,
        error="No playable HTTP video stream was offered by this page.",
    )


# ── 2. Universal Video & Audio Downloader (Instagram / YouTube / Snapchat / +) ─


def _height_cap_from_quality(quality: str) -> int | None:
    q = (quality or "best").strip().lower()
    if q in ("4k", "2160", "2160p", "uhd"):
        return 2160
    if q in ("1440", "1440p", "2k"):
        return 1440
    if q in ("1080", "1080p", "fullhd", "fhd"):
        return 1080
    if q in ("720", "720p", "hd"):
        return 720
    if q in ("480", "480p", "sd"):
        return 480
    if q in ("360", "360p", "low"):
        return 360
    return None


def download_media(
    url_or_query: str,
    *,
    output_dir: str = "",
    audio_only: bool = False,
    quality: str = "best",
    filename_hint: str = "",
    cookies_browser: str = "",
    progress_cb: Callable[[str], None] | None = None,
) -> DownloadResult:
    """Download video (.mp4) or audio (.mp3/.m4a) from Instagram, YouTube, Snapchat, TikTok, X, Reddit, or any yt-dlp site."""
    raw = (url_or_query or "").strip()
    if not raw:
        return DownloadResult(ok=False, error="No video URL or search query provided.")

    try:
        import yt_dlp  # noqa: F401
    except Exception:
        return DownloadResult(
            ok=False,
            error="yt-dlp is not installed. Run: pip install -U yt-dlp",
        )

    dest_dir = resolve_output_directory(output_dir)
    ffmpeg_bin = resolve_ffmpeg_path()

    is_url = raw.lower().startswith(("http://", "https://"))
    target = raw if is_url else f"ytsearch1:{raw}"
    height_cap = _height_cap_from_quality(quality)

    if audio_only:
        if ffmpeg_bin:
            fmt = "bestaudio/best"
        else:
            fmt = "bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio/best"
    else:
        h_clause = f"[height<={height_cap}]" if height_cap else ""
        if ffmpeg_bin:
            # Prefer H.264/AAC MP4 merge for universal Windows/macOS/QuickTime/phone compatibility,
            # falling back cleanly to any video+audio or combined stream
            fmt = (
                f"bv*[vcodec^=avc1]{h_clause}+ba[ext=m4a]/"
                f"bv*[ext=mp4]{h_clause}+ba[ext=m4a]/"
                f"b[ext=mp4]{h_clause}/"
                f"bv*{h_clause}+ba/b{h_clause}/b"
            )
        else:
            # No ffmpeg binary: choose best combined single-file stream so download never errors on merge
            fmt = f"b[ext=mp4]{h_clause}/b{h_clause}/b"

    # Stage inside a clean temp directory inside dest_dir so we always locate the exact final file
    stage_dir = Path(tempfile.mkdtemp(prefix=".jarvis_dl_", dir=str(dest_dir)))
    try:
        outtmpl = str(stage_dir / "%(title).90B [%(extractor)s].%(ext)s")
        opts: dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "format": fmt,
            "outtmpl": outtmpl,
            "restrictfilenames": False,
            "windowsfilenames": True,
        }
        if ffmpeg_bin:
            opts["ffmpeg_location"] = ffmpeg_bin
            if audio_only:
                opts["postprocessors"] = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ]
            else:
                opts["merge_output_format"] = "mp4"

        if callable(progress_cb):
            last_pct = {"bucket": -1}

            def _hook(d: dict[str, Any]) -> None:
                if d.get("status") == "downloading":
                    total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                    done = d.get("downloaded_bytes") or 0
                    if total > 0:
                        pct = int(done * 100 / total)
                        bucket = pct // 25
                        if bucket > last_pct["bucket"]:
                            last_pct["bucket"] = bucket
                            progress_cb(f"Downloading… {pct}%")

            opts["progress_hooks"] = [_hook]

        info = _extract_with_ytdlp(
            target,
            opts,
            download=True,
            cookies_browser=cookies_browser,
        )

        produced = sorted(
            [
                p
                for p in stage_dir.iterdir()
                if p.is_file() and not p.name.endswith((".part", ".ytdl"))
            ],
            key=lambda p: p.stat().st_size,
            reverse=True,
        )
        if not produced:
            return DownloadResult(
                ok=False,
                platform=detect_platform(raw),
                error="Download finished without producing a media file.",
            )

        staged_file = produced[0]
        if staged_file.stat().st_size == 0:
            return DownloadResult(
                ok=False,
                platform=detect_platform(raw),
                error="Downloaded file was empty (0 bytes).",
            )

        webpage_url = str(info.get("webpage_url") or (raw if is_url else ""))
        platform = detect_platform(webpage_url or raw)
        raw_title = (
            filename_hint
            or str(info.get("title") or "").strip()
            or str(info.get("id") or "video")
        )
        safe_stem = sanitize_filename(f"{raw_title} [{platform}]", max_len=96)
        ext = staged_file.suffix.lower() or (".mp3" if audio_only else ".mp4")

        final_path = dest_dir / f"{safe_stem}{ext}"
        counter = 1
        while final_path.exists():
            final_path = dest_dir / f"{safe_stem} ({counter}){ext}"
            counter += 1

        shutil.move(str(staged_file), str(final_path))
        size_bytes = final_path.stat().st_size

        return DownloadResult(
            ok=True,
            filepath=str(final_path),
            filename=final_path.name,
            filesize_bytes=size_bytes,
            title=str(info.get("title") or raw_title).strip()[:160],
            uploader=str(info.get("uploader") or info.get("channel") or "").strip(),
            platform=platform,
            duration=int(info.get("duration") or 0),
            webpage_url=webpage_url,
            audio_only=audio_only,
        )
    except Exception as exc:
        return DownloadResult(
            ok=False,
            platform=detect_platform(raw),
            webpage_url=raw if is_url else "",
            audio_only=audio_only,
            error=str(exc),
        )
    finally:
        shutil.rmtree(stage_dir, ignore_errors=True)


# ── 3. Metadata, Captions & Multimodal Audio Summarization ───────────────────


def get_media_info(url: str, *, cookies_browser: str = "") -> dict[str, Any]:
    """Fetch structured metadata for any Instagram, Snapchat, YouTube, TikTok, X, or web video URL."""
    raw = (url or "").strip()
    if not raw:
        return {"ok": False, "error": "No URL provided."}
    try:
        info = _extract_with_ytdlp(
            raw,
            {"quiet": True, "no_warnings": True, "skip_download": True, "noplaylist": True},
            download=False,
            cookies_browser=cookies_browser,
        )
    except Exception as exc:
        return {"ok": False, "platform": detect_platform(raw), "error": str(exc)}

    webpage_url = str(info.get("webpage_url") or raw)
    return {
        "ok": True,
        "platform": detect_platform(webpage_url),
        "title": str(info.get("title") or "").strip(),
        "description": str(info.get("description") or "").strip()[:1200],
        "uploader": str(info.get("uploader") or info.get("channel") or "").strip(),
        "duration": int(info.get("duration") or 0),
        "view_count": info.get("view_count"),
        "like_count": info.get("like_count"),
        "upload_date": info.get("upload_date") or "",
        "webpage_url": webpage_url,
    }


def _clean_subtitle_payload(raw_text: str) -> str:
    text = (raw_text or "").strip()
    if not text:
        return ""
    # JSON3 format from YouTube / yt-dlp
    if text.startswith("{") and '"events"' in text:
        try:
            data = json.loads(text)
            segs: list[str] = []
            for ev in data.get("events") or []:
                for s in ev.get("segs") or []:
                    tok = str(s.get("utf8") or "").strip()
                    if tok:
                        segs.append(tok)
            if segs:
                return re.sub(r"\s+", " ", " ".join(segs)).strip()
        except Exception:
            pass
    # WebVTT / SRT cleanup
    lines: list[str] = []
    for ln in text.splitlines():
        s = ln.strip()
        if (
            not s
            or s.startswith("WEBVTT")
            or "-->" in s
            or re.fullmatch(r"\d+", s)
        ):
            continue
        s = re.sub(r"<[^>]+>", "", s).strip()
        if s and (not lines or lines[-1] != s):
            lines.append(s)
    return re.sub(r"\s+", " ", " ".join(lines)).strip()


def _fetch_subtitles_from_info(info: dict[str, Any]) -> str:
    lang_order = ["en", "en-US", "en-GB", "ar", "tr", "es", "fr", "de", "pt", "ru", "hi", "ja", "ko", "zh"]
    for bucket_key in ("subtitles", "automatic_captions"):
        bucket = info.get(bucket_key)
        if not isinstance(bucket, dict) or not bucket:
            continue
        candidate_langs = [l for l in lang_order if l in bucket] + [
            k for k in bucket.keys() if k not in lang_order
        ]
        for lang in candidate_langs[:4]:
            tracks = bucket.get(lang) or []
            if not isinstance(tracks, list):
                continue
            # Prefer vtt/srv3/srt/json3 text tracks
            ordered = sorted(
                tracks,
                key=lambda t: (
                    0
                    if t.get("ext") in ("vtt", "srt", "json3")
                    else 1
                ),
            )
            for tr in ordered[:2]:
                sub_url = tr.get("url")
                if not sub_url:
                    continue
                try:
                    with httpx.Client(
                        timeout=12.0, follow_redirects=True, headers=DEFAULT_HEADERS
                    ) as client:
                        r = client.get(sub_url)
                    if r.status_code == 200 and r.text:
                        cleaned = _clean_subtitle_payload(r.text)
                        if len(cleaned) >= 20:
                            return cleaned
                except Exception:
                    continue
    return ""


def _transcribe_short_video_audio(url: str, *, cookies_browser: str = "") -> str:
    """Download lightweight audio stream (<24 MB) and transcribe via OpenAI Whisper or Gemini multimodal."""
    from memory import config_manager as cfg

    tmp_dir = Path(tempfile.mkdtemp(prefix=".jarvis_vid_stt_"))
    try:
        opts: dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "format": "worstaudio[ext=m4a]/bestaudio[filesize<24M]/worstaudio/best[filesize<24M]",
            "outtmpl": str(tmp_dir / "track.%(ext)s"),
        }
        ffmpeg_bin = resolve_ffmpeg_path()
        if ffmpeg_bin:
            opts["ffmpeg_location"] = ffmpeg_bin

        _extract_with_ytdlp(url, opts, download=True, cookies_browser=cookies_browser)
        files = [p for p in tmp_dir.iterdir() if p.is_file() and p.stat().st_size > 0]
        if not files:
            return ""
        audio_file = files[0]
        if audio_file.stat().st_size > 24 * 1024 * 1024:
            return ""

        # 1. Try OpenAI Audio Transcriptions if an OpenAI key is configured
        ocfg = cfg.get_openai_cfg()
        oai_key = (ocfg.get("api_key") or "").strip()
        if oai_key and len(oai_key) > 15:
            base_url = (ocfg.get("base_url") or "https://api.openai.com/v1").rstrip("/")
            mime = mimetypes.guess_type(audio_file.name)[0] or "audio/mp4"
            raw_bytes = audio_file.read_bytes()
            for model_name in ("gpt-4o-mini-transcribe", "whisper-1"):
                try:
                    with httpx.Client(timeout=45.0) as client:
                        resp = client.post(
                            f"{base_url}/audio/transcriptions",
                            headers={"Authorization": f"Bearer {oai_key}"},
                            data={"model": model_name},
                            files={"file": (audio_file.name, raw_bytes, mime)},
                        )
                    if resp.status_code == 200:
                        txt = str(resp.json().get("text") or "").strip()
                        if txt:
                            return txt
                except Exception:
                    continue

        # 2. Try Gemini multimodal audio understanding if a Gemini key is configured
        gkey = (cfg.get_gemini_key() or "").strip()
        if gkey and len(gkey) > 15:
            try:
                from google.genai import types
                from core import gemini

                mime = mimetypes.guess_type(audio_file.name)[0] or "audio/mp4"
                part = types.Part.from_bytes(
                    data=audio_file.read_bytes(), mime_type=mime
                )
                resp = gemini.call(
                    [
                        part,
                        "Transcribe everything spoken in this video audio accurately, "
                        "and note any key sound/music cues if there is no speech.",
                    ],
                    tier=gemini.FAST,
                    timeout_ms=45_000,
                )
                if resp and getattr(resp, "text", None):
                    return resp.text.strip()
            except Exception:
                pass
        return ""
    except Exception:
        return ""
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def summarize_media(
    url: str,
    *,
    focus: str = "",
    cookies_browser: str = "",
) -> dict[str, Any]:
    """Universal video summarizer for Instagram, Snapchat, YouTube, TikTok, X, Reddit & any web video."""
    raw = (url or "").strip()
    if not raw:
        return {"ok": False, "error": "No video URL provided."}

    try:
        info = _extract_with_ytdlp(
            raw,
            {"quiet": True, "no_warnings": True, "skip_download": True, "noplaylist": True},
            download=False,
            cookies_browser=cookies_browser,
        )
    except Exception as exc:
        return {"ok": False, "platform": detect_platform(raw), "error": str(exc)}

    webpage_url = str(info.get("webpage_url") or raw)
    platform = detect_platform(webpage_url)
    title = str(info.get("title") or "").strip()
    uploader = str(info.get("uploader") or info.get("channel") or "").strip()
    description = str(info.get("description") or "").strip()[:3000]
    duration = int(info.get("duration") or 0)

    transcript = _fetch_subtitles_from_info(info)
    if not transcript and duration <= 1200:
        transcript = _transcribe_short_video_audio(
            webpage_url, cookies_browser=cookies_browser
        )

    if not transcript and not description and not title:
        return {
            "ok": False,
            "platform": platform,
            "error": "Could not extract captions, audio speech, or description from that video.",
        }

    from core import gemini

    focus_line = f"\nUser focus / question: {focus}\n" if focus else ""
    prompt = (
        f"Summarize this {platform} video clearly and concisely.\n"
        f"Title: {title or 'Untitled'}\n"
        f"Creator: {uploader or 'Unknown'}\n"
        f"Duration: {duration}s\n"
        f"{focus_line}"
        f"Caption / Description:\n{description[:1500] or '(none)'}\n\n"
        f"Spoken Transcript:\n{(transcript or '(no spoken transcript detected)')[:65000]}\n\n"
        "Provide a 1-sentence overview followed by 3–5 concise bullet takeaways."
    )
    resp = gemini.call(prompt, tier=gemini.SMART, timeout_ms=55_000)
    summary_text = (getattr(resp, "text", "") or "").strip() if resp else ""
    if not summary_text:
        # Clean deterministic fallback if offline / no cloud model reachable
        summary_text = (
            f"{title or platform + ' video'}"
            + (f" by {uploader}" if uploader else "")
            + (f": {transcript[:600]}" if transcript else f": {description[:600]}")
        )

    return {
        "ok": True,
        "platform": platform,
        "title": title,
        "uploader": uploader,
        "duration": duration,
        "webpage_url": webpage_url,
        "has_transcript": bool(transcript),
        "summary": summary_text,
    }
