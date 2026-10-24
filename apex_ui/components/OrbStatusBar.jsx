"use client";

import { useJarvis, useJarvisAudioLevel } from "./JarvisBridge";

function Waveform({
  active,
  level = 0,
  speaking = false,
  cx,
  cy,
  width = 200,
  color = "#f5a623",
}) {
  const barCount = 28;
  const barW = 3;
  const gap = (width - barCount * barW) / (barCount - 1);
  const lv = Math.max(0, Math.min(1, Number(level) || 0));
  const hasLiveSignal = lv > 0.02;

  return (
    <g>
      {Array.from({ length: barCount }, (_, i) => {
        const x = cx - width / 2 + i * (barW + gap);
        const distCenter =
          1 - Math.abs(i - (barCount - 1) / 2) / ((barCount - 1) / 2);
        const baseH = 3 + Math.abs(Math.sin(i * 0.6)) * 5;
        const liveBoost =
          (6 + distCenter * 28 + Math.abs(Math.sin(i * 1.15)) * 12) *
          Math.min(1, lv * 2.2);
        const activeH = hasLiveSignal
          ? Math.max(baseH, 4 + liveBoost)
          : speaking
          ? 8 + Math.abs(Math.sin(i * 0.8)) * 24
          : 5 + Math.abs(Math.sin(i * 0.7)) * 10;
        const h = active ? activeH : baseH;
        return (
          <rect
            key={i}
            x={x}
            y={cy - h / 2}
            width={barW}
            height={h}
            rx={1.5}
            fill={color}
            opacity={active ? 0.88 : 0.3}
            style={{
              transformOrigin: `${x + barW / 2}px ${cy}px`,
              transition: hasLiveSignal
                ? "height 60ms linear, y 60ms linear"
                : undefined,
              animation:
                active && !hasLiveSignal
                  ? `sbBar ${0.55 + (i % 5) * 0.16}s ease-in-out ${
                      (i % 7) * 0.07
                    }s infinite alternate`
                  : "none",
            }}
          />
        );
      })}
    </g>
  );
}

export default function OrbStatusBar({
  state = "idle",
  rawState = "",
  level = undefined,
  subtitle = null,
}) {
  const { theme, assistantName } = useJarvis();
  const ctxLevel = useJarvisAudioLevel();
  const effLevel = level !== undefined ? level : ctxLevel;
  const PRIMARY = theme.primary;
  const GOLD = theme.secondary;
  const GOLD_BRIGHT = theme.secondaryBright;

  const W = 240,
    H = 54;
  const cx = W / 2,
    cy = 18;
  const isActive = state !== "idle";
  const waveColor = state === "speaking" ? GOLD : PRIMARY;
  const rawUpper = String(rawState || "").toUpperCase();
  const label =
    rawUpper === "MUTED"
      ? "MUTED"
      : rawUpper === "PAUSED"
      ? "PAUSED"
      : state === "listening"
      ? "LISTENING"
      : state === "speaking"
      ? "SPEAKING"
      : state === "thinking"
      ? "PROCESSING"
      : "STANDBY";

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom: 58,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        zIndex: 18,
        pointerEvents: "none",
      }}
    >
      <style>{`@keyframes sbBar { from { transform: scaleY(0.35); } to { transform: scaleY(1.15); } }`}</style>

      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} fill="none">
        <Waveform
          active={isActive}
          level={effLevel}
          speaking={state === "speaking"}
          cx={cx}
          cy={cy}
          width={136}
          color={waveColor}
        />

        <circle
          cx={cx}
          cy={cy}
          r={4.5}
          fill={state === "speaking" ? GOLD_BRIGHT : PRIMARY}
          opacity="0.92"
          style={{ filter: `drop-shadow(0 0 8px ${waveColor})` }}
        />

        <text
          x={cx}
          y={cy + 26}
          textAnchor="middle"
          fill={waveColor}
          fontSize="9.5"
          fontFamily="'Share Tech Mono', monospace"
          letterSpacing="0.34em"
          opacity="0.72"
        >
          {label}
        </text>
      </svg>
    </div>
  );
}
