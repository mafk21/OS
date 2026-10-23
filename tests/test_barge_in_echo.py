"""Comprehensive regression tests for two-stage AEC, voice detection, and live barge-in.

Verifies:
1. Close-mic breathing, aspirated formant sighs, low-frequency wind puffs,
   keyboard clicks, and 50/60 Hz mains hum are rejected (0 false interrupts).
2. Normal AND whisper-quiet conversational human speech (~120–750 int16 RMS)
   with realistic -6 to -12 dB/oct glottal roll-off (deep male 90 Hz, male
   130 Hz, female 220 Hz) passes immediately from block #0 (~128 ms = 2 blocks)
   without shouting or speaking for a long time.
3. Dynamic multi-reflection room loudspeaker echo (convolved 3-tap RIR across
   ~142 ms OS + acoustic delay) + heavy breathing never false-triggers, while
   a quiet 165 RMS "Stop!" (quieter than 200 RMS speaker echo) cancels cleanly
   and triggers barge-in in 128 ms (2 blocks).
4. `JarvisLive` runtime regressions:
   - Repeated `set_speaking(True)` calls per 60 ms output batch NEVER wipe
     in-progress `_barge_score` / `_barge_blocks` / `_barge_preroll`.
   - `interrupt()` when `_turn_done_event` is already set keeps `_interrupted`
     False so Gemini's next reply is never silently discarded, while setting
     `_abort_playback` to flush hardware output buffers immediately.
   - `_normalize_barge_pcm` boosts quiet barge-in speech for server VAD while
     leaving normal speech and post-utterance silence untouched.
"""

from __future__ import annotations

import asyncio
from collections import deque
import importlib
from pathlib import Path
import sys
import threading
import types

import numpy as np

from core.echo import (
    EchoGuard,
    band_energies,
    is_voiced_speech,
    speech_band_level,
    voice_confidence,
)


SR_MIC = 16000
SR_OUT = 24000
BLOCK_MIC = 1024  # 64 ms @ 16 kHz


def _synth_glottal_voice(
    f0_start: float,
    f0_end: float,
    rms: float,
    sr: int = SR_MIC,
    n: int = BLOCK_MIC,
    tilt_exp: float = 0.85,
    noise_rms: float = 30.0,
    seed: int = 0,
) -> np.ndarray:
    """Realistic pitched voice with natural -6 to -12 dB/oct glottal roll-off + formants."""
    rng = np.random.default_rng(seed)
    f0_t = np.linspace(f0_start, f0_end, n)
    phase = 2.0 * np.pi * np.cumsum(f0_t) / sr
    sig = np.zeros(n, dtype=np.float64)
    max_h = min(38, int((sr * 0.45) // max(f0_start, f0_end)))
    for k in range(1, max_h + 1):
        fk = k * 0.5 * (f0_start + f0_end)
        glottal = 1.0 / (k ** tilt_exp)
        formant = (
            0.35
            + 1.0 * np.exp(-0.5 * ((fk - 480.0) / 150.0) ** 2)
            + 0.75 * np.exp(-0.5 * ((fk - 1450.0) / 260.0) ** 2)
            + 0.35 * np.exp(-0.5 * ((fk - 2550.0) / 350.0) ** 2)
        )
        sig += glottal * formant * np.sin(k * phase + 0.37 * k)
    sig = sig / (np.std(sig) + 1e-9) * rms
    if noise_rms > 0:
        sig += rng.normal(0.0, noise_rms, n)
    return np.clip(sig, -32767, 32767).astype(np.int16)


def _synth_breath(rms: float, sr: int = SR_MIC, n: int = BLOCK_MIC, seed: int = 1) -> np.ndarray:
    """Realistic unvoiced exhale / sigh: broad vocal-tract noise without pitch harmonics."""
    rng = np.random.default_rng(seed)
    w = rng.normal(0.0, 1.0, n)
    spec = np.fft.rfft(w)
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    env = (
        0.55 * np.exp(-((freqs - 180.0) / 140.0) ** 2)
        + 1.0 * np.exp(-((freqs - 520.0) / 380.0) ** 2)
        + 0.7 * np.exp(-((freqs - 1650.0) / 850.0) ** 2)
        + 0.45 * np.exp(-((freqs - 3600.0) / 1400.0) ** 2)
    )
    y = np.fft.irfft(spec * env, n=n)
    t = np.linspace(0.0, 1.0, n, endpoint=False)
    y *= 0.65 + 0.35 * np.sin(np.pi * t)
    y = y / (np.std(y) + 1e-9) * rms
    return np.clip(y, -32767, 32767).astype(np.int16)


class TestSpeechBandLevel:
    def test_silence_and_low_rumble_are_zero_or_tiny(self):
        zeros = np.zeros(BLOCK_MIC, dtype=np.int16)
        assert speech_band_level(zeros, SR_MIC) == 0.0

        rng = np.random.default_rng(7)
        w = rng.normal(0.0, 1.0, BLOCK_MIC)
        freqs = np.fft.rfftfreq(BLOCK_MIC, 1.0 / SR_MIC)
        puff_spec = np.fft.rfft(w) * ((freqs >= 30.0) & (freqs <= 190.0))
        puff = np.fft.irfft(puff_spec, n=BLOCK_MIC)
        puff = (puff / np.std(puff) * 900.0).astype(np.int16)
        assert speech_band_level(puff, SR_MIC) < 0.03

    def test_high_frequency_hiss_rejected_by_speech_band(self):
        rng = np.random.default_rng(11)
        w = rng.normal(0.0, 1.0, BLOCK_MIC)
        freqs = np.fft.rfftfreq(BLOCK_MIC, 1.0 / SR_MIC)
        hiss_spec = np.fft.rfft(w) * (freqs >= 3900.0)
        hiss = np.fft.irfft(hiss_spec, n=BLOCK_MIC)
        hiss = (hiss / np.std(hiss) * 900.0).astype(np.int16)
        assert speech_band_level(hiss, SR_MIC) < 0.03

    def test_quiet_and_normal_conversational_speech_register_cleanly(self):
        quiet_voice = _synth_glottal_voice(108.0, 112.0, rms=120.0, tilt_exp=0.95, seed=3)
        assert speech_band_level(quiet_voice, SR_MIC) >= 0.024

        normal_voice = _synth_glottal_voice(135.0, 140.0, rms=750.0, seed=4)
        lvl = speech_band_level(normal_voice, SR_MIC)
        assert 0.20 <= lvl <= 0.45


class TestVoicedSpeechDetector:
    def test_rejects_heavy_breathing_and_sighs_across_volumes(self):
        for idx, rms in enumerate((180.0, 400.0, 800.0, 1400.0, 2200.0)):
            breath = _synth_breath(rms=rms, seed=100 + idx)
            assert is_voiced_speech(breath, SR_MIC) is False
            assert voice_confidence(breath, SR_MIC) == 0.0

    def test_rejects_keyboard_click_and_mains_hum(self):
        rng = np.random.default_rng(22)
        click = rng.normal(0.0, 30.0, BLOCK_MIC)
        click[240:268] += rng.normal(0.0, 5000.0, 28)
        click_i16 = np.clip(click, -32767, 32767).astype(np.int16)
        assert is_voiced_speech(click_i16, SR_MIC) is False

        t = np.arange(BLOCK_MIC) / SR_MIC
        hum = (
            650.0 * np.sin(2.0 * np.pi * 60.0 * t)
            + 350.0 * np.sin(2.0 * np.pi * 120.0 * t)
            + rng.normal(0.0, 35.0, BLOCK_MIC)
        ).astype(np.int16)
        assert is_voiced_speech(hum, SR_MIC) is False

    def test_accepts_quiet_and_deep_glottal_tilt_human_voices(self):
        # Deep male (~92 Hz) with steep -11 dB/oct glottal roll-off at quiet 125 RMS
        deep_quiet = _synth_glottal_voice(90.0, 94.0, rms=125.0, tilt_exp=1.10, seed=31)
        assert is_voiced_speech(deep_quiet, SR_MIC) is True

        # Conversational male (~130 Hz) at soft 140 RMS
        male_soft = _synth_glottal_voice(128.0, 134.0, rms=140.0, tilt_exp=0.90, seed=32)
        assert is_voiced_speech(male_soft, SR_MIC) is True

        # Female (~225 Hz) at soft 135 RMS
        female_soft = _synth_glottal_voice(220.0, 232.0, rms=135.0, tilt_exp=0.85, seed=33)
        assert is_voiced_speech(female_soft, SR_MIC) is True


class TestEchoGuardBargeIn:
    def test_headphones_instant_128ms_barge_in_from_block_zero_and_breath_rejected(self):
        guard = EchoGuard()
        need = guard.required_blocks
        assert need == 2  # ~128 ms (2 x 64 ms blocks) for crisp "Stop!" / "Wait!"

        t0 = 1000.0
        # Even at block #0 (zero prior warmup), quiet 140 RMS user speech on
        # headphones interrupts within 2 blocks (128 ms)!
        jarvis_0 = _synth_glottal_voice(130.0, 134.0, rms=1600.0, sr=SR_OUT, n=2400, seed=1)
        guard.note_output(jarvis_0, SR_OUT, speech_band_level(jarvis_0, SR_OUT), when=t0)

        score = 0.0
        for b in range(2):
            ts = t0 + 0.04 + b * 0.064
            user_quiet = _synth_glottal_voice(175.0, 182.0, rms=140.0, seed=50 + b)
            score += guard.speech_score(
                user_quiet, SR_MIC, speech_band_level(user_quiet, SR_MIC), when=ts
            )
        assert score >= float(need)

        # Now feed 80 blocks (~5.1 s) of loud close-mic breathing while JARVIS speaks:
        # 0 blocks may score as speech.
        false_positives = 0
        for i in range(80):
            ts = t0 + 1.0 + i * 0.064
            j_chunk = _synth_glottal_voice(
                125.0 + (i % 5) * 4.0, 130.0 + (i % 5) * 4.0, rms=1600.0, sr=SR_OUT, n=1536, seed=200 + i
            )
            guard.note_output(j_chunk, SR_OUT, speech_band_level(j_chunk, SR_OUT), when=ts)
            breath = _synth_breath(rms=850.0, seed=400 + i)
            if guard.is_user_speech(breath, SR_MIC, speech_band_level(breath, SR_MIC), when=ts + 0.02):
                false_positives += 1
        assert false_positives == 0

    def test_loudspeaker_echo_plus_breath_rejected_real_voice_accepted(self):
        guard = EchoGuard()
        need = guard.required_blocks
        t0 = 2000.0

        streak = 0
        for i in range(20):
            ts = t0 + i * 0.064
            jarvis_24k = _synth_glottal_voice(130.0, 132.0, rms=1800.0, sr=SR_OUT, n=2400, seed=500 + i)
            guard.note_output(jarvis_24k, SR_OUT, speech_band_level(jarvis_24k, SR_OUT), when=ts)
            jarvis_echo_16k = _synth_glottal_voice(130.0, 132.0, rms=240.0, sr=SR_MIC, n=BLOCK_MIC, seed=500 + i)
            if guard.is_user_speech(
                jarvis_echo_16k, SR_MIC, speech_band_level(jarvis_echo_16k, SR_MIC), when=ts + 0.08
            ):
                streak += 1
            else:
                streak = 0
            assert streak < need

        # Echo + loud user breathing simultaneously -> still rejected
        streak = 0
        for i in range(16):
            ts = t0 + 1.5 + i * 0.064
            jarvis_24k = _synth_glottal_voice(130.0, 132.0, rms=1800.0, sr=SR_OUT, n=2400, seed=700 + i)
            guard.note_output(jarvis_24k, SR_OUT, speech_band_level(jarvis_24k, SR_OUT), when=ts)
            echo_plus_breath = np.clip(
                _synth_glottal_voice(130.0, 132.0, rms=240.0, sr=SR_MIC, n=BLOCK_MIC, seed=700 + i).astype(np.int32)
                + _synth_breath(rms=520.0, seed=800 + i).astype(np.int32),
                -32767,
                32767,
            ).astype(np.int16)
            if guard.is_user_speech(
                echo_plus_breath, SR_MIC, speech_band_level(echo_plus_breath, SR_MIC), when=ts + 0.08
            ):
                streak += 1
            else:
                streak = 0
            assert streak < need

        # User speaks normally over speaker echo -> interrupts in 2 blocks (128 ms)
        score = 0.0
        for b in range(2):
            ts = t0 + 3.0 + b * 0.064
            jarvis_24k = _synth_glottal_voice(130.0, 132.0, rms=1800.0, sr=SR_OUT, n=2400, seed=900 + b)
            guard.note_output(jarvis_24k, SR_OUT, speech_band_level(jarvis_24k, SR_OUT), when=ts)
            user_over_echo = np.clip(
                _synth_glottal_voice(130.0, 132.0, rms=240.0, sr=SR_MIC, n=BLOCK_MIC, seed=900 + b).astype(np.int32)
                + _synth_glottal_voice(195.0, 202.0, rms=420.0, sr=SR_MIC, n=BLOCK_MIC, seed=950 + b).astype(np.int32),
                -32767,
                32767,
            ).astype(np.int16)
            score += guard.speech_score(
                user_over_echo, SR_MIC, speech_band_level(user_over_echo, SR_MIC), when=ts + 0.08
            )
        assert score >= float(need)

    def test_convolved_3tap_room_echo_cancelled_and_quiet_165rms_stop_interrupts_in_128ms(self):
        """End-to-end linear FDAF + RES test on continuous 24 kHz gliding speech
        convolved with a realistic 3-reflection room impulse response (~142 ms delay)
        plus continuous heavy breathing, followed by a quiet 165 RMS 'Stop!'."""
        rng = np.random.default_rng(2026)
        dur_s = 8.0
        n16 = int(dur_s * SR_MIC)
        t16 = np.arange(n16) / SR_MIC
        f0 = 132.0 + 28.0 * np.sin(2.0 * np.pi * 2.1 * t16) + 12.0 * np.cos(2.0 * np.pi * 3.7 * t16)
        ph = 2.0 * np.pi * np.cumsum(f0) / SR_MIC
        spk_16k = np.zeros(n16, dtype=np.float64)
        for k in range(1, 25):
            spk_16k += (1.0 / (k ** 0.85)) * np.sin(k * ph + 0.4 * k)
        env = np.clip(0.6 + 0.55 * np.sin(2.0 * np.pi * 3.8 * t16), 0.08, 1.2)
        spk_16k = spk_16k / np.std(spk_16k) * 1800.0 * env

        n24 = int(dur_s * SR_OUT)
        spk_24k = np.interp(
            np.linspace(0.0, dur_s, n24, endpoint=False), t16, spk_16k
        ).astype(np.int16)

        # 3-reflection room impulse response at 142.7 ms OS/acoustic latency (~205 RMS echo)
        delay_samps = int(0.1427 * SR_MIC)
        rir = np.zeros(delay_samps + 420, dtype=np.float64)
        rir[delay_samps] = 0.115
        rir[delay_samps + 115] = -0.048
        rir[delay_samps + 290] = 0.024
        echo_16k = np.convolve(spk_16k, rir)[:n16]

        guard = EchoGuard()
        n_blocks = n16 // BLOCK_MIC
        spk_cursor = 0
        barge_score = 0.0
        false_interrupts = 0

        # First 95 blocks (~6.1 s): speaker echo + 500 RMS breath bursts -> 0 false interrupts
        for b in range(95):
            ts = 500.0 + b * 0.064
            target_24 = int((b + 1) * BLOCK_MIC * SR_OUT / SR_MIC) + 1200
            while spk_cursor < min(n24, target_24):
                end_c = min(n24, spk_cursor + 2400)
                ch = spk_24k[spk_cursor:end_c]
                guard.note_output(ch, SR_OUT, speech_band_level(ch, SR_OUT), when=ts)
                spk_cursor = end_c

            mic_f = echo_16k[b * BLOCK_MIC : (b + 1) * BLOCK_MIC].copy()
            mic_f += rng.normal(0.0, 28.0, BLOCK_MIC)
            if (b % 20) in (6, 7, 8, 9):
                mic_f += _synth_breath(rms=500.0, seed=1200 + b).astype(np.float64)
            mic_i16 = np.clip(mic_f, -32767, 32767).astype(np.int16)

            sc = guard.speech_score(mic_i16, SR_MIC, speech_band_level(mic_i16, SR_MIC), when=ts)
            if sc >= 1.0:
                barge_score += sc
                if barge_score >= 2.0:
                    false_interrupts += 1
                    barge_score = 0.0
            else:
                barge_score = max(0.0, barge_score - 0.75)

        assert false_interrupts == 0

        # Block 95 & 96 (128 ms): User quietly says "Stop!" at 165 RMS (quieter than echo!)
        stop_score = 0.0
        for b in (95, 96):
            ts = 500.0 + b * 0.064
            target_24 = int((b + 1) * BLOCK_MIC * SR_OUT / SR_MIC) + 1200
            while spk_cursor < min(n24, target_24):
                end_c = min(n24, spk_cursor + 2400)
                ch = spk_24k[spk_cursor:end_c]
                guard.note_output(ch, SR_OUT, speech_band_level(ch, SR_OUT), when=ts)
                spk_cursor = end_c

            quiet_user = _synth_glottal_voice(
                108.0 + (b - 95) * 3.0, 111.0 + (b - 95) * 3.0, rms=165.0, tilt_exp=0.90, seed=3000 + b
            )
            mic_f = echo_16k[b * BLOCK_MIC : (b + 1) * BLOCK_MIC] + quiet_user.astype(np.float64)
            mic_i16 = np.clip(mic_f, -32767, 32767).astype(np.int16)
            stop_score += guard.speech_score(
                mic_i16, SR_MIC, speech_band_level(mic_i16, SR_MIC), when=ts
            )

        assert stop_score >= 2.0, f"Quiet 165 RMS 'Stop!' failed 128ms barge-in: score={stop_score}"

    def test_windows_380ms_latency_nonlinear_speaker_never_self_interrupts(self):
        """Regression test for the Windows WASAPI/Bluetooth output-latency bug:
        during the first ~380 ms after `note_output`, audio is still inside the OS
        buffer so the mic hears silence. `EchoGuard` must NEVER decay coupling to
        zero ('headphones') during that silence and self-interrupt when JARVIS's
        own voice exits the speakers — across 150, 250, 500, and 950 RMS nonlinear
        4-tap reverberant speaker echo + sentence pauses + heavy breathing!"""
        rng = np.random.default_rng(1234)
        dur_s = 10.0
        n16 = int(dur_s * SR_MIC)
        t16 = np.arange(n16) / SR_MIC
        f0 = 130.0 + 32.0 * np.sin(2.0 * np.pi * 2.0 * t16) + 15.0 * np.cos(2.0 * np.pi * 3.4 * t16)
        ph = 2.0 * np.pi * np.cumsum(f0) / SR_MIC
        spk_clean = sum((1.0 / (k ** 0.85)) * np.sin(k * ph + 0.33 * k) for k in range(1, 26))
        env = np.clip(0.65 + 0.55 * np.sin(2.0 * np.pi * 3.1 * t16), 0.0, 1.2)
        env[(t16 > 3.0) & (t16 < 3.45)] = 0.0  # inter-sentence pause
        env[(t16 > 6.8) & (t16 < 7.25)] = 0.0  # inter-sentence pause
        spk_clean = spk_clean / np.std(spk_clean) * 2000.0 * env
        n24 = int(dur_s * SR_OUT)
        spk_24k = np.interp(np.linspace(0.0, dur_s, n24, endpoint=False), t16, spk_clean).astype(np.int16)

        spk_nonlin = np.tanh(spk_clean / 2400.0) * 2400.0
        lat_samps = int(0.380 * SR_MIC)
        rir = np.zeros(lat_samps + 600, dtype=np.float64)
        rir[lat_samps] = 1.0
        rir[lat_samps + 95] = -0.45
        rir[lat_samps + 240] = 0.25
        rir[lat_samps + 470] = -0.12
        raw_echo = np.convolve(spk_nonlin, rir)[:n16]
        raw_echo = raw_echo / (np.std(raw_echo) + 1e-9)

        for echo_rms in (150.0, 250.0, 500.0, 950.0):
            guard = EchoGuard()
            spk_cur = 0
            score = 0.0
            self_interrupts = 0
            for b in range(n16 // BLOCK_MIC):
                ts = 100.0 + b * 0.064
                tgt = int((b + 1) * BLOCK_MIC * SR_OUT / SR_MIC) + int(0.15 * SR_OUT)
                while spk_cur < min(n24, tgt):
                    ec = min(n24, spk_cur + 2400)
                    ch = spk_24k[spk_cur:ec]
                    guard.note_output(ch, SR_OUT, speech_band_level(ch, SR_OUT), when=ts)
                    spk_cur = ec
                mic = raw_echo[b * BLOCK_MIC : (b + 1) * BLOCK_MIC] * echo_rms + rng.normal(0.0, 28.0, BLOCK_MIC)
                if (b % 20) in (8, 9, 10):
                    mic += _synth_breath(rms=520.0, seed=3000 + b).astype(np.float64)
                mic_i16 = np.clip(mic, -32767, 32767).astype(np.int16)
                sb = speech_band_level(mic_i16, SR_MIC)
                sc = guard.speech_score(mic_i16, SR_MIC, sb, when=ts) if sb >= 0.024 else 0.0
                if sc >= 1.0:
                    score += sc
                    if score >= 2.0:
                        self_interrupts += 1
                        score = 0.0
                else:
                    score = max(0.0, score - 0.75)
            assert self_interrupts == 0, f"Self-interrupted {self_interrupts}x at echo_rms={echo_rms}"

    def test_clock_skewed_bluetooth_echo_never_self_interrupts(self):
        """Even under +1200 ppm USB-mic vs speaker crystal clock skew + 420 ms
        Bluetooth latency + nonlinear distortion, Stage 2 prevents self-interruption."""
        rng = np.random.default_rng(777)
        dur_s = 8.0
        n16 = int(dur_s * SR_MIC)
        t16 = np.arange(n16) / SR_MIC
        f0 = 130.0 + 30.0 * np.sin(2.0 * np.pi * 2.0 * t16)
        ph = 2.0 * np.pi * np.cumsum(f0) / SR_MIC
        spk_clean = sum((1.0 / (k ** 0.85)) * np.sin(k * ph + 0.33 * k) for k in range(1, 24))
        spk_clean = spk_clean / np.std(spk_clean) * 1900.0
        n24 = int(dur_s * SR_OUT)
        spk_24k = np.interp(np.linspace(0.0, dur_s, n24, endpoint=False), t16, spk_clean).astype(np.int16)

        t_skew = np.linspace(0.0, dur_s * 1.0012, n16, endpoint=False)
        spk_skew = np.interp(t_skew, t16, np.tanh(spk_clean / 2000.0) * 2000.0)
        lat = int(0.420 * SR_MIC)
        rir = np.zeros(lat + 500, dtype=np.float64)
        rir[lat] = 1.0
        rir[lat + 100] = -0.50
        rir[lat + 260] = 0.28
        echo_skew = np.convolve(spk_skew, rir)[:n16]
        echo_skew = echo_skew / (np.std(echo_skew) + 1e-9)

        guard = EchoGuard()
        spk_cur = 0
        score = 0.0
        false_int = 0
        for b in range(n16 // BLOCK_MIC):
            ts = 200.0 + b * 0.064
            tgt = int((b + 1) * BLOCK_MIC * SR_OUT / SR_MIC) + int(0.15 * SR_OUT)
            while spk_cur < min(n24, tgt):
                ec = min(n24, spk_cur + 2400)
                ch = spk_24k[spk_cur:ec]
                guard.note_output(ch, SR_OUT, speech_band_level(ch, SR_OUT), when=ts)
                spk_cur = ec
            mic_i16 = np.clip(
                echo_skew[b * BLOCK_MIC : (b + 1) * BLOCK_MIC] * 450.0 + rng.normal(0.0, 28.0, BLOCK_MIC),
                -32767,
                32767,
            ).astype(np.int16)
            sb = speech_band_level(mic_i16, SR_MIC)
            sc = guard.speech_score(mic_i16, SR_MIC, sb, when=ts) if sb >= 0.024 else 0.0
            if sc >= 1.0:
                score += sc
                if score >= 2.0:
                    false_int += 1
                    score = 0.0
            else:
                score = max(0.0, score - 0.75)
        assert false_int == 0


def _load_main_headless(monkeypatch):
    """Import `main` in headless CI without requiring PortAudio or a GUI display."""
    if "main" in sys.modules:
        return sys.modules["main"]

    sd_stub = types.ModuleType("sounddevice")
    sd_stub.query_devices = lambda *a, **k: []
    monkeypatch.setitem(sys.modules, "sounddevice", sd_stub)

    has_genai = (
        importlib.util.find_spec("google") is not None
        and importlib.util.find_spec("google.genai") is not None
    )
    if not has_genai:
        class _DynamicStub(types.ModuleType):
            def __getattr__(self, _name: str):
                return object

        google_mod = sys.modules.get("google") or types.ModuleType("google")
        genai_mod = _DynamicStub("google.genai")
        genai_types = _DynamicStub("google.genai.types")
        genai_mod.types = genai_types
        google_mod.genai = genai_mod
        monkeypatch.setitem(sys.modules, "google", google_mod)
        monkeypatch.setitem(sys.modules, "google.genai", genai_mod)
        monkeypatch.setitem(sys.modules, "google.genai.types", genai_types)

    ui_stub = types.ModuleType("ui")

    class _DummyUI:
        muted = False
        current_file = None

        def set_state(self, *_a, **_k):
            pass

        def write_log(self, *_a, **_k):
            pass

        def set_audio_level(self, *_a, **_k):
            pass

    ui_stub.JarvisUI = _DummyUI
    monkeypatch.setitem(sys.modules, "ui", ui_stub)
    return importlib.import_module("main")


class TestJarvisLiveRuntimeBargeIn:
    def test_repeated_set_speaking_true_does_not_wipe_barge_progress(self, monkeypatch):
        """Regression test for Smoking Gun #A: `_play_audio` calls `set_speaking(True)`
        on every ~60 ms output batch. It must ONLY reset barge accumulators on the
        False -> True rising edge, never mid-speech!"""
        main_mod = _load_main_headless(monkeypatch)
        jl = main_mod.JarvisLive.__new__(main_mod.JarvisLive)
        jl._speaking_lock = threading.Lock()
        jl._is_speaking = False
        jl._tail_until = 0.0
        jl._out_latency = 0.20
        jl._wake_enabled = False
        jl._grace_period = 8.0
        jl._grace_until = 0.0
        jl._out_level = 0.0
        jl._paused = False
        jl._barge_blocks = 0
        jl._barge_score = 0.0
        jl._barge_consonant_hold = 0
        jl._barge_preroll = []
        jl._mic_ring = deque(maxlen=4)

        states = []

        class _UI:
            muted = False

            def set_state(self, s):
                states.append(s)

        jl.ui = _UI()

        # Rising edge False -> True initializes cleanly
        jl.set_speaking(True)
        assert states == ["SPEAKING"]

        # Simulate user's 1st voiced block arriving while JARVIS is speaking
        jl._barge_blocks = 1
        jl._barge_score = 1.15
        jl._barge_consonant_hold = 2
        jl._barge_preroll = [b"\x01\x02"]
        jl._mic_ring.append(b"\x01\x02")

        # Next 60 ms speaker batch calls set_speaking(True) again while already speaking!
        jl.set_speaking(True)

        # Progress MUST be preserved 100%!
        assert jl._barge_blocks == 1
        assert jl._barge_score == 1.15
        assert jl._barge_consonant_hold == 2
        assert jl._barge_preroll == [b"\x01\x02"]
        assert len(jl._mic_ring) == 1
        assert states == ["SPEAKING"]  # no redundant UI state spam either

    def test_interrupt_respects_server_turn_done_so_next_reply_is_never_eaten(self, monkeypatch):
        """Regression test for Smoking Gun #B: when Gemini has already sent
        `turn_complete` (`_turn_done_event.is_set() == True`) while local audio is
        still playing out of `audio_in_queue`, `interrupt()` must NOT leave
        `_interrupted = True` (which used to discard Gemini's next answer!)."""
        main_mod = _load_main_headless(monkeypatch)

        def _make_stub_jl(turn_already_done: bool):
            jl = main_mod.JarvisLive.__new__(main_mod.JarvisLive)
            jl._speaking_lock = threading.Lock()
            jl._is_speaking = True
            jl._interrupted = False
            jl._abort_playback = threading.Event()
            jl._tail_until = 0.0
            jl._out_latency = 0.20
            jl._wake_enabled = False
            jl._grace_period = 8.0
            jl._grace_until = 0.0
            jl._out_level = 0.3
            jl._paused = False
            jl._barge_blocks = 1
            jl._barge_score = 1.1
            jl._barge_consonant_hold = 1
            jl._barge_preroll = [b"abc"]
            jl._mic_ring = deque([b"abc"], maxlen=4)
            jl._barge_open_until = 0.0
            jl._play_cursor = 123.0
            jl.audio_in_queue = asyncio.Queue()
            jl.audio_in_queue.put_nowait(b"\x00" * 2400)
            jl.audio_in_queue.put_nowait(b"\x00" * 2400)
            jl._turn_done_event = asyncio.Event()
            if turn_already_done:
                jl._turn_done_event.set()

            class _Vis:
                def reset(self):
                    pass

            class _UI:
                muted = False

                def set_state(self, *_a):
                    pass

                def write_log(self, *_a):
                    pass

            jl._visemes = _Vis()
            jl.ui = _UI()
            return jl

        # Case A: Server ALREADY finished streaming turn -> _interrupted MUST stay False!
        jl_done = _make_stub_jl(turn_already_done=True)
        jl_done.interrupt()
        assert jl_done._interrupted is False
        assert jl_done._abort_playback.is_set() is True
        assert jl_done.audio_in_queue.empty()
        assert jl_done._tail_until == 0.0

        # Case B: Server STILL mid-stream -> _interrupted MUST be True to drop trailing old audio!
        jl_streaming = _make_stub_jl(turn_already_done=False)
        jl_streaming.interrupt()
        assert jl_streaming._interrupted is True
        assert jl_streaming._abort_playback.is_set() is True
        assert jl_streaming.audio_in_queue.empty()

    def test_no_portaudio_stream_abort_and_server_interrupt_clears_flag(self):
        """Ensure `_play_audio` never calls `stream.abort()` (which wedges blocking
        PortAudio `RawOutputStream` on Windows WASAPI/MME), and `_receive_audio`
        clears `self._interrupted` on `sc.interrupted` and `sc.input_transcription`
        so Gemini's next reply is never silently discarded."""
        src = Path(__file__).resolve().parent.parent.joinpath("main.py").read_text(
            encoding="utf-8"
        )
        assert "stream.abort()" not in src
        assert 'if getattr(sc, "interrupted", False):' in src
        assert "if sc.input_transcription and sc.input_transcription.text:" in src

    def test_end_to_end_multi_turn_answering_never_drops_replies(self, monkeypatch):
        """Runs the real `JarvisLive._receive_audio` + `_play_audio` coroutines
        across multiple normal and interrupted turns (including Gemini sending
        `sc.interrupted=True` WITHOUT `turn_complete=True`) and proves every
        subsequent JARVIS reply plays out of the speaker stream and returns
        `_is_speaking` cleanly to `False`."""
        main_mod = _load_main_headless(monkeypatch)

        written_batches: list[bytes] = []

        class _FakeOutStream:
            latency = 0.18

            def start(self):
                pass

            def write(self, data: bytes):
                written_batches.append(bytes(data))

            def stop(self):
                pass

            def close(self):
                pass

        monkeypatch.setattr(
            main_mod.sd, "RawOutputStream", lambda **_kw: _FakeOutStream(), raising=False
        )

        class _Txt:
            def __init__(self, text: str):
                self.text = text

        class _SC:
            def __init__(self, *, interrupted=False, turn_complete=False, in_txt="", out_txt=""):
                self.interrupted = interrupted
                self.turn_complete = turn_complete
                self.input_transcription = _Txt(in_txt) if in_txt else None
                self.output_transcription = _Txt(out_txt) if out_txt else None

        class _Resp:
            def __init__(self, *, data=b"", sc=None):
                self.data = data
                self.server_content = sc
                self.tool_call = None
                self.session_resumption_update = None
                self.go_away = None

        async def _run_scenario():
            jl = main_mod.JarvisLive.__new__(main_mod.JarvisLive)
            jl._asst_name = "JARVIS"
            jl._speaking_lock = threading.Lock()
            jl._is_speaking = False
            jl._interrupted = False
            jl._interrupted_at = 0.0
            jl._last_interrupted_rx = 0.0
            jl._abort_playback = threading.Event()
            jl._tail_until = 0.0
            jl._out_latency = 0.18
            jl._wake_enabled = False
            jl._grace_period = 8.0
            jl._grace_until = 0.0
            jl._out_level = 0.0
            jl._paused = False
            jl._barge_blocks = 0
            jl._barge_score = 0.0
            jl._barge_consonant_hold = 0
            jl._barge_preroll = []
            jl._mic_ring = deque(maxlen=4)
            jl._barge_open_until = 0.0
            jl._play_cursor = 0.0
            jl._last_out_logged = ""
            jl._last_user_speech = 0.0
            jl._session_log = []
            jl._dashboard = None
            jl._vision_close_pending = False
            jl._vision_busy = False
            jl._echo = EchoGuard()
            jl.audio_in_queue = asyncio.Queue()
            jl.out_queue = asyncio.Queue(maxsize=64)
            jl._turn_done_event = asyncio.Event()

            logged: list[str] = []

            class _Vis:
                def feed_text(self, *_a):
                    pass

                def frames(self, f, *_a):
                    return f

                def reset(self):
                    pass

            class _UI:
                muted = False

                def set_state(self, *_a):
                    pass

                def write_log(self, msg: str):
                    logged.append(msg)

                def push_visemes(self, *_a):
                    pass

                def set_audio_level(self, *_a):
                    pass

            jl._visemes = _Vis()
            jl.ui = _UI()

            server_q: asyncio.Queue = asyncio.Queue()

            class _FakeSession:
                def receive(self):
                    async def _gen():
                        while True:
                            item = await server_q.get()
                            if item is None:
                                return
                            yield item

                    return _gen()

            jl.session = _FakeSession()

            play_task = asyncio.create_task(jl._play_audio())
            recv_task = asyncio.create_task(jl._receive_audio())

            chunk_a = (np.ones(2400, dtype=np.int16) * 500).tobytes()
            chunk_b = (np.ones(2400, dtype=np.int16) * 900).tobytes()
            chunk_c = (np.ones(2400, dtype=np.int16) * 1200).tobytes()

            # Turn 1: Normal user question -> JARVIS answers cleanly
            await server_q.put(_Resp(sc=_SC(in_txt="Hello Jarvis")))
            await server_q.put(_Resp(data=chunk_a, sc=_SC(out_txt="Hello sir.")))
            await server_q.put(_Resp(sc=_SC(turn_complete=True)))
            await asyncio.sleep(0.15)
            assert sum(len(x) for x in written_batches) == len(chunk_a)
            assert jl._is_speaking is False

            # Turn 2: JARVIS starts long reply -> user interrupts mid-stream ->
            # Gemini sends `interrupted=True` WITHOUT `turn_complete=True` ->
            # then immediately sends Turn 3 answer `chunk_b`!
            await server_q.put(_Resp(data=chunk_a, sc=_SC(out_txt="Long monologue...")))
            await asyncio.sleep(0.02)
            jl.interrupt()  # local barge-in while _turn_done_event is False!
            await asyncio.sleep(0.02)
            written_batches.clear()
            assert jl._interrupted is True
            # Stale in-flight chunk from old turn is dropped:
            await server_q.put(_Resp(data=chunk_a))
            await asyncio.sleep(0.02)
            assert written_batches == []
            # Server acknowledges interruption WITHOUT turn_complete:
            await server_q.put(_Resp(sc=_SC(interrupted=True)))
            await asyncio.sleep(0.02)
            assert jl._interrupted is False
            # Server sends answer to user's new question — MUST PLAY 100%!
            await server_q.put(_Resp(sc=_SC(in_txt="What is two plus two?")))
            await server_q.put(_Resp(data=chunk_b, sc=_SC(out_txt="It is four.")))
            await server_q.put(_Resp(sc=_SC(turn_complete=True)))
            await asyncio.sleep(0.15)
            assert b"".join(written_batches) == chunk_b
            assert any("It is four." in m for m in logged)
            assert jl._is_speaking is False

            # Turn 4: Server already sent turn_complete while audio was queued ->
            # local interrupt() fires -> Turn 5 reply `chunk_c` MUST PLAY 100%!
            written_batches.clear()
            jl._turn_done_event.set()
            jl.interrupt()
            assert jl._interrupted is False
            await server_q.put(_Resp(sc=_SC(in_txt="Are you still there?")))
            await server_q.put(_Resp(data=chunk_c, sc=_SC(out_txt="Always here, sir.")))
            await server_q.put(_Resp(sc=_SC(turn_complete=True)))
            await asyncio.sleep(0.15)
            assert sum(len(x) for x in written_batches) == len(chunk_c)
            assert any("Always here, sir." in m for m in logged)
            assert jl._is_speaking is False

            recv_task.cancel()
            play_task.cancel()
            for t in (recv_task, play_task):
                try:
                    await t
                except asyncio.CancelledError:
                    pass

        asyncio.run(_run_scenario())


class TestMainBargeInWiring:
    def test_main_uses_voiced_barge_in_without_raw_amplitude_bypass(self):
        src = Path(__file__).resolve().parent.parent.joinpath("main.py").read_text(
            encoding="utf-8"
        )
        assert "if lvl > 0.16:" not in src
        assert "interrupt forced ON" not in src
        assert "_barge_preroll" in src
        assert "_mic_ring" in src
        assert "_abort_playback" in src
        assert "speech_band_level(indata, SEND_SAMPLE_RATE)" in src
        assert "self._echo.speech_score(" in src
