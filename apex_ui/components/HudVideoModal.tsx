"use client";

import React, { useEffect, useRef } from "react";
import { ExternalLink, Volume2, VolumeX, X } from "lucide-react";
import { useJarvis } from "./JarvisBridge";

export default function HudVideoModal() {
  const { video, theme, activePersona, closeVideo, setVideoMuted } = useJarvis();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

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

  return (
    <div
      data-testid="hud-video-player"
      style={{
        position: "fixed",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        width: "min(760px, calc(100vw - 40px))",
        maxHeight: "calc(100vh - 130px)",
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
          gap: 10,
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
          maxHeight: "calc(100vh - 190px)",
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
          style={{
            width: "100%",
            maxHeight: "calc(100vh - 190px)",
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
    </div>
  );
}
