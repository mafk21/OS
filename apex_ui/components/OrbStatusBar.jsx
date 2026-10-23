"use client";

const GOLD = '#f5a623'
const GOLD_BRIGHT = '#ffd080'
const CYAN = '#00e5ff'

function Waveform({ active, level = 0, speaking = false, cx, cy, width = 200 }) {
  const barCount = 28
  const barW = 3
  const gap = (width - barCount * barW) / (barCount - 1)
  const lv = Math.max(0, Math.min(1, Number(level) || 0))
  const hasLiveSignal = lv > 0.02

  return (
    <g>
      {Array.from({ length: barCount }, (_, i) => {
        const x = cx - width / 2 + i * (barW + gap)
        const distCenter = 1 - Math.abs(i - (barCount - 1) / 2) / ((barCount - 1) / 2)
        const baseH = 3 + Math.abs(Math.sin(i * 0.6)) * 5
        const liveBoost = (6 + distCenter * 28 + Math.abs(Math.sin(i * 1.15)) * 12) * Math.min(1, lv * 2.2)
        const activeH = hasLiveSignal
          ? Math.max(baseH, 4 + liveBoost)
          : (speaking ? 8 + Math.abs(Math.sin(i * 0.8)) * 24 : 5 + Math.abs(Math.sin(i * 0.7)) * 10)
        const h = active ? activeH : baseH
        return (
          <rect key={i} x={x} y={cy - h / 2}
            width={barW} height={h}
            rx={1.5} fill={GOLD} opacity={active ? 0.88 : 0.3}
            style={{
              transformOrigin: `${x + barW / 2}px ${cy}px`,
              transition: hasLiveSignal ? 'height 60ms linear, y 60ms linear' : undefined,
              animation: (active && !hasLiveSignal)
                ? `sbBar ${0.55 + (i % 5) * 0.16}s ease-in-out ${(i % 7) * 0.07}s infinite alternate`
                : 'none',
            }} />
        )
      })}
    </g>
  )
}

export default function OrbStatusBar({ state = 'idle', rawState = '', level = 0, subtitle = null }) {
  const W = 440, H = 112
  const cx = W / 2, cy = 38
  const isActive = state !== 'idle'
  const rawUpper = String(rawState || '').toUpperCase()
  const label =
    rawUpper === 'MUTED' ? 'MICROPHONE MUTED' :
    rawUpper === 'PAUSED' ? 'PAUSED' :
    state === 'listening' ? 'LISTENING' :
    state === 'speaking' ? 'SPEAKING' :
    state === 'thinking' ? 'PROCESSING' :
    'STANDBY'

  return (
    <div style={{
      position: 'absolute', left: 0, right: 0, bottom: 58, display: 'flex',
      flexDirection: 'column', alignItems: 'center', zIndex: 18, pointerEvents: 'none',
    }}>
      <style>{`@keyframes sbBar { from { transform: scaleY(0.35); } to { transform: scaleY(1.15); } }`}</style>

      {subtitle && subtitle.text && (
        <div style={{
          maxWidth: 'min(680px, 88vw)',
          marginBottom: 4,
          padding: '5px 14px',
          borderRadius: 14,
          background: 'rgba(4, 10, 20, 0.72)',
          border: `1px solid ${subtitle.role === 'user' ? 'rgba(0,229,255,0.28)' : 'rgba(245,166,35,0.28)'}`,
          backdropFilter: 'blur(10px)',
          fontSize: 12,
          lineHeight: 1.45,
          color: 'rgba(240,237,232,0.9)',
          textAlign: 'center',
          overflow: 'hidden',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
        }}>
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 9.5,
            letterSpacing: '0.16em',
            marginRight: 8,
            color: subtitle.role === 'user' ? CYAN : GOLD,
            textTransform: 'uppercase',
          }}>
            {subtitle.role === 'user' ? 'YOU' : 'JARVIS'}
          </span>
          {subtitle.text}
        </div>
      )}

      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} fill="none">
        <defs>
          <filter id="sbBlur" x="-60%" y="-60%" width="220%" height="220%">
            <feGaussianBlur stdDeviation="4" result="b" />
            <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>

        <line x1={cx - 150} y1={cy} x2={cx - 28} y2={cy} stroke={GOLD} strokeWidth="1" opacity={isActive ? 0.5 : 0.18} strokeDasharray="4 3" />
        <line x1={cx + 28} y1={cy} x2={cx + 150} y2={cy} stroke={GOLD} strokeWidth="1" opacity={isActive ? 0.5 : 0.18} strokeDasharray="4 3" />

        <Waveform active={isActive} level={level} speaking={state === 'speaking'} cx={cx} cy={cy} width={170} />

        <circle cx={cx} cy={cy} r={20} stroke={GOLD} strokeWidth="1.5" strokeOpacity="0.7" fill="#030200" filter="url(#sbBlur)" className="orb-center-ring" />
        <circle cx={cx} cy={cy} r={6} fill={GOLD_BRIGHT} opacity="0.95" className="orb-center" style={{ filter: `drop-shadow(0 0 10px ${GOLD})` }} />

        <text x={cx} y={cy + 42} textAnchor="middle" fill={GOLD} fontSize="12" fontFamily="'Share Tech Mono', monospace" letterSpacing="0.38em" opacity="0.8">{label}</text>

        {[0, 1, 2].map(i => (
          <circle key={i} cx={cx + (i - 1) * 12} cy={cy + 58} r={2.4} fill={GOLD} className={`orb-dot-blink blink-${i}`} />
        ))}

        {!isActive && (
          <text className="sb-hint" x={cx} y={cy + 73} textAnchor="middle" fill={GOLD} fontSize="8.5" fontFamily="'Share Tech Mono', monospace"
            letterSpacing="0.14em" opacity="0.34">TAP THE CORE · CLICK AN AGENT · SPEAK OR TYPE BELOW</text>
        )}
      </svg>
    </div>
  )
}
