"""
Telling real human speech apart from speaker echo, breathing, sighs, and noise.

Why a plain loudness check fails
--------------------------------
1. **Breathing & mic wind**: A sigh, nasal exhale, or chair shift near a headset
   or laptop mic routinely reaches -38 to -28 dBFS in wideband RMS — louder than
   a quiet talker sitting back from the desk — yet carries zero vocal-fold pitch
   periodicity and concentrates energy in sub-250 Hz proximity turbulence or
   >3.4 kHz airflow hiss.
2. **Variable room echo**: How loud JARVIS comes back into the mic depends on
   speaker volume, room reverb, and whether headphones are plugged in.

Three independent checks work together here:
1. **`speech_band_level()`** — RMS measured strictly inside the 250–3400 Hz
   vowel-formant band, so sub-250 Hz mic puffs and high-frequency hiss cannot
   masquerade as loud speech.
2. **`is_voiced_speech()`** — Verifies genuine human vocal-fold periodicity
   (80–380 Hz pitch autocorrelation stability across overlapping 28 ms
   sub-windows) plus formant-band energy dominance, rejecting breaths, sighs,
   whispers, keyboard clicks, and mains/fan hum.
3. **`EchoGuard`** — Subtracts the best-matching slice of JARVIS's recent
   playback across speech bands (fitting inside the 200–3800 Hz formant region)
   and tracks an adaptive room echo floor and gain.
"""

from __future__ import annotations

import time

import numpy as np

# Log-spaced edges across the range that carries speech. Coarse on purpose:
# fine bins would track pitch, and pitch is exactly what differs between two
# people saying the same word — we want the *timbre* that echo preserves.
_BAND_EDGES = (200, 400, 700, 1100, 1700, 2600, 3800, 5200, 7000)
_FORMANT_BANDS = 6    # bands 0..5 span 200..3800 Hz (voiced speech formants)

_HISTORY_S = 1.0      # how far back an echo could plausibly have been played
_MIN_LEVEL = 0.08     # speech-band floor (~263 int16 RMS); ignores quiet hiss/breath

_MIN_USER = 0.14      # minimum formant-band residual required to count as a new voice
_HEAD_Q = 95          # near-worst room echo percentile
_HEAD_MULT = 1.12     # headroom above room echo p95

_UNRELIABLE_FLOOR = 0.26
_BLOCKS_NORMAL = 4    # ~256 ms of sustained voiced speech (rejects clicks/breaths)
_BLOCKS_NOISY = 5     # ~320 ms in reverberant rooms

_FLOOR_WINDOW = 48
_FLOOR_Q = 35
_WARMUP = 6           # ~380 ms echo calibration window when speakers are audible
_RELEARN_RUN = 28

_PCM_FLOOR = 60.0
_PCM_FULL = 2600.0


def band_energies(pcm, sr: int) -> np.ndarray:
    """Raw energy per speech band — left unnormalised for linear projection."""
    x = np.asarray(pcm, dtype=np.float32).reshape(-1)
    if x.size < 64:
        return np.zeros(len(_BAND_EDGES) - 1, dtype=np.float32)
    x = x - x.mean()
    n = 1 << (int(x.size) - 1).bit_length()
    mag = np.abs(np.fft.rfft(x * np.hanning(x.size), n=n))
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    out = np.empty(len(_BAND_EDGES) - 1, dtype=np.float32)
    for i in range(len(_BAND_EDGES) - 1):
        m = (freqs >= _BAND_EDGES[i]) & (freqs < _BAND_EDGES[i + 1])
        out[i] = float(mag[m].sum())
    return out


def speech_band_level(pcm, sr: int = 16000) -> float:
    """Map int16 PCM loudness strictly inside 250–3400 Hz to 0.0–1.0.

    Unlike wideband RMS, this ignores <250 Hz mic wind/breath puffs, desk bumps,
    and >3400 Hz sibilant/fan hiss.
    """
    try:
        x = np.asarray(pcm, dtype=np.float32).reshape(-1)
        if x.size < 64:
            return 0.0
        x = x - x.mean()
        n = 1 << (int(x.size) - 1).bit_length()
        spec = np.fft.rfft(x, n=n)
        freqs = np.fft.rfftfreq(n, 1.0 / sr)
        mask = (freqs >= 250.0) & (freqs <= 3400.0)
        band_pwr = float(np.sum(spec[mask].real ** 2 + spec[mask].imag ** 2))
        rms = float(np.sqrt(2.0 * band_pwr / (x.size * n)))
    except Exception:
        return 0.0
    if rms <= _PCM_FLOOR:
        return 0.0
    return min(1.0, (rms - _PCM_FLOOR) / (_PCM_FULL - _PCM_FLOOR))


def is_voiced_speech(pcm, sr: int = 16000) -> bool:
    """True only when `pcm` carries periodic human vocal-fold vibration + formants.

    Rejects:
      - Close-mic nasal/mouth breathing & sighs (unvoiced turbulent airflow)
      - Mic wind puffs & desk thumps (sub-250 Hz dominant)
      - Keyboard/mouse clicks & taps (impulsive, non-periodic across sub-windows)
      - 50/60/120 Hz mains or fan drone (missing upper formant energy >600 Hz)
    """
    try:
        x = np.asarray(pcm, dtype=np.float32).reshape(-1)
        if x.size < 256:
            return False
        x = x - x.mean()
        if float(np.dot(x, x)) <= 1e-6:
            return False

        win = np.hanning(x.size).astype(np.float32)
        nfft = 1 << (int(x.size) - 1).bit_length()
        spec = np.fft.rfft(x * win, n=nfft)
        pwr = spec.real * spec.real + spec.imag * spec.imag
        freqs = np.fft.rfftfreq(nfft, 1.0 / sr)

        p_total   = float(pwr[freqs >= 50.0].sum()) + 1e-12
        p_sub     = float(pwr[(freqs >= 50.0) & (freqs < 250.0)].sum())
        p_pitch   = float(pwr[(freqs >= 90.0) & (freqs <= 1250.0)].sum())
        p_formant = float(pwr[(freqs >= 300.0) & (freqs <= 3500.0)].sum())
        p_upper   = float(pwr[(freqs >= 600.0) & (freqs <= 3400.0)].sum())
        p_hiss    = float(pwr[freqs > 3400.0].sum())

        if (
            (p_formant / p_total) < 0.28
            or (p_pitch / p_total) < 0.09
            or (p_upper / p_total) < 0.06
            or (p_sub / p_total) >= 0.65
            or (p_hiss / p_total) >= 0.45
        ):
            return False

        # Band-limited (85–1250 Hz) pitch autocorrelation on ~28 ms sub-windows
        # across the human fundamental frequency range (80–380 Hz).
        win_len = min(x.size, max(256, int(0.028 * sr)))
        step = max(128, win_len // 2)
        lag_lo = max(1, int(sr / 380.0))
        lag_hi = min(win_len - 32, int(sr / 80.0))
        if lag_hi <= lag_lo + 2:
            return False

        n_ac = 1 << int(2 * win_len - 1).bit_length()
        f_ac = np.fft.rfftfreq(n_ac, 1.0 / sr)
        bp_mask = ((f_ac >= 85.0) & (f_ac <= 1250.0)).astype(np.float32)

        corrs: list[float] = []
        lags_best: list[int] = []
        for start in range(0, x.size - win_len + 1, step):
            seg = x[start : start + win_len]
            seg = seg - seg.mean()
            sp = np.fft.rfft(seg, n=n_ac) * bp_mask
            ac = np.fft.irfft(sp.real * sp.real + sp.imag * sp.imag, n=n_ac)
            if ac[0] <= 1e-9:
                continue
            region = ac[lag_lo - 1 : lag_hi + 2]
            peaks = (region[1:-1] > region[:-2]) & (region[1:-1] >= region[2:])
            if not np.any(peaks):
                corrs.append(0.0)
                continue
            vals = region[1:-1]
            idx = int(np.argmax(np.where(peaks, vals, -1e30)))
            corrs.append(float(vals[idx] / (ac[0] + 1e-12)))
            lags_best.append(lag_lo + idx)

        if len(corrs) < 2:
            return False
        if float(np.mean(corrs)) < 0.36 or float(min(corrs)) < 0.26:
            return False
        if len(lags_best) < 2:
            return False
        jitter = (max(lags_best) - min(lags_best)) / float(np.median(lags_best))
        if jitter > 0.22:
            return False

        return True
    except Exception:
        return False


class EchoGuard:
    """Classifies microphone blocks while the assistant is speaking."""

    def __init__(self) -> None:
        self._hist: list[tuple[float, np.ndarray, float]] = []
        self._gain = 0.5          # mic speech-band level per unit of output level
        self._seen = 0
        self._last_sim = 0.0
        self._last_expected = 0.0
        self._residuals: list[float] = []
        self._floor = 0.10
        self._run = 0
        self._head = 0.14

    @property
    def gain(self) -> float:
        return self._gain

    @property
    def calibrated(self) -> bool:
        return self._seen >= 8

    @property
    def floor(self) -> float:
        return self._floor

    @property
    def reliable(self) -> bool:
        return self._floor < _UNRELIABLE_FLOOR

    @property
    def threshold(self) -> float:
        return max(_MIN_USER, self._head * _HEAD_MULT)

    @property
    def required_blocks(self) -> int:
        return _BLOCKS_NORMAL if self.reliable else _BLOCKS_NOISY

    @property
    def last_similarity(self) -> float:
        return self._last_sim

    def reset(self) -> None:
        """Playback stopped — drop the history, keep what was learned."""
        self._hist.clear()
        self._last_sim = 0.0

    def note_output(self, pcm, sr: int, level: float, when: float | None = None) -> None:
        """Record ~64 ms slices of what is being played, for syllable-accurate matching."""
        try:
            t = time.monotonic() if when is None else when
            arr = np.asarray(pcm)
            slice_len = max(256, int(0.064 * sr))
            if arr.size >= slice_len * 2:
                step = slice_len
                dt = step / float(sr)
                idx = 0
                for start in range(0, arr.size - slice_len + 1, step):
                    seg = arr[start : start + slice_len]
                    sb_lvl = speech_band_level(seg, sr)
                    eff_lvl = sb_lvl if sb_lvl > 0.0 else float(level)
                    self._hist.append((t + idx * dt, band_energies(seg, sr), eff_lvl))
                    idx += 1
            else:
                sb_lvl = speech_band_level(arr, sr)
                eff_lvl = sb_lvl if sb_lvl > 0.0 else float(level)
                self._hist.append((t, band_energies(arr, sr), eff_lvl))
            cutoff = t - _HISTORY_S
            if len(self._hist) > 16:
                self._hist = [h for h in self._hist if h[0] >= cutoff]
        except Exception:
            pass

    def is_user_speech(
        self,
        pcm,
        sr: int,
        level: float | None = None,
        when: float | None = None,
    ) -> bool:
        """True only if `pcm` is genuine voiced user speech, NOT echo or breath."""
        try:
            sb_level = speech_band_level(pcm, sr)
            eff_level = sb_level

            if eff_level < _MIN_LEVEL:
                if self._hist and max(h[2] for h in self._hist) > 0.15:
                    self._residuals.append(0.0)
                    if len(self._residuals) > _FLOOR_WINDOW:
                        del self._residuals[:-_FLOOR_WINDOW]
                    if len(self._residuals) >= _WARMUP:
                        self._floor = float(np.percentile(self._residuals, _FLOOR_Q))
                        self._head = float(np.percentile(self._residuals, _HEAD_Q))
                    self._gain = max(0.02, self._gain * 0.92)
                    self._seen = min(self._seen + 1, 999)
                self._run = 0
                return False

            # Reject breathing, sighs, clicks, wind puffs & hum up front before
            # they can ever trigger barge-in or corrupt echo statistics.
            voiced = is_voiced_speech(pcm, sr)

            if not self._hist:
                self._run = (self._run + 1) if voiced else 0
                return voiced

            t = time.monotonic() if when is None else when
            bands = band_energies(pcm, sr)
            m_v = bands[:_FORMANT_BANDS]
            total_v = float(m_v.sum())
            if total_v <= 1e-9:
                self._run = 0
                return False

            # Project formant bands (200–3800 Hz) onto recent playback slices so
            # high-frequency breath hiss (>3800 Hz) cannot inflate residual ratio.
            best_res, best_level = 1.0, 0.0
            for ts, ref, ref_level in self._hist:
                if ts > t or t - ts > _HISTORY_S:
                    continue
                r_v = ref[:_FORMANT_BANDS]
                denom = float(np.dot(r_v, r_v))
                if denom < 1e-12:
                    continue
                alpha = max(0.0, float(np.dot(m_v, r_v)) / denom)
                residual = np.maximum(m_v - alpha * r_v, 0.0)
                ratio = float(residual.sum()) / total_v
                if ratio < best_res:
                    best_res, best_level = ratio, ref_level
            self._last_sim = 1.0 - best_res

            if best_level <= 0.0:
                self._run = (self._run + 1) if voiced else 0
                return voiced

            if not voiced:
                self._run = 0
                return False

            warming = len(self._residuals) < _WARMUP
            thr = self.threshold
            exp_echo = self._gain * best_level
            self._last_expected = exp_echo

            # Count as user speech when voiced AND either:
            #  (a) formant timbre differs from speaker output + clears echo level, or
            #  (b) user is speaking with clear voiced energy well above expected echo
            #      (handles overlapping male/female timbres).
            distinct_timbre = (not warming) and (best_res >= thr) and (eff_level >= exp_echo + 0.04)
            louder_voiced = (self.calibrated or not warming) and (eff_level >= exp_echo + 0.09)
            speech = distinct_timbre or louder_voiced

            if speech:
                self._run += 1
                if self._run > _RELEARN_RUN:
                    self._residuals.clear()
                    self._run = 0
                    return False
                return True

            self._run = 0
            self._residuals.append(best_res)
            if len(self._residuals) > _FLOOR_WINDOW:
                del self._residuals[:-_FLOOR_WINDOW]
            if len(self._residuals) >= _WARMUP:
                self._floor = float(np.percentile(self._residuals, _FLOOR_Q))
                self._head = float(np.percentile(self._residuals, _HEAD_Q))
            if warming:
                obs = eff_level / max(best_level, 1e-6)
                self._gain += (min(obs, 3.0) - self._gain) * 0.15
                self._seen = min(self._seen + 1, 999)
                return False

            if best_res <= self._floor * 1.20 and best_level > 0.05:
                obs = eff_level / max(best_level, 1e-6)
                self._gain += (min(obs, 3.0) - self._gain) * 0.08
                self._seen = min(self._seen + 1, 999)
            return False
        except Exception:
            return False
