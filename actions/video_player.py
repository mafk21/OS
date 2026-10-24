"""
Play a video where the avatar normally is (both 3D Web HUD & Classic PyQt6).

WHAT IT ACCEPTS
    • a local file        C:\\Users\\me\\clip.mp4, ~/Videos/holiday.mkv
    • a direct media URL  https://example.com/trailer.mp4
    • ANY social/web link Instagram Reel/Post, YouTube Video/Short, Snapchat
                          Spotlight/Story, TikTok, X/Twitter, Reddit, Facebook,
                          Twitch, Vimeo, Dailymotion, and 1,800+ yt-dlp sites
    • a search phrase     "play the new Dune trailer"
    • clipboard fallback  saying "play this video" when a link is copied

SOUND IS OFF UNTIL ASKED FOR
    Starts muted so a video's soundtrack never talks into JARVIS's open
    microphone unless the user clicks Unmute in the HUD player or asks JARVIS
    to turn sound on.
"""
from __future__ import annotations

from pathlib import Path
import threading
import webbrowser

from core.media_engine import (
    detect_platform,
    extract_url_from_text_or_clipboard,
    is_direct_media_url,
    resolve_playable_stream,
)

_open_lock = threading.Lock()
_open_seq = 0


def _begin_open() -> int:
    global _open_seq
    with _open_lock:
        _open_seq += 1
        return _open_seq


def _still_wanted(token: int) -> bool:
    with _open_lock:
        return token == _open_seq


def _is_url(text: str) -> bool:
    return text.lower().startswith(("http://", "https://", "file://"))


def _local_path(text: str) -> str:
    raw = (text or "").strip().strip('"').strip("'")
    if not raw:
        return ""
    try:
        p = Path(raw).expanduser()
        if p.exists() and p.is_file():
            return str(p)
    except Exception:
        pass
    return ""


def _resolve_youtube(url_or_query: str) -> tuple[str, str, str, str]:
    """Backwards-compatible helper returning (video_url, audio_url, title, error) for any platform."""
    stream = resolve_playable_stream(url_or_query, max_height=720)
    if stream.ok:
        return stream.video_url, stream.audio_url, stream.title, ""
    return "", "", "", stream.error


def _search_page(query: str) -> str:
    from urllib.parse import quote_plus

    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"


def _call_show_video(
    player,
    source: str,
    title: str,
    *,
    muted: bool = True,
    audio_source: str = "",
    headers: dict[str, str] | None = None,
    webpage_url: str = "",
    platform: str = "",
) -> None:
    try:
        player.show_video(
            source,
            title,
            muted=muted,
            audio_source=audio_source,
            headers=headers or {},
            webpage_url=webpage_url,
            platform=platform,
        )
    except TypeError:
        player.show_video(source, title, muted=muted, audio_source=audio_source)


def video_player(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    params = parameters or {}
    action = (params.get("action") or "play").strip().lower()
    source = (params.get("source") or "").strip()

    if player is None:
        return "There is no display to play a video on."

    # ---- stop -------------------------------------------------------------
    if action in ("stop", "close", "hide"):
        was_opening = not player.video_is_playing()
        _begin_open()
        player.stop_video()
        if was_opening:
            return "Stopped it before it opened."
        return "Closed the video."

    # ---- sound ------------------------------------------------------------
    if action in ("mute", "unmute", "sound_on", "sound_off"):
        if not player.video_is_playing():
            return "Nothing is playing."
        muted = action in ("mute", "sound_off")
        player.set_video_muted(muted)
        return "Muted the video." if muted else "Turned the video's sound on."

    # ---- play -------------------------------------------------------------
    if not source or "clipboard" in source.lower():
        clip_url = extract_url_from_text_or_clipboard(source, allow_clipboard=True)
        if clip_url:
            source = clip_url

    if not source:
        return "What should I play?"

    local = _local_path(source)
    if local:
        _call_show_video(
            player,
            local,
            Path(local).name,
            muted=True,
            platform="Local",
        )
        return f"Playing {Path(local).name} on the display, muted."

    # Direct media file URL (.mp4/.webm/.m3u8) goes straight to the player;
    # ANY social/web page URL (Instagram, YouTube, Snapchat, TikTok, X, Reddit, etc.)
    # resolves through yt-dlp on a background thread.
    if _is_url(source) and is_direct_media_url(source):
        _call_show_video(
            player,
            source,
            source.rsplit("/", 1)[-1][:48],
            muted=True,
            webpage_url=source,
            platform=detect_platform(source),
        )
        return "Playing that on the display, muted."

    threading.Thread(
        target=_play_resolved,
        args=(player, source, _begin_open()),
        daemon=True,
        name="video-open",
    ).start()
    return f"status=opening source={source}"


def _play_resolved(player, source: str, token: int) -> None:
    try:
        stream = resolve_playable_stream(source, max_height=720)
    except Exception as exc:  # noqa: BLE001
        stream = None
        err = str(exc)
    else:
        err = stream.error if stream else "unknown error"

    if not _still_wanted(token):
        return

    if stream and stream.ok and stream.video_url:
        try:
            label = (
                f"{stream.platform}: {stream.title}"
                if stream.title and stream.platform not in ("Web", "YouTube")
                else (stream.title or source)
            )
            _call_show_video(
                player,
                stream.video_url,
                label,
                muted=True,
                audio_source=stream.audio_url,
                headers=stream.http_headers,
                webpage_url=stream.webpage_url,
                platform=stream.platform,
            )
            return
        except Exception as exc:  # noqa: BLE001
            err = str(exc)

    page = source if _is_url(source) else _search_page(source)
    opened = ""
    try:
        webbrowser.open(page)
        opened = " and it has been opened in the browser instead"
    except Exception:
        pass
    _say(
        player,
        "Tell the user, in one short sentence in their own language: "
        f"'{source}' could not be played on the display ({err}){opened}.",
    )


def _say(player, instruction: str) -> None:
    if player is not None and hasattr(player, "request_say"):
        try:
            player.request_say(instruction)
        except Exception:
            pass


TOOL = {
    "name": "video_player",
    "description": (
        "Plays a VIDEO directly on JARVIS's own HUD display (and stops, mutes, "
        "or unmutes it). Supports Instagram Reels/Posts, YouTube Videos/Shorts, "
        "Snapchat Spotlights/Stories, TikTok, X / Twitter, Reddit, Facebook, "
        "Twitch, Vimeo, any yt-dlp video URL, local video files, direct .mp4 "
        "URLs, or spoken search queries ('play the new Dune trailer'). "
        "Video always starts MUTED — only call action='unmute' when the user "
        "asks to hear the audio. For DOWNLOADING videos/audio to disk, use "
        "'social_video' with action='download'."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "'play' (default), 'stop' to close it, 'unmute' to turn sound on, 'mute' to silence it.",
                "enum": ["play", "stop", "mute", "unmute"],
            },
            "source": {
                "type": "STRING",
                "description": (
                    "For action='play': any video URL (Instagram, YouTube, Snapchat, "
                    "TikTok, X, Reddit, etc.), local file path, or search query. "
                    "Omit to play a link currently copied on the clipboard."
                ),
            },
        },
        "required": ["action"],
    },
    "handler": video_player,
}
