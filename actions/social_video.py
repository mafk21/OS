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
    classify_mix_or_playlist,
    clean_media_url,
    detect_platform,
    download_media,
    download_mix_or_playlist,
    extract_mix_or_playlist,
    extract_url_from_text_or_clipboard,
    get_media_info,
    is_direct_media_url,
    is_mix_or_playlist_url,
    resolve_playable_stream,
    summarize_media,
    summarize_mix_or_playlist,
    watch_media,
    watch_mix_or_playlist,
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
    single_only = bool(params.get("single_only", False))
    track_index_raw = params.get("track_index")
    track_index = int(track_index_raw) if track_index_raw not in (None, "") else None

    # Queue navigation controls on an active HUD Mix / Playlist
    if action in ("next", "skip"):
        if player is not None and hasattr(player, "next_video"):
            step = player.next_video()
            if step.get("ok"):
                return f"Playing Mix track {step['index'] + 1}/{step['total']}: {step['title']}."
            return str(step.get("error") or "No Mix queue is active on the HUD.")
        return "No HUD Mix queue is currently active."

    if action in ("previous", "prev", "back"):
        if player is not None and hasattr(player, "prev_video"):
            step = player.prev_video()
            if step.get("ok"):
                return f"Playing Mix track {step['index'] + 1}/{step['total']}: {step['title']}."
            return str(step.get("error") or "No Mix queue is active on the HUD.")
        return "No HUD Mix queue is currently active."

    if action in ("jump", "select_track") and track_index is not None:
        if player is not None and hasattr(player, "jump_video"):
            step = player.jump_video(max(0, track_index - 1))
            if step.get("ok"):
                return f"Jumped to Mix track {step['index'] + 1}/{step['total']}: {step['title']}."
            return str(step.get("error") or "No Mix queue is active on the HUD.")
        return "No HUD Mix queue is currently active."

    # Resolve URL from explicit argument, currently playing HUD Mix/video, or system clipboard
    resolved_url = extract_url_from_text_or_clipboard(
        raw_url,
        allow_clipboard=False,
    )
    target = clean_media_url(resolved_url or raw_url)
    wants_active_mix = any(k in raw_url.lower() for k in ("mix", "playlist"))
    if not target or target.lower() in ("current", "playing", "this", "it", "mix", "this mix", "playlist", "this playlist"):
        if player is not None:
            try:
                if (wants_active_mix or not single_only) and hasattr(player, "current_mix_source"):
                    cur_mix = (player.current_mix_source() or "").strip()
                    if cur_mix and (wants_active_mix or action in ("info", "summarize", "download")):
                        target = cur_mix
                if (not target or target.lower() in ("current", "playing", "this", "it", "mix", "this mix", "playlist", "this playlist")) and hasattr(player, "current_video_source"):
                    cur_vid = (player.current_video_source() or "").strip()
                    if cur_vid:
                        target = cur_vid
            except Exception:
                pass
    if not target or "clipboard" in target.lower():
        clip_u = extract_url_from_text_or_clipboard(raw_url, allow_clipboard=True)
        if clip_u:
            target = clip_u

    if not target:
        return (
            "Please share the video or YouTube Mix link (from Instagram, YouTube, Snapchat, TikTok, "
            "X, Reddit, or any other site), play it on the HUD, or copy it to your clipboard first."
        )

    platform = detect_platform(target)
    is_collection = (not single_only) and is_mix_or_playlist_url(target)
    collection_meta = classify_mix_or_playlist(target) if is_collection else {}
    collection_kind = str(collection_meta.get("kind") or "Mix / Playlist")

    # ── 1. DOWNLOAD VIDEO, AUDIO, OR ENTIRE MIX / PLAYLIST ────────────────────
    if action in ("download", "save", "dl", "audio", "mp3", "mp4"):
        audio_only = bool(params.get("audio_only", False)) or action in ("audio", "mp3")
        quality = str(params.get("quality") or "best").strip()
        destination = str(params.get("destination") or "Downloads").strip()
        open_after = bool(params.get("open_after", False))
        reveal_folder = bool(params.get("reveal_folder", False))
        play_in_hud = bool(params.get("play_in_hud", False))

        kind_lbl = "MP3 audio" if audio_only else "MP4 video"

        def _on_prog(msg: str) -> None:
            if player is not None and hasattr(player, "write_log"):
                player.write_log(f"[Video] {platform}: {msg}")

        if is_collection:
            max_items = int(params.get("max_items") or 10)
            if player is not None and hasattr(player, "write_log"):
                player.write_log(
                    f"[Mix] Downloading {collection_kind} ({kind_lbl}, up to {max_items} tracks)…"
                )
            mix_res = download_mix_or_playlist(
                target,
                output_dir=destination,
                audio_only=audio_only,
                quality=quality,
                max_items=max_items,
                cookies_browser=cookies_browser,
                progress_cb=_on_prog,
            )
            if not mix_res.ok:
                return f"Could not download {collection_kind}: {mix_res.error}"

            file_lines = "\n".join(
                f"  {Path(fp).name}" for fp in mix_res.files[:15]
            )
            if len(mix_res.files) > 15:
                file_lines += f"\n  … +{len(mix_res.files) - 15} more"
            mix_card = (
                f"Type     : {mix_res.kind} ({mix_res.platform})\n"
                f"Title    : {mix_res.title}\n"
                f"Format   : {'Audio (.mp3)' if mix_res.audio_only else 'Video (.mp4)'}\n"
                f"Tracks   : {len(mix_res.files)} downloaded ({mix_res.total_size_mb} MB)\n"
                f"Folder   : {mix_res.folder_path}\n"
                f"Files    :\n{file_lines}"
            )
            if player is not None and hasattr(player, "show_content"):
                try:
                    player.show_content(f"{mix_res.kind} Download Complete", mix_card)
                except Exception:
                    pass
            if reveal_folder or open_after:
                _open_local_file_or_folder(mix_res.files[0], reveal_folder=True)
            return (
                f"Downloaded {len(mix_res.files)} {'MP3 tracks' if mix_res.audio_only else 'MP4 videos'} "
                f"from {mix_res.kind} '{mix_res.title}' ({mix_res.total_size_mb} MB) to {mix_res.folder_path}."
            )

        if player is not None and hasattr(player, "write_log"):
            player.write_log(f"[Video] Downloading {platform} {kind_lbl}…")

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

    # ── 2. PLAY VIDEO OR MIX / PLAYLIST QUEUE IN HUD OR BROWSER ───────────────
    if action in ("play", "open"):
        if bool(params.get("open_in_browser", False)):
            if target.lower().startswith(("http://", "https://")):
                webbrowser.open(target)
                return f"Opened {platform} link in your browser."

        if player is not None and hasattr(player, "show_video"):
            if is_collection:
                max_q = int(params.get("max_items") or 25)
                coll = extract_mix_or_playlist(
                    target, max_items=max_q, cookies_browser=cookies_browser
                )
                if coll.ok and coll.tracks:
                    start_idx = (
                        max(0, min(len(coll.tracks) - 1, track_index - 1))
                        if track_index is not None
                        else coll.start_index
                    )
                    lead = coll.tracks[start_idx]
                    stream = resolve_playable_stream(lead.url, cookies_browser=cookies_browser)
                    if stream.ok and stream.video_url:
                        q_payload = [
                            {
                                "index": tr.index,
                                "id": tr.id,
                                "title": tr.title,
                                "uploader": tr.uploader,
                                "duration": tr.duration,
                                "url": tr.url,
                                "platform": tr.platform,
                            }
                            for tr in coll.tracks
                        ]
                        try:
                            player.show_video(
                                stream.video_url,
                                stream.title or lead.title,
                                muted=True,
                                audio_source=stream.audio_url,
                                headers=stream.http_headers,
                                webpage_url=stream.webpage_url or lead.url,
                                platform=stream.platform or coll.platform,
                                queue=q_payload,
                                queue_index=start_idx,
                                playlist_title=coll.title,
                                playlist_url=target,
                            )
                        except TypeError:
                            player.show_video(
                                stream.video_url,
                                stream.title or lead.title,
                                muted=True,
                                audio_source=stream.audio_url,
                            )
                        return (
                            f"Playing {coll.kind} '{coll.title}' on the HUD "
                            f"(starting at track {start_idx + 1}/{len(coll.tracks)}: '{stream.title or lead.title}'; "
                            "auto-advances through the Mix — use Next/Previous or the Queue drawer anytime)."
                        )

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

    # ── 3. VISUALLY WATCH / SEE FRAMES + AUDIO (SINGLE VIDEO OR MIX!) ─────────
    if action in ("watch", "see", "look", "describe", "inspect_visuals"):
        focus = str(params.get("focus") or params.get("question") or "").strip()
        if is_collection:
            if player is not None and hasattr(player, "write_log"):
                player.write_log(f"[Mix] Visually watching {collection_kind} keyframes…")
            max_tracks = int(params.get("max_items") or 3)
            res_mix_watch = watch_mix_or_playlist(
                target,
                question=focus,
                max_tracks=max_tracks,
                track_index=track_index,
                cookies_browser=cookies_browser,
            )
            if not res_mix_watch.get("ok"):
                return f"Could not visually inspect {collection_kind}: {res_mix_watch.get('error')}"
            m_title = res_mix_watch.get("title") or collection_kind
            f_n = int(res_mix_watch.get("frames_analyzed") or 0)
            body = str(res_mix_watch.get("analysis") or res_mix_watch.get("summary") or "").strip()
            if player is not None and hasattr(player, "show_content"):
                try:
                    player.show_content(
                        f"{res_mix_watch.get('kind', collection_kind)} Visual Watch ({f_n} frames) — {m_title[:24]}",
                        body,
                    )
                except Exception:
                    pass
            return (
                f"{res_mix_watch.get('kind', collection_kind)} Visual Analysis "
                f"('{m_title}', {f_n} keyframes inspected):\n{body}"
            )

        if player is not None and hasattr(player, "write_log"):
            player.write_log(f"[Video] Watching {platform} video frames & audio…")

        max_frames = int(params.get("max_frames") or 8)
        res_watch = watch_media(
            target,
            question=focus,
            max_frames=max_frames,
            cookies_browser=cookies_browser,
        )
        if not res_watch.get("ok"):
            return f"Could not visually inspect that {platform} video: {res_watch.get('error')}"

        title = res_watch.get("title") or f"{res_watch.get('platform')} Video"
        frames_n = int(res_watch.get("frames_analyzed") or 0)
        body = str(res_watch.get("analysis") or res_watch.get("summary") or "").strip()
        if player is not None and hasattr(player, "show_content"):
            try:
                player.show_content(
                    f"{res_watch.get('platform')} Visual Analysis ({frames_n} frames) — {title[:26]}",
                    body,
                )
            except Exception:
                pass
        return (
            f"{res_watch.get('platform')} Visual & Audio Analysis "
            f"({frames_n} keyframes inspected — {title}):\n{body}"
        )

    # ── 4. SUMMARIZE / TRANSCRIBE VIDEO OR MIX / PLAYLIST ─────────────────────
    if action in ("summarize", "summary", "transcribe", "analyze"):
        focus = str(params.get("focus") or "").strip()
        if is_collection:
            if player is not None and hasattr(player, "write_log"):
                player.write_log(f"[Mix] Summarizing {collection_kind}…")
            max_items = int(params.get("max_items") or 6)
            res_mix_sum = summarize_mix_or_playlist(
                target,
                focus=focus,
                max_items=max_items,
                cookies_browser=cookies_browser,
            )
            if not res_mix_sum.get("ok"):
                return f"Could not summarize {collection_kind}: {res_mix_sum.get('error')}"
            m_title = res_mix_sum.get("title") or collection_kind
            body = str(res_mix_sum.get("summary") or "").strip()
            if player is not None and hasattr(player, "show_content"):
                try:
                    player.show_content(
                        f"{res_mix_sum.get('kind', collection_kind)} Summary — {m_title[:28]}",
                        body,
                    )
                except Exception:
                    pass
            return (
                f"{res_mix_sum.get('kind', collection_kind)} Summary "
                f"('{m_title}', {res_mix_sum.get('track_count', 0)} tracks):\n{body}"
            )

        if player is not None and hasattr(player, "write_log"):
            player.write_log(f"[Video] Analyzing {platform} video…")

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

    # ── 5. INSPECT METADATA / TRACKLIST ───────────────────────────────────────
    if action in ("info", "get_info", "metadata", "details", "tracklist", "tracks"):
        if is_collection or action in ("tracklist", "tracks"):
            max_q = int(params.get("max_items") or 25)
            coll = extract_mix_or_playlist(
                target, max_items=max_q, cookies_browser=cookies_browser
            )
            if not coll.ok:
                return f"Could not fetch {collection_kind} tracklist: {coll.error}"
            lines = [
                f"Type     : {coll.kind} ({coll.platform})",
                f"Title    : {coll.title}",
                f"Tracks   : {len(coll.tracks)}",
                "",
            ]
            for tr in coll.tracks:
                dur = f" ({_format_duration(tr.duration)})" if tr.duration else ""
                by = f" — {tr.uploader}" if tr.uploader else ""
                lines.append(f"{tr.index + 1:02d}. {tr.title}{by}{dur}")
            out = "\n".join(lines)
            if player is not None and hasattr(player, "show_content"):
                try:
                    player.show_content(f"{coll.kind} Tracklist ({len(coll.tracks)})", out)
                except Exception:
                    pass
            return out

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
        "download, play, watch, summarize, info, next, previous, jump."
    )


TOOL = {
    "name": "social_video",
    "description": (
        "Universal multimodal video, audio, YouTube Mix (`watch?v=...&list=RD...`), and Playlist tool "
        "for Instagram (Reels, Posts, Stories, IGTV), YouTube (Videos, Shorts, Music, Radio Mixes, Playlists), "
        "Snapchat (Spotlight, Public Stories), TikTok, X / Twitter, Facebook, Reddit, Twitch, Vimeo, "
        "SoundCloud (tracks & sets), Pinterest, LinkedIn, local video files, and 1,800+ other sites. "
        "Supports BOTH single videos AND full YouTube Mixes / Playlists across every action: "
        "• 'watch': visually extract & see timestamped keyframes + audio across a video OR across a YouTube Mix/Playlist. "
        "• 'play': play inline on the 3D HUD (for Mixes/Playlists, loads the full queue with Prev/Next/Tracklist & auto-advance!). "
        "• 'download': save MP4 video(s) or MP3 audio (for Mixes/Playlists, saves a numbered folder of tracks!). "
        "• 'summarize' / 'info': summarize or inspect full Mix tracklists & metadata. "
        "• 'next' / 'previous' / 'jump': navigate tracks in an active HUD Mix queue."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "'watch' (visually see frames + audio), 'download' (save MP4/MP3 or full Mix folder), 'play' (play video or Mix queue on HUD), 'summarize', 'info' (metadata / Mix tracklist), 'next', 'previous', or 'jump'.",
                "enum": ["watch", "download", "play", "summarize", "info", "next", "previous", "jump"],
            },
            "url": {
                "type": "STRING",
                "description": "Video, YouTube Mix (`watch?v=...&list=RD...`), or Playlist URL, or local file path. Omit to act on the active HUD video/Mix or clipboard.",
            },
            "audio_only": {
                "type": "BOOLEAN",
                "description": "For action='download': true to extract MP3 audio (great for downloading a YouTube Mix as MP3 songs!), false (default) for MP4 video.",
            },
            "quality": {
                "type": "STRING",
                "description": "Preferred video quality for download: 'best' (default), '4k', '1080p', '720p', or '480p'.",
            },
            "destination": {
                "type": "STRING",
                "description": "Where to save downloads: 'Downloads' (default), 'Desktop', 'Videos', or a folder path.",
            },
            "max_items": {
                "type": "INTEGER",
                "description": "For YouTube Mixes & Playlists: max number of tracks to download (default 10, max 50), queue (default 25), summarize (default 6), or visually watch (default 3).",
            },
            "track_index": {
                "type": "INTEGER",
                "description": "1-based track number in a Mix/Playlist to start playing, jump to (action='jump'), or visually inspect (action='watch').",
            },
            "single_only": {
                "type": "BOOLEAN",
                "description": "Set true ONLY if the user explicitly wants just the single current video from a `watch?v=...&list=...` URL instead of the full Mix/Playlist.",
            },
            "open_after": {
                "type": "BOOLEAN",
                "description": "Open the downloaded file/folder immediately after saving.",
            },
            "reveal_folder": {
                "type": "BOOLEAN",
                "description": "Reveal the saved file/Mix folder inside Explorer / Finder after downloading.",
            },
            "play_in_hud": {
                "type": "BOOLEAN",
                "description": "Play the downloaded video right inside JARVIS's HUD once saved.",
            },
            "focus": {
                "type": "STRING",
                "description": "Specific visual/audio question when watching or summarizing (e.g. 'what vibe is this mix?', 'what car is in this reel?').",
            },
            "max_frames": {
                "type": "INTEGER",
                "description": "Number of evenly spaced visual keyframes (1–12, default 8) to inspect when watching a video.",
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
