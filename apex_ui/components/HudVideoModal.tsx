"use client";

import React, { useEffect, useRef, useState } from "react";
import {
  ExternalLink,
  ListMusic,
  SkipBack,
  SkipForward,
  Volume2,
  VolumeX,
  X,
} from "lucide-react";
import { useJarvis } from "./JarvisBridge";

function formatSec(sec?: number): string {
  if (!sec || sec <= 0) return "";
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

export default function HudVideoModal() {
  const {
    video,
    theme,
    activePersona,
    closeVideo,
    setVideoMuted,
    nextVideo,
    prevVideo,
    jumpVideo,
  } = useJarvis();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [queueOpen, setQueueOpen] = useState(false);

  useEffect(() => {
    const v = videoRef.current;
    const a = audioRef.current;
    if (!v || !video) return;

    const hasSplitAudio = Boolean(video.audio_url && a);
    v.muted = hasSplitAudio ? true : Boolean(video.muted);
    if (a) {
      a.muted = Boolean(video.muted);
    }

    const syncPlay = () => {
      if (a && hasSplitAudio) {
        if (Math.abs(a.currentTime - v.currentTime) > 0.28) {
          a.currentTime = v.currentTime;
        }
        a.play().catch(() => {});
      }
    };
    const syncPause = () => {
      if (a && hasSplitAudio) a.pause();
    };
    const syncSeek = () => {
      if (a && hasSplitAudio) {
        a.currentTime = v.currentTime;
      }
    };

    v.addEventListener("play", syncPlay);
    v.addEventListener("playing", syncPlay);
    v.addEventListener("pause", syncPause);
    v.addEventListener("seeked", syncSeek);
    return () => {
      v.removeEventListener("play", syncPlay);
      v.removeEventListener("playing", syncPlay);
      v.removeEventListener("pause", syncPause);
      v.removeEventListener("seeked", syncSeek);
    };
  }, [video]);

  if (!video) return null;

  const isFemale = activePersona === "female";
  const primary = theme.primary;
  const secondary = theme.secondary;
  const platformLabel = (video.platform || "VIDEO").toUpperCase();
  const queue = Array.isArray(video.queue) ? video.queue : [];
  const queueTotal = video.queue_total || queue.length;
  const queueIndex = video.queue_index || 0;
  const hasQueue = queueTotal > 1;

  const reportEnded = () => {
    // This is the browser's real HTMLMediaElement ended event—not a duration
    // estimate. Retry the local handoff because a dropped completion event is
    // worse than a duplicate (the durable manager deduplicates by task state).
    const payload = JSON.stringify({
      action: "video_ended",
      video_id: video.id,
      webpage_url: video.webpage_url || "",
      playlist_url: video.playlist_url || "",
      queue_index: queueIndex,
      queue_total: queueTotal,
      terminal: !hasQueue || queueIndex >= queueTotal - 1,
    });
    const send = async () => {
      for (const waitMs of [0, 250, 750]) {
        if (waitMs) await new Promise((resolve) => setTimeout(resolve, waitMs));
        try {
          const response = await fetch("/api/hud/action", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: payload,
          });
          if (response.ok) return;
        } catch {}
      }
    };
    void send();
  };

  return (
    <div
      data-testid="hud-video-player"
      style={{
        position: "fixed",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        width: "min(780px, calc(100vw - 40px))",
        maxHeight: "calc(100vh - 120px)",
        zIndex: 85,
        display: "flex",
        flexDirection: "column",
        borderRadius: 20,
        background: isFemale
          ? "linear-gradient(165deg, rgba(18, 7, 24, 0.94), rgba(8, 3, 12, 0.96))"
          : "linear-gradient(165deg, rgba(4, 12, 22, 0.94), rgba(2, 6, 13, 0.96))",
        border: `1px solid rgba(${theme.orbGlowRgb}, 0.42)`,
        boxShadow: `0 28px 70px rgba(0, 0, 0, 0.78), 0 0 42px rgba(${theme.orbGlowRgb}, 0.16)`,
        backdropFilter: "blur(22px)",
        overflow: "hidden",
      }}
    >
      {/* Top Bar */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: "10px 14px",
          borderBottom: "1px solid rgba(255,255,255,0.08)",
        }}
      >
        <span
          style={{
            padding: "3px 9px",
            borderRadius: 999,
            background: `rgba(${theme.orbGlowRgb}, 0.16)`,
            border: `1px solid rgba(${theme.orbGlowRgb}, 0.45)`,
            color: primary,
            fontFamily: "var(--font-mono), monospace",
            fontSize: 9.5,
            letterSpacing: "0.14em",
            flexShrink: 0,
          }}
        >
          {platformLabel}
        </span>

        {hasQueue && (
          <span
            data-testid="hud-video-mix-badge"
            title={video.playlist_title || "Active Mix / Playlist"}
            style={{
              padding: "3px 9px",
              borderRadius: 999,
              background: `rgba(${theme.orbGlow2Rgb}, 0.16)`,
              border: `1px solid rgba(${theme.orbGlow2Rgb}, 0.45)`,
              color: secondary,
              fontFamily: "var(--font-mono), monospace",
              fontSize: 9.5,
              letterSpacing: "0.10em",
              flexShrink: 0,
            }}
          >
            MIX · {queueIndex + 1}/{queueTotal}
          </span>
        )}

        <div
          style={{
            flex: 1,
            minWidth: 0,
            color: "#f2efe9",
            fontSize: 12.5,
            fontWeight: 500,
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
          title={video.title}
        >
          {video.title}
        </div>

        {hasQueue && (
          <>
            <button
              type="button"
              onClick={() => prevVideo()}
              title="Previous track in Mix"
              style={{
                width: 28,
                height: 28,
                borderRadius: "50%",
                border: "1px solid rgba(255,255,255,0.18)",
                background: "rgba(255,255,255,0.05)",
                color: "#e2e8f0",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
                padding: 0,
                flexShrink: 0,
              }}
            >
              <SkipBack size={12} />
            </button>

            <button
              type="button"
              onClick={() => nextVideo()}
              title="Next track in Mix"
              style={{
                width: 28,
                height: 28,
                borderRadius: "50%",
                border: "1px solid rgba(255,255,255,0.18)",
                background: "rgba(255,255,255,0.05)",
                color: "#e2e8f0",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
                padding: 0,
                flexShrink: 0,
              }}
            >
              <SkipForward size={12} />
            </button>

            <button
              type="button"
              onClick={() => setQueueOpen((prev) => !prev)}
              title="Toggle Mix tracklist"
              style={{
                height: 28,
                padding: "0 9px",
                borderRadius: 999,
                border: `1px solid ${queueOpen ? primary : "rgba(255,255,255,0.18)"}`,
                background: queueOpen
                  ? `rgba(${theme.orbGlowRgb}, 0.18)`
                  : "rgba(255,255,255,0.05)",
                color: queueOpen ? primary : "#dbe6f2",
                fontFamily: "var(--font-mono), monospace",
                fontSize: 9.5,
                letterSpacing: "0.08em",
                display: "inline-flex",
                alignItems: "center",
                gap: 4,
                cursor: "pointer",
                flexShrink: 0,
              }}
            >
              <ListMusic size={12} />
              QUEUE
            </button>
          </>
        )}

        <button
          type="button"
          onClick={() => setVideoMuted(!video.muted)}
          title={video.muted ? "Turn video sound on" : "Mute video sound"}
          style={{
            height: 28,
            padding: "0 10px",
            borderRadius: 999,
            border: `1px solid ${video.muted ? `${secondary}66` : `${primary}66`}`,
            background: video.muted
              ? `rgba(${theme.orbGlow2Rgb}, 0.14)`
              : `rgba(${theme.orbGlowRgb}, 0.16)`,
            color: video.muted ? secondary : primary,
            fontFamily: "var(--font-mono), monospace",
            fontSize: 9.5,
            letterSpacing: "0.10em",
            display: "inline-flex",
            alignItems: "center",
            gap: 5,
            cursor: "pointer",
            flexShrink: 0,
          }}
        >
          {video.muted ? <VolumeX size={12} /> : <Volume2 size={12} />}
          {video.muted ? "MUTED" : "SOUND ON"}
        </button>

        {video.webpage_url && (
          <a
            href={video.webpage_url}
            target="_blank"
            rel="noopener noreferrer"
            title="Open original page"
            style={{
              height: 28,
              padding: "0 9px",
              borderRadius: 999,
              border: "1px solid rgba(255,255,255,0.16)",
              background: "rgba(255,255,255,0.04)",
              color: "#dbe6f2",
              fontFamily: "var(--font-mono), monospace",
              fontSize: 9.5,
              display: "inline-flex",
              alignItems: "center",
              gap: 4,
              textDecoration: "none",
              flexShrink: 0,
            }}
          >
            <ExternalLink size={11} />
            SOURCE
          </a>
        )}

        <button
          type="button"
          onClick={() => closeVideo()}
          title="Close video"
          style={{
            width: 28,
            height: 28,
            borderRadius: "50%",
            border: "1px solid rgba(255,255,255,0.16)",
            background: "rgba(255,255,255,0.05)",
            color: "#e2e8f0",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            padding: 0,
            flexShrink: 0,
          }}
        >
          <X size={13} />
        </button>
      </div>

      {/* Video Surface */}
      <div
        style={{
          position: "relative",
          background: "#000",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          maxHeight: queueOpen && hasQueue ? "calc(100vh - 340px)" : "calc(100vh - 190px)",
        }}
      >
        <video
          key={video.id}
          ref={videoRef}
          src={video.video_url}
          autoPlay
          playsInline
          controls
          muted={Boolean(video.audio_url) ? true : video.muted}
          onEnded={() => {
            reportEnded();
            if (hasQueue) {
              nextVideo();
            }
          }}
          style={{
            width: "100%",
            maxHeight: queueOpen && hasQueue ? "calc(100vh - 340px)" : "calc(100vh - 190px)",
            objectFit: "contain",
            display: "block",
          }}
        />
        {video.audio_url && (
          <audio
            key={`${video.id}-aud`}
            ref={audioRef}
            src={video.audio_url}
            autoPlay
            muted={video.muted}
            style={{ display: "none" }}
          />
        )}
      </div>

      {/* Collapsible Mix / Playlist Tracklist Drawer */}
      {hasQueue && queueOpen && (
        <div
          data-testid="hud-video-queue-drawer"
          style={{
            maxHeight: 165,
            overflowY: "auto",
            borderTop: "1px solid rgba(255,255,255,0.08)",
            background: "rgba(2, 6, 14, 0.86)",
            padding: "6px 10px",
          }}
        >
          {video.playlist_title && (
            <div
              style={{
                padding: "4px 6px 6px",
                color: secondary,
                fontFamily: "var(--font-mono), monospace",
                fontSize: 9.5,
                letterSpacing: "0.12em",
                textTransform: "uppercase",
              }}
            >
              {video.playlist_title}
            </div>
          )}
          {queue.map((item, idx) => {
            const active = idx === queueIndex;
            return (
              <button
                key={`${item.id || idx}-${idx}`}
                type="button"
                onClick={() => jumpVideo(idx)}
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "6px 8px",
                  borderRadius: 8,
                  border: active
                    ? `1px solid rgba(${theme.orbGlowRgb}, 0.45)`
                    : "1px solid transparent",
                  background: active
                    ? `rgba(${theme.orbGlowRgb}, 0.14)`
                    : "transparent",
                  color: active ? primary : "#dbe6f2",
                  fontSize: 11.5,
                  textAlign: "left",
                  cursor: "pointer",
                }}
              >
                <span
                  style={{
                    width: 24,
                    fontFamily: "var(--font-mono), monospace",
                    fontSize: 10,
                    opacity: 0.72,
                    flexShrink: 0,
                  }}
                >
                  {String(idx + 1).padStart(2, "0")}
                </span>
                <span
                  style={{
                    flex: 1,
                    minWidth: 0,
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                  }}
                >
                  {item.title}
                  {item.uploader ? (
                    <span style={{ opacity: 0.62, marginLeft: 6 }}>
                      · {item.uploader}
                    </span>
                  ) : null}
                </span>
                {item.duration ? (
                  <span
                    style={{
                      fontFamily: "var(--font-mono), monospace",
                      fontSize: 10,
                      opacity: 0.65,
                      flexShrink: 0,
                    }}
                  >
                    {formatSec(item.duration)}
                  </span>
                ) : null}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
