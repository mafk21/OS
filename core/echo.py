"""Acoustic echo cancellation and human-voice barge-in detector.

Separates genuine user speech from:
  1. JARVIS's own voice leaking from loudspeakers back into the microphone
     across arbitrary Windows/OS/Bluetooth output latencies (up to ~2.0 s),
     nonlinear laptop speaker distortion, clock drift, and multi-path room
     reflections, and
  2. Non-speech microphone sounds — close-mic breathing/exhales, aspirated
     sighs, low-frequency wind puffs, keyboard/mouse clicks, and steady fan/AC
     or mains hum — even when loud.

Normal and quiet conversational speech (down to ~115 int16 RMS at desk distance,
deep 85 Hz male voices with natural -6 to -12 dB/oct glottal tilt, female/child
voices, and crisp single-word commands like "Stop", "Wait", "No", "Hey" lasting
~128 ms = 2 blocks) passes cleanly on both headphones and loudspeakers.

Architecture:
  - Stage 1 (Phase-Verified Overlap-Save FDAF): Phase-continuous streaming
    24 kHz -> 16 kHz resampler feeds a 2.0 s speaker ring buffer. Generalized
    FFT cross-correlation locks onto the OS + room acoustic delay, advancing by
    elapsed wall/sample time across silent syllable gaps, and cancels linear
    multi-tap room echo via a 1024-tap Frequency-Domain Adaptive Filter.
  - Stage 2 (Continuous-Hop 2-Pass Fine-Bin Spectral Echo Suppressor):
    Maintains seamless 50%-overlapping 64 ms speaker spectra across `note_output`
    boundaries (never decaying acoustic coupling during OS buffer latency
    silence!). Suppresses aligned nonlinear speaker harmonics when Stage 1 is
    locked, or performs 2-pass fine-harmonic orthogonal cancellation across the
    1.6 s speaker window before waveform lock / under clock drift.
  - Voiced Speech Classifier: Evaluates pre-emphasized formant balance, local
    harmonic-comb prominence, transient concentration, and Wiener-Khinchin pitch
    autocorrelation at T0 and 2*T0 across 75–400 Hz.
"""

from __future__ import annotations

import threading
import time
import numpy as np

# Canonical internal analysis grid: 1024 samples (64 ms) @ 16 kHz, 2x-padded
# to 2048 FFT points (7.8125 Hz/bin).
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

_BP_AC_MASK = ((_FREQS_16K >= 75.0) & (_FREQS_16K <= 1150.0)).astype(np.float32)
_SPEECH_MASK_120 = (_FREQS_16K >= 120.0) & (_FREQS_16K <= 3500.0)
_FINE_MASK = (_FREQS_16K >= 120.0) & (_FREQS_16K <= 3400.0)

_PCM_FLOOR = 28.0
_PCM_FULL = 2350.0

# Echo history & adaptive filter constants (sized for Windows WASAPI / Bluetooth / HDMI)
_WINDOW_S = 1.6
_FDAF_TAPS = 1024           # 64 ms room impulse response span @ 16 kHz
_MAX_DELAY_SAMPLES = 32000  # 2.0 s speaker reference ring @ 16 kHz


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
    """Normalized 0..1 RMS level strictly inside the 200–3500 Hz speech band."""
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
    echo_subtracted: bool = False,
) -> float:
    """Core voiced-speech confidence scorer (returns 0.0 or 1.05..1.17)."""
    if raw_zm is not None and raw_zm.size >= 512:
        q = raw_zm.size // 4
        es = [
            float(np.dot(raw_zm[k * q : (k + 1) * q], raw_zm[k * q : (k + 1) * q]))
            for k in range(4)
        ]
        if max(es) > 0.86 * (sum(es) + 1e-9) and min(es) < 0.02 * max(es):
            return 0.0

    pwr_raw = mag_16k * mag_16k
    if float(np.sqrt(np.sum(pwr_raw[_SPEECH_MASK_120]) * 2.0 / 0.375)) < 40.0:
        return 0.0

    p_raw_tot = float(pwr_raw[_FREQS_16K >= 50.0].sum()) + 1e-12
    if float(pwr_raw[_FREQS_16K > 3800.0].sum()) / p_raw_tot > 0.55:
        return 0.0

    pwr_pe = (mag_16k * _PE_WEIGHT) ** 2
    p_pe_tot = float(pwr_pe[(_FREQS_16K >= 50.0) & (_FREQS_16K <= 4000.0)].sum()) + 1e-12
    if (
        float(pwr_pe[(_FREQS_16K >= 240.0) & (_FREQS_16K <= 3600.0)].sum()) / p_pe_tot < 0.24
        or float(pwr_pe[(_FREQS_16K >= 420.0) & (_FREQS_16K <= 3400.0)].sum()) / p_pe_tot < 0.09
        or float(pwr_pe[(_FREQS_16K >= 50.0) & (_FREQS_16K < 200.0)].sum()) / p_pe_tot > 0.70
    ):
        return 0.0

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

    ac = np.fft.irfft((mag_16k * _BP_AC_MASK) ** 2, n=_NFFT_16K)
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
        # Stage 1: 2.0 s 16 kHz speaker waveform ring + 1024-tap Overlap-Save FDAF
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
        self._last_mic_ts: float | None = None

        # Stage 2: Seamless 50%-overlapping 16 kHz spectral history across chunk boundaries
        # IMPORTANT: Acoustic coupling (`_gain_bark`) is NEVER decayed during quiet mic
        # blocks, because during the first 150-500 ms of playback the audio is still
        # inside the OS output buffer and has not physically exited the speakers yet!
        self._hist_tail = np.zeros(0, dtype=np.float32)
        self._hist: list[tuple[float, np.ndarray, np.ndarray, float]] = []
        self._gain_bark = np.full(_VOICE_BARK, 0.22, dtype=np.float32)
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
        """Record a speaker output chunk seamlessly across arbitrary batch sizes."""
        if when is None:
            when = time.monotonic()
        arr = np.asarray(pcm)
        if arr.size == 0 or sample_rate <= 0:
            return

        with self._lock:
            spk_16k = self._push_speaker_16k_unlocked(arr, sample_rate)
            if spk_16k.size == 0:
                return
            self._hist_tail = np.concatenate([self._hist_tail, spk_16k])
            hop = _N_STD // 2
            dt = hop / float(_SR_STD)
            idx = 0
            pushed_any = False
            while self._hist_tail.size >= _N_STD:
                seg = self._hist_tail[:_N_STD]
                self._hist_tail = self._hist_tail[hop:]
                sb = speech_band_level(seg, _SR_STD)
                if sb >= 0.015:
                    mag = _mag_from_16k(seg - seg.mean())
                    self._hist.append((when + idx * dt, mag, _bark_profile(mag), sb))
                    pushed_any = True
                idx += 1

            # Ensure very first short chunk (<64 ms) is still represented immediately
            if not pushed_any and not self._hist and self._hist_tail.size >= 64:
                seg = _to_16k_frame(self._hist_tail, _SR_STD)
                sb = speech_band_level(seg, _SR_STD)
                if sb >= 0.015 or level >= 0.02:
                    mag = _mag_from_16k(seg)
                    self._hist.append((when, mag, _bark_profile(mag), max(sb, float(level))))

            cutoff = when - _WINDOW_S
            if len(self._hist) > 96 or (self._hist and self._hist[0][0] < cutoff):
                self._hist = [h for h in self._hist if h[0] >= cutoff][-96:]

    def reset(self) -> None:
        """Clear active playback reference at turn end while keeping learned room model."""
        with self._lock:
            self._hist.clear()
            self._hist_tail = np.zeros(0, dtype=np.float32)
            self._spk_buf.fill(0.0)
            self._spk_samples_pushed = 0
            self._ref_abs_end = None
            self._unlock_streak = 0
            self._last_mic_ts = None
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
        valid = win_e > _N_STD * (100.0 ** 2)
        if not np.any(valid):
            return None
        ncc = np.where(valid, np.abs(seg) / np.sqrt(win_e * m_e + 1e-9), 0.0)
        pk_idx = int(np.argmax(ncc))
        if float(ncc[pk_idx]) >= 0.32:
            pos = lo + pk_idx
            end = min(self._spk_buf.size, pos + _FDAF_TAPS + 64)
            return self._spk_samples_pushed - (self._spk_buf.size - end)
        return None

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
            # Advance speaker alignment pointer by elapsed time so silent syllable
            # gaps (even when callers skip quiet frames) never slip FDAF phase!
            if self._last_mic_ts is not None and when > self._last_mic_ts:
                adv = max(_N_STD, int(round((when - self._last_mic_ts) * _SR_STD)))
                if adv > _SR_STD * 2:
                    self._ref_abs_end = None
                elif self._ref_abs_end is not None:
                    self._ref_abs_end += adv
            elif self._ref_abs_end is not None:
                self._ref_abs_end += _N_STD
            self._last_mic_ts = when

            if self._ref_abs_end is not None:
                end_chk = self._spk_buf.size - (self._spk_samples_pushed - self._ref_abs_end)
                if end_chk - 2 * _FDAF_TAPS < 0 or end_chk > self._spk_buf.size:
                    self._ref_abs_end = None

            if sb_lvl < 0.024:
                self._last_sim = 0.0
                return 0.0

            if not self._hist and self._spk_samples_pushed < _N_STD:
                self._last_sim = 0.0
                return _voice_conf_from_spectrum(_mag_from_16k(x_16k), raw_zm=x_16k)

            # ── Stage 1: Phase-Verified Linear Overlap-Save FDAF ─────────────
            sig_16k = x_16k
            y_hat_valid: np.ndarray | None = None
            x_aligned: np.ndarray | None = None
            res_gain = 0.0

            if self._spk_samples_pushed >= _N_STD:
                d = x_16k.astype(np.float64)
                if self._ref_abs_end is None:
                    cand = self._find_coarse_abs_end_unlocked(x_16k)
                    if cand is not None:
                        end = self._spk_buf.size - (self._spk_samples_pushed - cand)
                        ref0 = self._spk_buf[end - _N_STD - 64 : end - 64].astype(np.float64)
                        if ref0.size == _N_STD:
                            a0 = max(
                                0.0, float(np.dot(d, ref0)) / (float(np.dot(ref0, ref0)) + 1e-9)
                            )
                            y0 = a0 * ref0
                            e0 = d - y0
                            if float(np.dot(e0, e0)) < 0.92 * float(np.dot(d, d)):
                                self._ref_abs_end = cand
                                if self._delay_conf == 0:
                                    h0 = np.zeros(2 * _FDAF_TAPS, dtype=np.float64)
                                    h0[64] = a0
                                    self._W = np.fft.rfft(h0)
                                    self._delay_conf = 1
                                sig_16k = (e0 - e0.mean()).astype(np.float32)
                                y_hat_valid = y0.astype(np.float32)
                                x_aligned = ref0.astype(np.float32)
                                res_gain = 1.25
                else:
                    end = self._spk_buf.size - (self._spk_samples_pushed - self._ref_abs_end)
                    start = end - 2 * _FDAF_TAPS
                    if 0 <= start and end <= self._spk_buf.size:
                        x_blk = self._spk_buf[start:end].astype(np.float64)
                        x_pwr = float(np.dot(x_blk[_FDAF_TAPS:], x_blk[_FDAF_TAPS:])) + 1e-9
                        if x_pwr >= _N_STD * (25.0 ** 2):
                            X = np.fft.rfft(x_blk)
                            y_hat = np.fft.irfft(self._W * X, n=2 * _FDAF_TAPS)[_FDAF_TAPS:]
                            e = d - y_hat
                            d_pwr = float(np.dot(d, d)) + 1e-9
                            e_pwr = float(np.dot(e, e)) + 1e-9
                            y_pwr = float(np.dot(y_hat, y_hat)) + 1e-9
                            corr_dy = float(np.dot(d, y_hat))

                            if corr_dy > 0.22 * y_pwr:
                                self._unlock_streak = 0
                                X2 = X.real ** 2 + X.imag ** 2
                                self._P = (
                                    (0.82 * self._P + 0.18 * X2) if self._delay_conf > 1 else X2
                                )
                                denom = 0.85 * self._P + 0.15 * float(np.mean(self._P)) + 1e6
                                e_f32 = e.astype(np.float32)
                                e_zm = e_f32 - e_f32.mean()
                                if (
                                    self._delay_conf > 8
                                    and e_pwr > 2.2 * y_pwr
                                    and _voice_conf_from_spectrum(_mag_from_16k(e_zm), raw_zm=e_zm)
                                    > 0.0
                                ):
                                    mu = 0.0
                                elif self._delay_conf < 25:
                                    mu = 0.55 if e_pwr <= 1.2 * d_pwr else 0.22
                                else:
                                    mu = 0.28 if e_pwr <= 0.6 * d_pwr else 0.10

                                if mu > 0.0:
                                    E_fft = np.fft.rfft(
                                        np.concatenate([np.zeros(_FDAF_TAPS), e])
                                    )
                                    grad = np.fft.irfft(
                                        (mu * np.conj(X) * E_fft) / denom, n=2 * _FDAF_TAPS
                                    )
                                    grad[_FDAF_TAPS:] = 0.0
                                    self._W += np.fft.rfft(grad)
                                    self._delay_conf += 1

                                if e_pwr < 0.85 * d_pwr:
                                    self._erle = 0.85 * self._erle + 0.15 * (
                                        d_pwr / max(e_pwr, 1e-6)
                                    )
                                    self._last_sim = float(min(1.0, 1.0 - np.sqrt(e_pwr / d_pwr)))

                                sig_16k = e_zm
                                y_hat_valid = y_hat.astype(np.float32)
                                x_aligned = x_blk[_FDAF_TAPS:].astype(np.float32)
                                nl_scale = float(np.sqrt(y_pwr / x_pwr))
                                res_gain = (
                                    1.35
                                    if (self._erle < 5.0 or self._delay_conf < 18)
                                    else (0.65 if self._erle < 9.0 else 0.40)
                                )
                            elif self._delay_conf >= 8 and self._unlock_streak < 5:
                                # Brief breath/double-talk dip: fall through to Stage 2
                                # for this frame without wiping the converged room filter!
                                self._unlock_streak += 1
                            else:
                                self._unlock_streak = 0
                                cand = self._find_coarse_abs_end_unlocked(x_16k)
                                if cand is not None and self._delay_conf >= 4:
                                    self._ref_abs_end = cand
                                    self._delay_conf = 0
                                else:
                                    self._ref_abs_end = None
                                    self._delay_conf = 0

            # When Stage 1 IS phase-locked, suppress residual reflections + aligned
            # nonlinear laptop-speaker harmonics (capped to actual echo coupling!):
            if y_hat_valid is not None:
                cur_mag = _mag_from_16k(sig_16k)
                y_mag = _mag_from_16k(y_hat_valid - y_hat_valid.mean())
                cur_mag = _subtract_echo_notches_safe(
                    cur_mag, y_mag, np.full_like(_FREQS_16K, float(res_gain))
                )
                if x_aligned is not None:
                    xa_mag = _mag_from_16k(x_aligned - x_aligned.mean())
                    c_f = (cur_mag * _PE_WEIGHT)[_FINE_MASK]
                    x_f = (xa_mag * _PE_WEIGHT)[_FINE_MASK]
                    xn2 = float(np.dot(x_f, x_f)) + 1e-12
                    cos_cx = float(np.dot(c_f, x_f)) / (
                        (float(np.linalg.norm(c_f)) + 1e-12) * float(np.sqrt(xn2))
                    )
                    if cos_cx >= 0.58:
                        a_raw = max(0.0, float(np.dot(c_f, x_f)) / xn2)
                        a_nl = min(a_raw * 1.35, float(locals().get("nl_scale", 0.3)) * 0.45)
                        cur_mag = _subtract_echo_notches_safe(
                            cur_mag, xa_mag, np.full_like(_FREQS_16K, a_nl)
                        )
                return _voice_conf_from_spectrum(
                    cur_mag, raw_zm=sig_16k, echo_subtracted=True
                )

            # ── Stage 2: 2-Pass Fine-Harmonic Spectral Echo Suppressor ────────
            # Handles frame #0 before FDAF lock, Bluetooth/USB crystal clock skew,
            # headphones, and synthetic phase-uncoupled echo signals.
            cur_mag = _mag_from_16k(sig_16k)
            if not self._hist:
                self._last_sim = 0.0
                return _voice_conf_from_spectrum(cur_mag, raw_zm=sig_16k)

            echo_sub = False
            for pass_idx in range(2):
                m_fine = (cur_mag * _PE_WEIGHT)[_FINE_MASK]
                m_norm = float(np.linalg.norm(m_fine)) + 1e-12
                best_cos = -1.0
                best_mag: np.ndarray | None = None
                best_bark: np.ndarray | None = None
                best_alpha = 0.0

                for ts, r_mag, r_bark, _ in self._hist:
                    if ts > when + 0.05 or when - ts > _WINDOW_S:
                        continue
                    r_fine = (r_mag * _PE_WEIGHT)[_FINE_MASK]
                    rn2 = float(np.dot(r_fine, r_fine))
                    if rn2 < 1e-12:
                        continue
                    dot_mr = float(np.dot(m_fine, r_fine))
                    cs = dot_mr / (m_norm * float(np.sqrt(rn2)) + 1e-12)
                    if cs > best_cos:
                        best_cos = cs
                        best_mag = r_mag
                        best_bark = r_bark
                        best_alpha = max(0.0, dot_mr / rn2)

                if best_mag is None or best_bark is None:
                    break

                if pass_idx == 0:
                    self._last_sim = float(max(0.0, best_cos))
                    if best_cos >= 0.72:
                        raw_bark = _bark_profile(cur_mag)
                        obs_g = np.minimum(1.8, raw_bark / np.maximum(best_bark, 0.2))
                        rate = 0.55 if self._seen < 4 else 0.18
                        act = best_bark > 0.10 * float(np.max(best_bark))
                        self._gain_bark = np.where(
                            act,
                            self._gain_bark + (obs_g - self._gain_bark) * rate,
                            self._gain_bark,
                        )
                        self._seen = min(self._seen + 1, 999)

                if best_cos >= (0.52 if pass_idx == 0 else 0.56):
                    cur_mag = _subtract_echo_notches_safe(
                        cur_mag, best_mag, np.full_like(_FREQS_16K, best_alpha * 1.55)
                    )
                    echo_sub = True
                elif pass_idx == 0 and best_cos >= 0.42:
                    cap_a = min(best_alpha, float(np.max(self._gain_bark)) * 1.45)
                    cur_mag = _subtract_echo_notches_safe(
                        cur_mag, best_mag, np.full_like(_FREQS_16K, cap_a * 1.20)
                    )
                    echo_sub = True
                    break
                else:
                    break

            return _voice_conf_from_spectrum(
                cur_mag, raw_zm=sig_16k, echo_subtracted=echo_sub
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
