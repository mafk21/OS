"""Installer-neutral local voice capability selection and diagnostics."""
from __future__ import annotations
import importlib.util, platform

def snapshot()->dict:
    engines={name: importlib.util.find_spec(module) is not None for name,module in {
        'openwakeword':'openwakeword','faster_whisper':'faster_whisper','moonshine':'moonshine_onnx','kokoro':'kokoro','piper':'piper'}.items()}
    stt='moonshine' if engines['moonshine'] else ('faster_whisper' if engines['faster_whisper'] else 'unavailable')
    tts='kokoro' if engines['kokoro'] else ('piper' if engines['piper'] else 'unavailable')
    return {'platform':platform.system().lower(),'engines':engines,'selected':{'wake':'openwakeword' if engines['openwakeword'] else 'unavailable','stt':stt,'tts':tts},'offline_ready':stt!='unavailable' and tts!='unavailable'}
