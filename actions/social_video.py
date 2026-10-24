"""
actions/social_video.py — Universal Video & Audio Action for Instagram, YouTube,
Snapchat, TikTok, X/Twitter, Reddit, Facebook, Twitch, Vimeo, SoundCloud & 1,800+ sites.

Capabilities:
  • download  — Save .mp4 video (4K/1080p/720p/best) or .mp3 audio to Downloads,
                Desktop, Videos, or any custom folder (auto-reads clipboard URL
                if the user says "download this video" without pasting the link).
  • play      — Stream and play any Instagram, Snapchat, YouTube, TikTok, X,
                Reddit, or web video directly inside JARVIS's HUD display.
  • summarize — Extract captions or transcribe the video's spoken audio via
                OpenAI Whisper / Gemini multimodal and summarize it concisely.
  • info      — Inspect video metadata (title, creator, platform, duration,
                views, likes, description).
"""

from __future__ import annotations

import os
from pathlib import Path
import webbrowser

from config import is_linux, is_mac, is_windows
from core.media_engine import (
    detect_platform,
    download_media,
    extract_url_from_text_or_clipboard,
    get_media_info,
    is_direct_media_url,
    resolve_playable_stream,
    summarize_media,
)


def _open_local_file_or_folder(filepath: str, *, reveal_folder: bool = False) -> None:
    p = Path(filepath)
    target = p.parent if reveal_folder else p
    if not target.exists():
        return
    try:
        from core.os_control import unpatched_popen

        if is_windows():
            if reveal_folder:
                unpatched_popen(["explorer.exe", f"/select,{p}"])
            else:
                os.startfile(str(p))  # type: ignore[attr-defined]
        elif is_mac():
            if reveal_folder:
                unpatched_popen(["open", "-R", str(p)])
            else:
                unpatched_popen(["open", str(p)])
        else:
            unpatched_popen(["xdg-open", str(target)])
    except Exception as exc:
        print(f"[SocialVideo] Could not open {target}: {exc}")


def _format_duration(seconds: int) -> str:
    if not seconds or seconds <= 0:
        return "Unknown"
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def social_video(
    parameters: dict | None = None,
    response=None,
    player=None,
    session_memory=None,
    speak=None,
) -> str:
    params = parameters or {}
    action = str(params.get("action") or "download").strip().lower()
    raw_url = str(params.get("url") or params.get("query") or "").strip()
    cookies_browser = str(params.get("cookies_browser") or "").strip()

    # Resolve URL from explicit argument or system clipboard
    resolved_url = extract_url_from_text_or_clipboard(
        raw_url,
        allow_clipboard=(not raw_url or "clipboard" in raw_url.lower()),
    )
    target = resolved_url or raw_url

    if not target:
        return (
            "Please share the video link (from Instagram, YouTube, Snapchat, TikTok, "
            "X, Reddit, or any other site) or copy it to your clipboard first."
        )

    platform = detect_platform(target)

    # ── 1. DOWNLOAD VIDEO OR AUDIO ────────────────────────────────────────────
    if action in ("download", "save", "dl", "audio", "mp3", "mp4"):
        audio_only = bool(params.get("audio_only", False)) or action in ("audio", "mp3")
        quality = str(params.get("quality") or "best").strip()
        destination = str(params.get("destination") or "Downloads").strip()
        open_after = bool(params.get("open_after", False))
        reveal_folder = bool(params.get("reveal_folder", False))
        play_in_hud = bool(params.get("play_in_hud", False))

        kind_lbl = "MP3 audio" if audio_only else "MP4 video"
        if player is not None and hasattr(player, "write_log"):
            player.write_log(f"[Video] Downloading {platform} {kind_lbl}…")

        def _on_prog(msg: str) -> None:
            if player is not None and hasattr(player, "write_log"):
                player.write_log(f"[Video] {platform}: {msg}")

        res = download_media(
            target,
            output_dir=destination,
            audio_only=audio_only,
            quality=quality,
            cookies_browser=cookies_browser,
            progress_cb=_on_prog,
        )

        if not res.ok:
            return (
                f"Could not download that {platform} media: {res.error}. "
                "If the post is private or requires login, pass cookies_browser='chrome' (or 'edge'/'firefox')."
            )

        summary_card = (
            f"Platform : {res.platform}\n"
            f"Title    : {res.title or res.filename}\n"
            + (f"Creator  : {res.uploader}\n" if res.uploader else "")
            + (f"Duration : {_format_duration(res.duration)}\n" if res.duration else "")
            + f"Format   : {'Audio (.mp3)' if res.audio_only else 'Video (.mp4)'}\n"
            f"Size     : {res.filesize_mb} MB\n"
            f"Saved to : {res.filepath}"
        )
        if player is not None and hasattr(player, "show_content"):
            try:
                player.show_content(f"{res.platform} Download Complete", summary_card)
            except Exception:
                pass

        if play_in_hud and not res.audio_only and player is not None and hasattr(player, "show_video"):
            try:
                player.show_video(res.filepath, res.title or res.filename, muted=True)
            except Exception:
                pass
        elif open_after or reveal_folder:
            _open_local_file_or_folder(res.filepath, reveal_folder=reveal_folder)

        return (
            f"Downloaded {res.platform} {'audio' if res.audio_only else 'video'} "
            f"'{res.title or res.filename}' ({res.filesize_mb} MB) to {res.filepath}."
        )

    # ── 2. PLAY VIDEO IN HUD OR BROWSER ───────────────────────────────────────
    if action in ("play", "watch", "open"):
        if bool(params.get("open_in_browser", False)):
            if target.lower().startswith(("http://", "https://")):
                webbrowser.open(target)
                return f"Opened {platform} video in your browser."

        if player is not None and hasattr(player, "show_video"):
            if Path(target).expanduser().is_file():
                p_str = str(Path(target).expanduser())
                player.show_video(p_str, Path(p_str).name, muted=True)
                return f"Playing {Path(p_str).name} on the HUD."

            if is_direct_media_url(target):
                player.show_video(target, target.rsplit("/", 1)[-1][:48], muted=True)
                return "Playing direct video stream on the HUD."

            stream = resolve_playable_stream(target, cookies_browser=cookies_browser)
            if stream.ok and stream.video_url:
                try:
                    player.show_video(
                        stream.video_url,
                        f"{stream.platform}: {stream.title}" if stream.title else stream.platform,
                        muted=True,
                        audio_source=stream.audio_url,
                        headers=stream.http_headers,
                        webpage_url=stream.webpage_url,
                        platform=stream.platform,
                    )
                except TypeError:
                    player.show_video(
                        stream.video_url,
                        stream.title or target,
                        muted=True,
                        audio_source=stream.audio_url,
                    )
                return (
                    f"Playing {stream.platform} video '{stream.title}' on the display "
                    "(starts muted so the mic stays clear — ask to unmute anytime)."
                )

            if target.lower().startswith(("http://", "https://")):
                webbrowser.open(target)
                return (
                    f"Could not extract an inline stream ({stream.error}); "
                    f"opened the {platform} link in your browser instead."
                )
            return f"Could not play '{target}': {stream.error}"

        if target.lower().startswith(("http://", "https://")):
            webbrowser.open(target)
            return f"Opened {platform} video in your browser."
        return "No display is attached to play the video."

    # ── 3. SUMMARIZE / TRANSCRIBE VIDEO ───────────────────────────────────────
    if action in ("summarize", "summary", "transcribe", "analyze"):
        if player is not None and hasattr(player, "write_log"):
            player.write_log(f"[Video] Analyzing {platform} video…")

        focus = str(params.get("focus") or "").strip()
        res_sum = summarize_media(target, focus=focus, cookies_browser=cookies_browser)
        if not res_sum.get("ok"):
            return f"Could not summarize that {platform} video: {res_sum.get('error')}"

        title = res_sum.get("title") or f"{res_sum.get('platform')} Video"
        body = str(res_sum.get("summary") or "").strip()
        if player is not None and hasattr(player, "show_content"):
            try:
                player.show_content(f"{res_sum.get('platform')} Summary — {title[:32]}", body)
            except Exception:
                pass
        return f"{res_sum.get('platform')} Summary ({title}):\n{body}"

    # ── 4. INSPECT METADATA ───────────────────────────────────────────────────
    if action in ("info", "get_info", "metadata", "details"):
        meta = get_media_info(target, cookies_browser=cookies_browser)
        if not meta.get("ok"):
            return f"Could not fetch {platform} video info: {meta.get('error')}"

        lines = [
            f"Platform : {meta.get('platform')}",
            f"Title    : {meta.get('title') or 'Untitled'}",
        ]
        if meta.get("uploader"):
            lines.append(f"Creator  : {meta['uploader']}")
        if meta.get("duration"):
            lines.append(f"Duration : {_format_duration(int(meta['duration']))}")
        if meta.get("view_count") is not None:
            lines.append(f"Views    : {int(meta['view_count']):,}")
        if meta.get("like_count") is not None:
            lines.append(f"Likes    : {int(meta['like_count']):,}")
        if meta.get("description"):
            lines.append(f"Caption  : {meta['description'][:400]}")
        out = "\n".join(lines)
        if player is not None and hasattr(player, "show_content"):
            try:
                player.show_content(f"{meta.get('platform')} Video Info", out)
            except Exception:
                pass
        return out

    return (
        f"Unknown action '{action}'. Supported actions: "
        "download, play, summarize, info."
    )


TOOL = {
    "name": "social_video",
    "description": (
        "Universal video & audio tool for Instagram (Reels, Posts, Stories, IGTV), "
        "YouTube (Videos, Shorts, Music), Snapchat (Spotlight, Public Stories), "
        "TikTok, X / Twitter, Facebook, Reddit, Twitch, Vimeo, SoundCloud, Pinterest, "
        "LinkedIn, and 1,800+ other sites. Use to DOWNLOAD videos (.mp4) or audio (.mp3), "
        "PLAY social/web videos on the HUD, SUMMARIZE spoken/captioned content from "
        "any video or reel, or get video INFO. If the user says 'download this video' "
        "without giving a URL, leave `url` empty to automatically use the link on their clipboard."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "'download' (save MP4/MP3), 'play' (watch on HUD), 'summarize' (transcribe & summarize), or 'info' (metadata).",
                "enum": ["download", "play", "summarize", "info"],
            },
            "url": {
                "type": "STRING",
                "description": "Video URL from Instagram, YouTube, Snapchat, TikTok, X, Reddit, etc. (or search phrase). Omit to auto-read copied URL from clipboard.",
            },
            "audio_only": {
                "type": "BOOLEAN",
                "description": "For action='download': true to extract MP3 audio only, false (default) for MP4 video.",
            },
            "quality": {
                "type": "STRING",
                "description": "Preferred video quality for download: 'best' (default), '4k', '1080p', '720p', or '480p'.",
            },
            "destination": {
                "type": "STRING",
                "description": "Where to save downloads: 'Downloads' (default), 'Desktop', 'Videos', or a folder path.",
            },
            "open_after": {
                "type": "BOOLEAN",
                "description": "Open the downloaded file immediately in the system media player after saving.",
            },
            "reveal_folder": {
                "type": "BOOLEAN",
                "description": "Reveal the saved file inside Explorer / Finder after downloading.",
            },
            "play_in_hud": {
                "type": "BOOLEAN",
                "description": "Play the downloaded video right inside JARVIS's HUD once saved.",
            },
            "focus": {
                "type": "STRING",
                "description": "Optional specific question or angle when summarizing a video.",
            },
            "cookies_browser": {
                "type": "STRING",
                "description": "Optional browser name ('chrome', 'edge', 'firefox', 'brave', 'safari') to read login cookies if a video is age-gated or private.",
            },
        },
        "required": ["action"],
    },
    "handler": social_video,
}
