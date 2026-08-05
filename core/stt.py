"""
Speech-to-Text with faster-whisper.

Pure transcription — recording lives in core/audio.py so the same model works
with either the PC microphone or the robot's mic array.

VRAM (approximate, int8_float16 on CUDA):
    small ~0.7 GB   medium ~1.6 GB   large-v3 ~3.1 GB
With the Claude backend the LLM uses no VRAM, so "small" or "medium" fit
comfortably inside an 8 GB card alongside anything else you run.
"""
from __future__ import annotations

import numpy as np
from faster_whisper import WhisperModel

from core.audio import _resample

WHISPER_RATE = 16000


class SpeechToText:
    def __init__(self, config: dict):
        cfg = config["stt"]
        self.language = cfg.get("language", "ko")
        self.beam_size = int(cfg.get("beam_size", 5))
        name = cfg.get("model", "small")

        device = cfg.get("device", "auto")
        compute_type = cfg.get("compute_type", "auto")

        print(f"[STT] Loading Whisper '{name}' (device={device})...")
        self.model, self.device = self._load(name, device, compute_type)
        print(f"[STT] Ready on {self.device}, language={self.language}.")

    @staticmethod
    def _load(name: str, device: str, compute_type: str):
        """Load the model, preferring CUDA when device is 'auto'."""
        def build(dev: str):
            ct = compute_type
            if ct == "auto":
                ct = "int8_float16" if dev == "cuda" else "int8"
            return WhisperModel(name, device=dev, compute_type=ct), dev

        if device == "auto":
            try:
                return build("cuda")
            except Exception as e:
                print(f"[STT] CUDA unavailable ({e}). Using CPU.")
                return build("cpu")
        return build(device)

    def transcribe(self, audio: np.ndarray, samplerate: int = WHISPER_RATE) -> str | None:
        """Transcribe float32 mono audio. Returns None when nothing was said."""
        if audio is None or audio.size == 0:
            return None

        if samplerate != WHISPER_RATE:
            audio = _resample(audio, samplerate, WHISPER_RATE)

        segments, _info = self.model.transcribe(
            audio.astype(np.float32),
            language=self.language,
            beam_size=self.beam_size,
            vad_filter=True,
        )
        text = " ".join(seg.text.strip() for seg in segments).strip()
        return text or None
