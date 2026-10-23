"""Tests for voiced-speech barge-in filtering and EchoGuard echo rejection."""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pytest

from core.echo import EchoGuard, band_energies, is_voiced_speech, speech_band_level

SR_MIC = 16000
SR_SPK = 24000
BLOCK = 1024  # 64 ms @ 16 kHz


def _synth_voice(
    f0_start: float,
    f0_end: float,
    formants: list[tuple[float, float, float]],
    rms: float = 700.0,
    sr: int = SR_MIC,
    n: int = BLOCK,
    rng: np.random.Generator | None = None,
    noise_rms: float = 40.0,
) -> np.ndarray:
    phase = 2.0 * np.pi * np.cumsum(np.linspace(f0_start, f0_end, n)) / sr
    f_mid = 0.5 * (f0_start + f0_end)
    sig = np.zeros(n, dtype=np.float64)
    for k in range(1, int(3600.0 / f_mid) + 1):
        fk = k * f_mid
        env = sum(w * np.exp(-0.5 * ((fk - fc) / bw) ** 2) for w, fc, bw in formants)
        sig += env * np.sin(k * phase + 0.31 * k)
    sig = sig / (np.std(sig) + 1e-9) * rms
    if rng is not None and noise_rms > 0:
        sig = sig + rng.normal(0.0, noise_rms, n)
    return np.clip(sig, -32767, 32767).astype(np.int16)


def _synth_breath(
    rng: np.random.Generator,
    rms: float = 650.0,
    sr: int = SR_MIC,
    n: int = BLOCK,
) -> np.ndarray:
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    shape = (1.0 / np.maximum(freqs, 40.0) ** 1.1) + 0.45 * np.exp(
        -0.5 * ((freqs - 3800.0) / 1200.0) ** 2
    )
    w = np.fft.rfft(rng.normal(0.0, 1.0, n))
    b = np.fft.irfft(w * shape, n=n)
    b = b / (np.std(b) + 1e-9) * rms
    return np.clip(b, -32767, 32767).astype(np.int16)


def _synth_sigh_formant_noise(
    rng: np.random.Generator,
    rms: float = 750.0,
    sr: int = SR_MIC,
    n: int = BLOCK,
) -> np.ndarray:
    """Whispery/aspirated sigh inside 400-2600 Hz with NO vocal-fold pitch."""
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    shape = np.exp(-0.5 * ((freqs - 900.0) / 450.0) ** 2) + 0.6 * np.exp(
        -0.5 * ((freqs - 2100.0) / 600.0) ** 2
    )
    w = np.fft.rfft(rng.normal(0.0, 1.0, n))
    s = np.fft.irfft(w * shape, n=n)
    s = s / (np.std(s) + 1e-9) * rms
    return np.clip(s, -32767, 32767).astype(np.int16)


class TestSpeechBandLevel:
    def test_ignores_low_frequency_mic_wind_puff(self):
        rng = np.random.default_rng(7)
        freqs = np.fft.rfftfreq(BLOCK, 1.0 / SR_MIC)
        puff = np.fft.irfft(
            np.fft.rfft(rng.normal(0.0, 1.0, BLOCK)) * ((freqs >= 30) & (freqs <= 190)),
            n=BLOCK,
        )
        puff = (puff / np.std(puff) * 900.0).astype(np.int16)
        assert speech_band_level(puff, SR_MIC) < 0.03

    def test_ignores_high_frequency_hiss(self):
        rng = np.random.default_rng(8)
        freqs = np.fft.rfftfreq(BLOCK, 1.0 / SR_MIC)
        hiss = np.fft.irfft(
            np.fft.rfft(rng.normal(0.0, 1.0, BLOCK)) * (freqs >= 3900),
            n=BLOCK,
        )
        hiss = (hiss / np.std(hiss) * 900.0).astype(np.int16)
        assert speech_band_level(hiss, SR_MIC) < 0.03

    def test_detects_speech_formant_energy(self):
        voice = _synth_voice(135, 140, [(1.0, 550, 180), (0.8, 1600, 260)], rms=750.0)
        lvl = speech_band_level(voice, SR_MIC)
        assert 0.20 <= lvl <= 0.40


class TestVoicedSpeechClassifier:
    def test_rejects_breaths_and_sighs_across_volumes(self):
        rng = np.random.default_rng(101)
        # Across 120 simulated 4-block breaths/sighs from quiet (180) to loud (1500),
        # zero 4-block streaks may pass as voiced speech.
        for rms in (180.0, 400.0, 800.0, 1500.0):
            for _ in range(30):
                streak = all(
                    is_voiced_speech(_synth_breath(rng, rms=rms), SR_MIC)
                    for _ in range(4)
                )
                assert not streak
                sigh_streak = all(
                    is_voiced_speech(_synth_sigh_formant_noise(rng, rms=rms), SR_MIC)
                    for _ in range(4)
                )
                assert not sigh_streak

    def test_rejects_keyboard_clicks_and_mains_hum(self):
        rng = np.random.default_rng(202)
        t = np.arange(BLOCK) / SR_MIC
        hum = (
            600.0 * np.sin(2 * np.pi * 60 * t)
            + 350.0 * np.sin(2 * np.pi * 120 * t)
            + rng.normal(0, 35, BLOCK)
        ).astype(np.int16)
        assert is_voiced_speech(hum, SR_MIC) is False

        click = rng.normal(0, 35, BLOCK)
        click[200:228] += rng.normal(0, 4500, 28)
        click = np.clip(click, -32767, 32767).astype(np.int16)
        assert is_voiced_speech(click, SR_MIC) is False

    @pytest.mark.parametrize(
        "f0s,f0e,formants,rms",
        [
            (115, 118, [(1.0, 500, 160), (0.8, 1450, 220), (0.4, 2500, 300)], 650.0),
            (92, 104, [(0.6, 110, 70), (1.0, 480, 170), (0.75, 1350, 250)], 650.0),
            (210, 214, [(1.0, 680, 200), (0.85, 1950, 300), (0.4, 2850, 350)], 650.0),
            (195, 235, [(1.0, 650, 200), (0.8, 1800, 300), (0.4, 2750, 380)], 650.0),
            (145, 152, [(1.0, 550, 180), (0.7, 1600, 250)], 460.0),
        ],
    )
    def test_accepts_diverse_human_voices(self, f0s, f0e, formants, rms):
        rng = np.random.default_rng(303)
        pcm = _synth_voice(f0s, f0e, formants, rms=rms, rng=rng, noise_rms=55.0)
        assert is_voiced_speech(pcm, SR_MIC) is True


class TestEchoGuardBargeIn:
    def test_headphones_rejects_breathing_accepts_real_speech(self):
        rng = np.random.default_rng(404)
        guard = EchoGuard()
        need = guard.required_blocks
        assert need >= 4

        # Loud close-mic breaths never sustain user-speech detection
        consec = 0
        for _ in range(40):
            b = _synth_breath(rng, rms=950.0)
            if guard.is_user_speech(b, SR_MIC):
                consec += 1
            else:
                consec = 0
            assert consec < need

        # Real spoken words trigger within `need` blocks
        consec = 0
        for _ in range(need):
            v = _synth_voice(
                130, 136, [(1.0, 520, 170), (0.8, 1550, 240)], rms=650.0, rng=rng
            )
            if guard.is_user_speech(v, SR_MIC):
                consec += 1
        assert consec >= need

    def test_loudspeaker_echo_plus_breath_rejected_real_voice_accepted(self):
        rng = np.random.default_rng(505)
        guard = EchoGuard()
        t0 = 100.0

        # JARVIS speaking at 24 kHz through speakers; 14% leaks back into 16 kHz mic
        jarvis_24k = _synth_voice(
            130, 132, [(1.0, 600, 220)], rms=1800.0, sr=SR_SPK, n=int(0.192 * SR_SPK)
        )
        jarvis_echo_16k = _synth_voice(
            130, 132, [(1.0, 600, 220)], rms=252.0, sr=SR_MIC, n=BLOCK
        )

        # Calibrate over 10 blocks of pure speaker echo
        for i in range(10):
            ts = t0 + i * 0.064
            guard.note_output(jarvis_24k, SR_SPK, 0.68, when=ts)
            assert guard.is_user_speech(jarvis_echo_16k, SR_MIC, when=ts + 0.02) is False

        # Now user breathes / sighs loudly while JARVIS echo continues -> 0 interrupts
        need = guard.required_blocks
        consec = 0
        for i in range(40):
            ts = t0 + (10 + i) * 0.064
            guard.note_output(jarvis_24k, SR_SPK, 0.68, when=ts)
            mic = np.clip(
                jarvis_echo_16k.astype(np.int32)
                + _synth_breath(rng, rms=500.0).astype(np.int32),
                -32767,
                32767,
            ).astype(np.int16)
            if guard.is_user_speech(mic, SR_MIC, when=ts + 0.02):
                consec += 1
            else:
                consec = 0
            assert consec < need

        # Now user actually speaks over JARVIS (even a male voice close in pitch!) -> interrupts!
        for f0s, f0e, fms in [
            (115, 118, [(1.0, 500, 150), (0.8, 1450, 220), (0.4, 2500, 300)]),
            (205, 220, [(1.0, 660, 200), (0.85, 1850, 280), (0.4, 2800, 350)]),
        ]:
            consec = 0
            for i in range(need):
                ts = t0 + (60 + i) * 0.064
                guard.note_output(jarvis_24k, SR_SPK, 0.68, when=ts)
                user_v = _synth_voice(f0s, f0e, fms, rms=680.0, rng=rng)
                mic = np.clip(
                    jarvis_echo_16k.astype(np.int32) + user_v.astype(np.int32),
                    -32767,
                    32767,
                ).astype(np.int16)
                if guard.is_user_speech(mic, SR_MIC, when=ts + 0.02):
                    consec += 1
            assert consec >= need


class TestMainBargeInWiring:
    def test_no_raw_level_bypass_and_respects_barge_toggle(self):
        src = (Path(__file__).resolve().parent.parent / "main.py").read_text(
            encoding="utf-8"
        )
        assert "if lvl > 0.16:" not in src
        assert "interrupt forced ON" not in src
        assert "_barge_preroll" in src
        assert "speech_band_level(indata, SEND_SAMPLE_RATE)" in src
