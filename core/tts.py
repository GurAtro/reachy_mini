"""
Text-to-Speech backend selection.

Every backend exposes the same surface:

    backend.synthesize(text) -> (float32 mono samples, samplerate) | None
    backend.speak(text, audio_source=None)

Synthesis returns PCM rather than playing directly, so the caller decides where
it goes - the PC speaker or the robot's speaker.

Pick with `tts.backend` in config.yaml:
    edge — edge-tts, no VRAM, natural Korean voices, needs internet
    qwen — Qwen3-TTS, local, voice cloning from a 3-second clip, offline
"""
from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class TTSBackend(ABC):
    """Shared playback logic; backends only implement synthesize()."""

    @abstractmethod
    def synthesize(self, text: str) -> tuple[np.ndarray, int] | None:
        """Render `text` to (float32 mono samples, samplerate). None on failure."""

    def speak(self, text: str, audio_source=None) -> None:
        if not text or not text.strip():
            return
        result = self.synthesize(text)
        if result is None:
            print(f"[TTS] (silent) {text}")
            return
        samples, rate = result
        if audio_source is not None:
            audio_source.play(samples, rate)
        else:
            import sounddevice as sd
            sd.play(samples, rate)
            sd.wait()


def create_tts(config: dict) -> TTSBackend:
    cfg = config.get("tts", {})
    backend = cfg.get("backend", "edge").lower()

    if backend == "edge":
        from core.tts_edge import EdgeTTS
        return EdgeTTS(config)

    if backend == "qwen":
        from core.tts_qwen import QwenTTS
        return QwenTTS(config)

    raise ValueError(
        f"Unknown tts.backend: {backend!r} (expected 'edge' or 'qwen')"
    )


# ── shared helpers ───────────────────────────────────────────────────

def to_mono_float32(data) -> np.ndarray:
    """Normalise torch tensors / stereo arrays to a 1-D float32 array."""
    if hasattr(data, "detach"):          # torch.Tensor
        data = data.detach().cpu().numpy()
    arr = np.asarray(data, dtype=np.float32)
    if arr.ndim > 1:
        # (channels, n) or (n, channels) - collapse the smaller axis
        arr = arr.mean(axis=0) if arr.shape[0] < arr.shape[1] else arr.mean(axis=1)
    return arr
