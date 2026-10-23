"""Acoustic echo cancellation and human-voice barge-in detector.

Separates genuine user speech from:
  1.JARVIS's own voice leaking from loudspeakers back into the microphone
    (across arbitrary OS output buffer latencies up to ~900 ms and multi-path
    room reflections), and
  2. Non-speech microphone sounds — close-mic breathing/exhales, aspirated
    sighs, low-frequency wind puffs, keyboard/mouse clicks, and steady fan/AC
    or mains hum — even when loud.

At the same time, normal and quiet conversational speech (down to ~115 int16
RMS at desk distance, deep 85 Hz male voices with natural -6 to -12 dB/oct
glottal tilt, female/child voices, and crisp single-word commands such as
"Stop", "Wait", "No", "Hey" lasting ~128 ms = 2 blocks) passes immediately
from block #0 with zero warmup lockout on both headphones and loudspeakers.

Architecture (two-stage WebRTC-style AEC + harmonic pitch detector):
  - Stage 1 (Linear Waveform FDAF): Phase-continuous streaming resampler feeds
    a ~900 ms 16 kHz speaker reference ring. Generalized FFT cross-correlation
    automatically locks onto the OS + room acoustic delay, seeding a 1024-tap
    (64 ms) overlap-save Frequency-Domain Adaptive Filter that cancels linear
    multi-reflection speaker echo in the time domain while leaving uncorrelated
    user speech untouched.
  - Stage 2 (Nonlinear Residual / Fine-Bin Spectral Echo Suppressor): Cancels
    any unconverged reflection remnants around predicted echo harmonics (or
    acts as a phase-invariant fine-bin spectral echo canceller before waveform
    lock / under nonlinear laptop speaker distortion), flooring attenuated
    bins to the local inter-harmonic floor so smooth breath/sigh noise never
    acquires artificial comb notches.
  - Voiced Speech Classifier: Evaluates pre-emphasized formant balance,
    local harmonic-comb prominence, impulse concentration, and Wiener-Khinchin
    pitch autocorrelation at T0 and 2*T0 across 75–400 Hz.
"""

from __future__ import annotations

import threading
import time
import numpy as np

# Canonical internal analysis grid: 1024 samples (64 ms) @ 16 kHz, 2x-padded
# to 2048 FFT points (7.8125 Hz/bin) so even 80 Hz bass harmonics are ~10 bins apart.
_SR_STD = 16000
_N_STD = 1024
_NFFT_16K = 2048
_FREQS_16K = np.fft.rfftfreq(_NFFT_16K, 1.0 / _SR_STD)
_HANN_1024 = np.hanning(_N_STD).astype(np.float32)

# Pre-emphasis |1 - 0.95 e^{-jw}| compensates natural -6 to -12 dB/oct glottal roll-off.
_PE_WEIGHT = np.abs(
    1.0 - 0.95 * np.exp(-1j * 2.0 * np.pi * _FREQS_16K / _SR_STD)
).astype(np.float32)

# 19 Bark-like sub-bands (first 17 cover 110–3700 Hz core voiced speech).
_BARK_EDGES = (
    110, 165, 225, 295, 375, 465, 570, 690, 830,
    990, 1175, 1390, 1640, 1930, 2270, 2670, 3150, 3700, 4800, 6500,
)
_VOICE_BARK = 17
_BARK_BINS = [
    np.where((_FREQS_16K >= _BARK_EDGES[i]) & (_FREQS_16K < _BARK_EDGES[i + 1]))[0]
    for i in range(len(_BARK_EDGES) - 1)
]
_BARK_CENTERS = np.array(
    [0.5 * (_BARK_EDGES[i] + _BARK_EDGES[i + 1]) for i in range(_VOICE_BARK)],
    dtype=np.float32,
)

_BP_AC_MASK = ((_FREQS_16K >= 75.0) & (_FREQS_16K <= 1150.0)).astype(np.float32)
_SPEECH_MASK_120 = (_FREQS_16K >= 120.0) & (_FREQS_16K <= 3500.0)
_FINE_MASK = (_FREQS_16K >= 120.0) & (_FREQS_16K <= 3400.0)

# Speech-band RMS normalization (200–3500 Hz rejects <190 Hz wind puffs & >3.8 kHz hiss
# while registering quiet ~115 int16 RMS desk speech cleanly above ~0.03).
_PCM_FLOOR = 28.0
_PCM_FULL = 2350.0

# Echo history & adaptive filter constants
_WINDOW_S = 1.0
_FDAF_TAPS = 1024          # 64 ms room impulse response span @ 16 kHz
_MAX_DELAY_SAMPLES = 14400 # up to 900 ms OS + acoustic output latency


def _to_16k_frame(pcm: np.ndarray, sample_rate: int) -> np.ndarray:
    """Return a zero-mean 1024-sample float32 frame on the 16 kHz time grid."""
    x = np.asarray(pcm, dtype=np.float32).reshape(-1)
    if x.size == 0 or sample_rate <= 0:
        return np.zeros(0, dtype=np.float32)
    if sample_rate != _SR_STD or x.size != _N_STD:
        x = np.interp(
            np.linspace(0.0, 1.0, _N_STD, endpoint=False),
            np.linspace(0.0, 1.0, x.size, endpoint=False),
            x,
        ).astype(np.float32)
    return x - x.mean()


def _mag_from_16k(x_zm: np.ndarray) -> np.ndarray:
    return (
        np.abs(np.fft.rfft(x_zm * _HANN_1024, n=_NFFT_16K)).astype(np.float32)
        / float(_N_STD)
    )


def _bark_profile(mag_16k: np.ndarray) -> np.ndarray:
    pe = mag_16k * _PE_WEIGHT
    return np.array(
        [float(pe[idx].mean()) if idx.size else 0.0 for idx in _BARK_BINS[:_VOICE_BARK]],
        dtype=np.float32,
    )


def band_energies(pcm: np.ndarray, sample_rate: int) -> np.ndarray:
    """Pre-emphasized Bark sub-band magnitude profile across 110–6500 Hz."""
    x = np.asarray(pcm, dtype=np.float32).reshape(-1)
    if x.size < 64 or sample_rate <= 0:
        return np.zeros(len(_BARK_EDGES) - 1, dtype=np.float32)
    x_zm = _to_16k_frame(x, sample_rate)
    pe = _mag_from_16k(x_zm) * _PE_WEIGHT
    return np.array(
        [float(pe[idx].mean()) if idx.size else 0.0 for idx in _BARK_BINS],
        dtype=np.float32,
    )


def speech_band_level(pcm: np.ndarray, sample_rate: int = 16000) -> float:
    """Normalized 0..1 RMS level strictly inside the 200–3500 Hz speech band.

    Rejects sub-190 Hz mic wind puffs / desk thumps and >3.8 kHz breath hiss,
    while remaining sensitive to quiet conversational speech (~115+ int16 RMS).
    """
    x = np.asarray(pcm, dtype=np.float32).reshape(-1)
    if x.size < 64 or sample_rate <= 0:
        return 0.0
    x = x - x.mean()
    n = 1 << (int(x.size) - 1).bit_length()
    spec = np.fft.rfft(x, n=n)
    freqs = np.fft.rfftfreq(n, 1.0 / sample_rate)
    mask = (freqs >= 200.0) & (freqs <= 3500.0)
    if not np.any(mask):
        return 0.0
    band_pwr = float(np.sum(spec[mask].real ** 2 + spec[mask].imag ** 2))
    rms = float(np.sqrt(2.0 * band_pwr / (x.size * n)))
    if rms <= _PCM_FLOOR:
        return 0.0
    return min(1.0, (rms - _PCM_FLOOR) / (_PCM_FULL - _PCM_FLOOR))


def _subtract_echo_notches_safe(
    mic_mag: np.ndarray, ref_mag: np.ndarray, gain_vec: np.ndarray
) -> np.ndarray:
    """Subtract predicted speaker echo while flooring over-subtracted harmonic
    bins to the 25th-percentile local inter-harmonic floor (prevents artificial
    periodic comb notches in smooth breath/sigh noise).
    """
    ref_wide = np.maximum(
        ref_mag, 0.50 * np.maximum(np.roll(ref_mag, 1), np.roll(ref_mag, -1))
    )
    echo_est = gain_vec * ref_wide
    env_low = np.percentile(
        np.lib.stride_tricks.sliding_window_view(np.pad(mic_mag, 8, mode="edge"), 17),
        25,
        axis=-1,
    ).astype(np.float32)
    sub = np.maximum(mic_mag - echo_est, env_low)
    return np.where(echo_est > 0.25 * mic_mag, sub, mic_mag)


def _voice_conf_from_spectrum(
    mag_16k: np.ndarray,
    raw_zm: np.ndarray | None = None,
    y_hat_16k: np.ndarray | None = None,
    res_gain: float = 0.0,
    echo_subtracted: bool = False,
) -> float:
    """Core voiced-speech confidence scorer (returns 0.0 or 1.05..1.17)."""
    # 1. Transient / keyboard-click / mic-tap rejection
    if raw_zm is not None and raw_zm.size >= 512:
        q = raw_zm.size // 4
        es = [
            float(np.dot(raw_zm[k * q : (k + 1) * q], raw_zm[k * q : (k + 1) * q]))
            for k in range(4)
        ]
        if max(es) > 0.86 * (sum(es) + 1e-9) and min(es) < 0.02 * max(es):
            return 0.0

    mag = mag_16k
    if y_hat_16k is not None and res_gain > 0.0 and y_hat_16k.size == _N_STD:
        if float(np.dot(y_hat_16k, y_hat_16k)) > _N_STD * (14.0 ** 2):
            yh = y_hat_16k - y_hat_16k.mean()
            y_mag = _mag_from_16k(yh)
            mag = _subtract_echo_notches_safe(
                mag, y_mag, np.full_like(_FREQS_16K, float(res_gain))
            )
            echo_subtracted = True

    # 2. Minimum voiced speech energy (120–3500 Hz >= 40 int16 RMS)
    pwr_raw = mag * mag
    if float(np.sqrt(np.sum(pwr_raw[_SPEECH_MASK_120]) * 2.0 / 0.375)) < 40.0:
        return 0.0

    # 3. Raw high-frequency hiss check (immune to pre-emphasis boosting quiet ADC noise)
    p_raw_tot = float(pwr_raw[_FREQS_16K >= 50.0].sum()) + 1e-12
    if float(pwr_raw[_FREQS_16K > 3800.0].sum()) / p_raw_tot > 0.55:
        return 0.0

    # 4. Pre-emphasized formant balance (handles deep male -12 dB/oct glottal tilt
    #    while rejecting 50/60 Hz mains hum and sub-bass wind rumble)
    pwr_pe = (mag * _PE_WEIGHT) ** 2
    p_pe_tot = float(pwr_pe[(_FREQS_16K >= 50.0) & (_FREQS_16K <= 4000.0)].sum()) + 1e-12
    if (
        float(pwr_pe[(_FREQS_16K >= 240.0) & (_FREQS_16K <= 3600.0)].sum()) / p_pe_tot < 0.24
        or float(pwr_pe[(_FREQS_16K >= 420.0) & (_FREQS_16K <= 3400.0)].sum()) / p_pe_tot < 0.09
        or float(pwr_pe[(_FREQS_16K >= 50.0) & (_FREQS_16K < 200.0)].sum()) / p_pe_tot > 0.70
    ):
        return 0.0

    # 5. Local harmonic-comb prominence across 160–2000 Hz (rejects unvoiced
    #    formant-shaped sighs & turbulent breaths whose spectrum lacks harmonics)
    sb = pwr_pe[(_FREQS_16K >= 160.0) & (_FREQS_16K <= 2000.0)]
    sb_sm = np.convolve(
        np.pad(sb, 1, mode="edge"),
        np.array([0.25, 0.5, 0.25], dtype=np.float32),
        mode="valid",
    )
    log_sb = np.log(sb_sm + 1e-12)
    env = np.convolve(
        np.pad(log_sb, 12, mode="edge"),
        np.ones(25, dtype=np.float32) / 25.0,
        mode="valid",
    )
    if float(np.std(log_sb - env)) < 1.13:
        if not echo_subtracted:
            return 0.0
        env_lin = (
            np.convolve(
                np.pad(sb_sm, 12, mode="edge"),
                np.ones(25, dtype=np.float32) / 25.0,
                mode="valid",
            )
            + 1e-12
        )
        if float(np.percentile(sb_sm / env_lin, 90)) < 2.45:
            return 0.0

    # 6. Wiener-Khinchin vocal-fold pitch autocorrelation (75–400 Hz) at T0 and 2*T0
    ac = np.fft.irfft((mag * _BP_AC_MASK) ** 2, n=_NFFT_16K)
    if ac[0] <= 1e-12:
        return 0.0
    lag_lo, lag_hi = int(_SR_STD / 400.0), int(_SR_STD / 75.0)
    reg = ac[lag_lo - 1 : lag_hi + 2]
    pks = (reg[1:-1] > reg[:-2]) & (reg[1:-1] >= reg[2:])
    if not np.any(pks):
        return 0.0
    vals = reg[1:-1]
    idx = int(np.argmax(np.where(pks, vals, -1e30)))
    lag = lag_lo + idx
    taper = max(0.55, 1.0 - 0.65 * (lag / float(_N_STD)))
    r_peak = float(vals[idx] / (ac[0] * taper + 1e-12))
    if 2 * lag < _N_STD - 64:
        taper2 = max(0.35, 1.0 - 0.75 * (2.0 * lag / float(_N_STD)))
        r_2nd = float(
            np.max(ac[2 * lag - 3 : 2 * lag + 4]) / (ac[0] * taper2 + 1e-12)
        )
    else:
        r_2nd = r_peak

    if r_peak < 0.43 or r_2nd < 0.27:
        return 0.0
    return round(1.05 + 0.12 * min(1.0, (r_peak - 0.43) / 0.30), 3)


def voice_confidence(pcm: np.ndarray, sample_rate: int = 16000) -> float:
    """Return 0.0 for non-speech/breath/noise, or 1.05..1.17 for voiced speech."""
    x = np.asarray(pcm, dtype=np.float32).reshape(-1)
    if x.size < 256 or sample_rate <= 0:
        return 0.0
    x_zm = _to_16k_frame(x, sample_rate)
    return _voice_conf_from_spectrum(_mag_from_16k(x_zm), raw_zm=x_zm)


def is_voiced_speech(pcm: np.ndarray, sample_rate: int = 16000) -> bool:
    """True when `pcm` contains periodic human vocal-fold speech."""
    return voice_confidence(pcm, sample_rate) >= 1.0


class EchoGuard:
    """Thread-safe two-stage acoustic echo canceller & barge-in speech detector."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # Stage 1: Streaming 16 kHz speaker waveform ring + 1024-tap Overlap-Save FDAF
        self._spk_buf = np.zeros(_MAX_DELAY_SAMPLES + 2 * _FDAF_TAPS, dtype=np.float32)
        self._spk_samples_pushed = 0
        self._W = np.zeros(_FDAF_TAPS + 1, dtype=np.complex128)
        self._P = np.zeros(_FDAF_TAPS + 1, dtype=np.float64)
        self._ref_abs_end: int | None = None
        self._delay_conf = 0
        self._unlock_streak = 0
        self._erle = 1.0
        self._res_phase = 0.0
        self._res_prev = 0.0

        # Stage 2: Fine-bin & Bark spectral reference history (handles frame #0 before
        # waveform lock, nonlinear speaker distortion, and uncorrelated test signals)
        self._hist: list[tuple[float, np.ndarray, np.ndarray, float]] = []
        self._gain_bark = np.full(_VOICE_BARK, 0.04, dtype=np.float32)
        self._seen = 0
        self._last_sim = 0.0

    # ── speaker side ──────────────────────────────────────────────────────────

    def _push_speaker_16k_unlocked(self, pcm: np.ndarray, sample_rate: int) -> np.ndarray:
        x = np.asarray(pcm, dtype=np.float32).reshape(-1)
        if x.size == 0 or sample_rate <= 0:
            return np.zeros(0, dtype=np.float32)
        if sample_rate == _SR_STD:
            spk_16k = x
        else:
            step = float(sample_rate) / float(_SR_STD)
            ext = np.concatenate([[self._res_prev], x])
            n_est = int((x.size - self._res_phase + 0.999999) // step) + 2
            positions = 1.0 + self._res_phase + np.arange(max(0, n_est)) * step
            positions = positions[positions < ext.size]
            if positions.size == 0:
                self._res_phase -= x.size
                self._res_prev = float(x[-1])
                return np.zeros(0, dtype=np.float32)
            idx0 = positions.astype(np.int64)
            frac = (positions - idx0).astype(np.float32)
            idx1 = np.minimum(idx0 + 1, ext.size - 1)
            spk_16k = ext[idx0] * (1.0 - frac) + ext[idx1] * frac
            self._res_phase = float((positions[-1] + step) - ext.size)
            self._res_prev = float(x[-1])

        n = spk_16k.size
        if n >= self._spk_buf.size:
            self._spk_buf[:] = spk_16k[-self._spk_buf.size :]
        else:
            self._spk_buf[:-n] = self._spk_buf[n:]
            self._spk_buf[-n:] = spk_16k
        self._spk_samples_pushed += n
        return spk_16k

    def note_output(
        self,
        pcm: np.ndarray,
        sample_rate: int,
        level: float,
        when: float | None = None,
    ) -> None:
        """Record a speaker output chunk for both waveform FDAF and spectral suppression."""
        if when is None:
            when = time.monotonic()
        arr = np.asarray(pcm)
        if arr.size == 0 or sample_rate <= 0:
            return

        with self._lock:
            spk_16k = self._push_speaker_16k_unlocked(arr, sample_rate)
            # Slice into 50%-overlapping 64 ms spectral frames for Stage 2
            step = _N_STD // 2
            if spk_16k.size >= _N_STD:
                dt = step / float(_SR_STD)
                for idx, start in enumerate(range(0, spk_16k.size - _N_STD + 1, step)):
                    seg = spk_16k[start : start + _N_STD]
                    sb = speech_band_level(seg, _SR_STD)
                    mag = _mag_from_16k(seg - seg.mean())
                    self._hist.append(
                        (when + idx * dt, mag, _bark_profile(mag), sb if sb > 0 else float(level))
                    )
            elif spk_16k.size >= 64:
                seg = _to_16k_frame(spk_16k, _SR_STD)
                sb = speech_band_level(spk_16k, _SR_STD)
                mag = _mag_from_16k(seg)
                self._hist.append(
                    (when, mag, _bark_profile(mag), sb if sb > 0 else float(level))
                )
            cutoff = when - _WINDOW_S
            if len(self._hist) > 64 or (self._hist and self._hist[0][0] < cutoff):
                self._hist = [h for h in self._hist if h[0] >= cutoff][-64:]

    def reset(self) -> None:
        """Clear active playback reference at turn end while keeping learned room model."""
        with self._lock:
            self._hist.clear()
            self._spk_buf.fill(0.0)
            self._spk_samples_pushed = 0
            self._ref_abs_end = None
            self._unlock_streak = 0
            self._res_phase = 0.0
            self._res_prev = 0.0
            self._last_sim = 0.0

    # ── Stage 1: Time-domain Overlap-Save FDAF ────────────────────────────────

    def _find_coarse_abs_end_unlocked(self, mic_16k: np.ndarray) -> int | None:
        if self._spk_samples_pushed < _N_STD:
            return None
        m = mic_16k - mic_16k.mean()
        m_e = float(np.dot(m, m))
        if m_e < _N_STD * (45.0 ** 2):
            return None
        nfft_cc = 1 << int(self._spk_buf.size + m.size).bit_length()
        cc = np.fft.irfft(
            np.fft.rfft(self._spk_buf, n=nfft_cc) * np.conj(np.fft.rfft(m, n=nfft_cc)),
            n=nfft_cc,
        )
        lo = _FDAF_TAPS
        hi = self._spk_buf.size - m.size
        seg = cc[lo : hi + 1]
        cs = np.concatenate([[0.0], np.cumsum(self._spk_buf.astype(np.float64) ** 2)])
        win_e = cs[lo + m.size : hi + m.size + 1] - cs[lo : hi + 1]
        valid = win_e > _N_STD * (110.0 ** 2)
        if not np.any(valid):
            return None
        ncc = np.where(valid, np.abs(seg) / np.sqrt(win_e * m_e + 1e-9), 0.0)
        pk_idx = int(np.argmax(ncc))
        if float(ncc[pk_idx]) >= 0.34:
            pos = lo + pk_idx
            end = min(self._spk_buf.size, pos + _FDAF_TAPS + 64)
            tail_offset = self._spk_buf.size - end
            return self._spk_samples_pushed - tail_offset
        return None

    def _fdaf_step_unlocked(
        self, mic_16k: np.ndarray, mic_advance: int = _N_STD
    ) -> tuple[np.ndarray, np.ndarray | None, float]:
        """Run Stage 1 linear waveform AEC locked in absolute sample coordinates
        (immune to asynchronous speaker write batch sizes vs 64 ms mic callbacks)."""
        if self._spk_samples_pushed < _N_STD:
            return mic_16k, None, 0.0

        d = mic_16k.astype(np.float64)
        if self._ref_abs_end is not None:
            self._ref_abs_end += mic_advance
            end_chk = self._spk_buf.size - (self._spk_samples_pushed - self._ref_abs_end)
            if end_chk - 2 * _FDAF_TAPS < 0 or end_chk > self._spk_buf.size:
                # Speaker underrun or buffer wrap after pause -> re-lock cleanly
                self._ref_abs_end = None

        if self._ref_abs_end is None:
            cand_abs = self._find_coarse_abs_end_unlocked(mic_16k)
            if cand_abs is None:
                return mic_16k, None, 0.0
            end = self._spk_buf.size - (self._spk_samples_pushed - cand_abs)
            ref0 = self._spk_buf[end - _N_STD - 64 : end - 64].astype(np.float64)
            if ref0.size != _N_STD:
                return mic_16k, None, 0.0
            alpha0 = max(0.0, float(np.dot(d, ref0)) / (float(np.dot(ref0, ref0)) + 1e-9))
            y0 = alpha0 * ref0
            e0 = d - y0
            self._ref_abs_end = cand_abs
            if self._delay_conf == 0:
                h0 = np.zeros(2 * _FDAF_TAPS, dtype=np.float64)
                h0[64] = alpha0
                self._W = np.fft.rfft(h0)
                self._delay_conf = 1
            return e0.astype(np.float32), y0.astype(np.float32), 0.85

        end = self._spk_buf.size - (self._spk_samples_pushed - self._ref_abs_end)
        start = end - 2 * _FDAF_TAPS
        if start < 0 or end > self._spk_buf.size:
            return mic_16k, None, 0.0
        x_blk = self._spk_buf[start:end].astype(np.float64)
        x_pwr = float(np.dot(x_blk[_FDAF_TAPS:], x_blk[_FDAF_TAPS:])) + 1e-9
        if x_pwr < _N_STD * (25.0 ** 2):
            return mic_16k, None, 0.0

        X = np.fft.rfft(x_blk)
        y_hat = np.fft.irfft(self._W * X, n=2 * _FDAF_TAPS)[_FDAF_TAPS:]
        e = d - y_hat

        d_pwr = float(np.dot(d, d)) + 1e-9
        e_pwr = float(np.dot(e, e)) + 1e-9
        y_pwr = float(np.dot(y_hat, y_hat)) + 1e-9

        X2 = X.real ** 2 + X.imag ** 2
        self._P = (0.82 * self._P + 0.18 * X2) if self._delay_conf > 1 else X2
        denom = 0.85 * self._P + 0.15 * float(np.mean(self._P)) + 1e6

        # Freeze filter weights during periodic double-talk so user speech is never learned as echo
        e_f32 = e.astype(np.float32)
        if (
            self._delay_conf > 6
            and e_pwr > 2.2 * y_pwr
            and _voice_conf_from_spectrum(_mag_from_16k(e_f32 - e_f32.mean()), raw_zm=e_f32 - e_f32.mean()) > 0.0
        ):
            mu = 0.0
        elif self._delay_conf < 25:
            mu = 0.55 if e_pwr <= 1.2 * d_pwr else 0.22
        else:
            mu = 0.28 if e_pwr <= 0.6 * d_pwr else 0.10

        corr_dy = float(np.dot(d, y_hat))
        if corr_dy <= 0.12 * y_pwr and e_pwr >= d_pwr:
            self._unlock_streak += 1
            unlock_limit = 1 if self._delay_conf < 3 else 8
            if self._unlock_streak >= unlock_limit:
                self._ref_abs_end = None
                self._delay_conf = 0
                self._unlock_streak = 0
                return mic_16k, None, 0.0
            if self._delay_conf < 3:
                return mic_16k, None, 0.0
        else:
            self._unlock_streak = 0

        if mu > 0.0 and (self._delay_conf >= 3 or corr_dy > 0.12 * y_pwr):
            E_fft = np.fft.rfft(np.concatenate([np.zeros(_FDAF_TAPS), e]))
            grad = np.fft.irfft((mu * np.conj(X) * E_fft) / denom, n=2 * _FDAF_TAPS)
            grad[_FDAF_TAPS:] = 0.0
            self._W += np.fft.rfft(grad)
            self._delay_conf += 1

        if e_pwr < 0.85 * d_pwr:
            self._erle = 0.85 * self._erle + 0.15 * (d_pwr / max(e_pwr, 1e-6))
            self._last_sim = float(min(1.0, 1.0 - np.sqrt(e_pwr / d_pwr)))

        res_gain = (
            1.45
            if (self._erle < 5.0 or self._delay_conf < 20)
            else (0.65 if self._erle < 9.0 else 0.42)
        )
        return e_f32, y_hat.astype(np.float32), res_gain

    # ── Microphone classification ─────────────────────────────────────────────

    def speech_score(
        self,
        pcm: np.ndarray,
        sample_rate: int,
        level: float | None = None,
        when: float | None = None,
    ) -> float:
        """Return 0.0 for silence/breath/echo, or 1.05..1.17 for genuine user speech."""
        if when is None:
            when = time.monotonic()
        x = np.asarray(pcm, dtype=np.float32).reshape(-1)
        if x.size < 256 or sample_rate <= 0:
            return 0.0

        sb_lvl = speech_band_level(x, sample_rate) if level is None else float(level)
        x_16k = _to_16k_frame(x, sample_rate)

        with self._lock:
            # Advance FDAF reference pointer on every mic frame even when quiet so
            # absolute speaker-vs-mic sample alignment stays locked across pauses!
            if self._ref_abs_end is not None:
                self._ref_abs_end += _N_STD
                end_chk = self._spk_buf.size - (self._spk_samples_pushed - self._ref_abs_end)
                if end_chk - 2 * _FDAF_TAPS < 0 or end_chk > self._spk_buf.size:
                    self._ref_abs_end = None

            # Quiet mic while speaker is playing -> rapid headphone / low-coupling detection
            if sb_lvl < 0.024:
                if self._hist and max(h[3] for h in self._hist) > 0.12:
                    self._gain_bark = np.maximum(0.005, self._gain_bark * 0.55)
                    self._seen = min(self._seen + 1, 999)
                self._last_sim = 0.0
                return 0.0

            if not self._hist:
                self._last_sim = 0.0
                return _voice_conf_from_spectrum(_mag_from_16k(x_16k), raw_zm=x_16k)

            # Stage 1: Linear time-domain FDAF + Stage 2 nonlinear residual suppression
            # (pointer was already advanced above by _N_STD for this mic block)
            e_16k, y_hat_16k, res_gain = self._fdaf_step_unlocked(x_16k, mic_advance=0)
            if y_hat_16k is not None:
                e_zm = e_16k - e_16k.mean()
                return _voice_conf_from_spectrum(
                    _mag_from_16k(e_zm),
                    raw_zm=e_zm,
                    y_hat_16k=y_hat_16k,
                    res_gain=res_gain,
                    echo_subtracted=True,
                )

            # Stage 2 standalone fallback (before waveform lock or phase-uncoupled echo):
            # Orthogonal fine-harmonic cosine match across 120–3400 Hz
            mic_mag = _mag_from_16k(x_16k)
            m_fine = (mic_mag * _PE_WEIGHT)[_FINE_MASK]
            m_norm = float(np.linalg.norm(m_fine)) + 1e-12
            best_cos = -1.0
            best_mag: np.ndarray | None = None
            best_bark: np.ndarray | None = None
            best_alpha = 0.0

            for ts, ref_mag, ref_bark, _ in self._hist:
                if ts > when + 0.02 or when - ts > _WINDOW_S:
                    continue
                r_fine = (ref_mag * _PE_WEIGHT)[_FINE_MASK]
                r_norm2 = float(np.dot(r_fine, r_fine))
                if r_norm2 < 1e-12:
                    continue
                dot_mr = float(np.dot(m_fine, r_fine))
                cos_sim = dot_mr / (m_norm * float(np.sqrt(r_norm2)) + 1e-12)
                if cos_sim > best_cos:
                    best_cos = cos_sim
                    best_mag = ref_mag
                    best_bark = ref_bark
                    best_alpha = max(0.0, dot_mr / r_norm2)

            if best_mag is None or best_bark is None:
                self._last_sim = 0.0
                return _voice_conf_from_spectrum(mic_mag, raw_zm=x_16k)

            self._last_sim = float(max(0.0, best_cos))
            mic_bark = _bark_profile(mic_mag)
            exp_bark_sum = float(np.sum(self._gain_bark * best_bark))
            tot_b = float(mic_bark.sum()) + 1e-12

            # High fine-harmonic match at expected coupling = pure speaker echo
            if best_cos >= 0.90 and (self._seen < 2 or tot_b <= exp_bark_sum * 1.25 + 4.0):
                obs_gain = np.minimum(1.5, mic_bark / np.maximum(best_bark, 0.2))
                rate = 0.65 if self._seen < 4 else 0.20
                mask_active = best_bark > 0.10 * float(np.max(best_bark))
                self._gain_bark = np.where(
                    mask_active,
                    self._gain_bark + (obs_gain - self._gain_bark) * rate,
                    self._gain_bark,
                )
                self._seen = min(self._seen + 1, 999)
                return 0.0

            # Confirmed headphone / near-zero coupling fast path
            if self._seen >= 2 and float(np.max(self._gain_bark)) < 0.025:
                return _voice_conf_from_spectrum(mic_mag, raw_zm=x_16k)

            # Frame #0 low-correlation fast path (different voice on headphones!)
            if self._seen < 2 and best_cos < 0.45:
                return _voice_conf_from_spectrum(mic_mag, raw_zm=x_16k)

            if self._seen >= 2:
                gain_curve = np.interp(
                    _FREQS_16K, _BARK_CENTERS, self._gain_bark * 1.35
                ).astype(np.float32)
                alpha_cap = min(best_alpha, float(np.max(self._gain_bark)) * 1.55)
                gain_vec = np.maximum(gain_curve, alpha_cap) * 1.55
            else:
                alpha_use = best_alpha if best_cos < 0.85 else min(best_alpha, 0.35)
                gain_vec = np.full_like(_FREQS_16K, alpha_use * 1.55)

            clean_mag = _subtract_echo_notches_safe(mic_mag, best_mag, gain_vec)
            return _voice_conf_from_spectrum(
                clean_mag, raw_zm=x_16k, echo_subtracted=True
            )

    def is_user_speech(
        self,
        pcm: np.ndarray,
        sample_rate: int,
        level: float | None = None,
        when: float | None = None,
    ) -> bool:
        """True when `pcm` contains genuine voiced user speech (not echo or breath)."""
        return self.speech_score(pcm, sample_rate, level=level, when=when) >= 1.0

    # ── Diagnostics / properties ──────────────────────────────────────────────

    @property
    def calibrated(self) -> bool:
        return self._seen >= 2 or self._delay_conf >= 2

    @property
    def required_blocks(self) -> int:
        """2 voiced 64 ms blocks (~128 ms) suffices for crisp single-word commands
        like 'Stop', 'Wait', 'No', 'Hey' while rejecting any single transient."""
        return 2

    @property
    def gain(self) -> float:
        return float(np.median(self._gain_bark))

    @property
    def threshold(self) -> float:
        return 0.10

    @property
    def last_similarity(self) -> float:
        return self._last_sim
