"""
edge-tts backend.

  Primary:  edge-tts  — free, natural Korean voices, no VRAM, needs internet
            (ko-KR-SunHiNeural / ko-KR-InJoonNeural)
  Fallback: pyttsx3   — fully offline Windows SAPI, used when edge-tts fails

Text is sent to Microsoft's servers. Use the `qwen` backend if everything has
to stay on the machine.
"""
from __future__ import annotations

import asyncio
import os
import tempfile

import numpy as np
import soundfile as sf

from core.tts import TTSBackend


class EdgeTTS(TTSBackend):
    def __init__(self, config: dict):
        cfg = config.get("tts", {})
        sub = cfg.get("edge", {})
        # Fall back to the flat layout used before backends were introduced.
        self.voice = sub.get("voice", cfg.get("voice", "ko-KR-SunHiNeural"))
        self.speed = sub.get("speed", cfg.get("speed", "+0%"))

        self._has_edge = self._probe_edge_tts()
        backend = "edge-tts" if self._has_edge else "pyttsx3 (offline)"
        print(f"[TTS] {backend}, voice: {self.voice}")

    @staticmethod
    def _probe_edge_tts() -> bool:
        try:
            import edge_tts  # noqa: F401
            return True
        except ImportError:
            return False

    def synthesize(self, text: str) -> tuple[np.ndarray, int] | None:
        if not text or not text.strip():
            return None

        if self._has_edge:
            try:
                return asyncio.run(self._synth_edge(text))
            except Exception as e:
                print(f"[TTS] edge-tts failed: {e} - falling back to pyttsx3")

        return self._synth_pyttsx3(text)

    async def _synth_edge(self, text: str) -> tuple[np.ndarray, int]:
        import edge_tts
        communicate = edge_tts.Communicate(text, self.voice, rate=self.speed)
        path = _tempfile(".mp3")
        try:
            await communicate.save(path)
            return _read_mono(path)
        finally:
            _unlink(path)

    def _synth_pyttsx3(self, text: str) -> tuple[np.ndarray, int] | None:
        try:
            import pyttsx3
        except ImportError:
            print("[TTS] pyttsx3 not installed; no speech output.")
            return None

        path = _tempfile(".wav")
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 175)
            # Prefer a Korean SAPI voice when one is installed.
            for v in engine.getProperty("voices"):
                name = (v.name or "").lower()
                if "korean" in name or "heami" in name or "ko-kr" in name:
                    engine.setProperty("voice", v.id)
                    break
            engine.save_to_file(text, path)
            engine.runAndWait()
            if not os.path.exists(path) or os.path.getsize(path) == 0:
                return None
            return _read_mono(path)
        except Exception as e:
            print(f"[TTS] pyttsx3 error: {e}")
            return None
        finally:
            _unlink(path)


# ── helpers ──────────────────────────────────────────────────────────

def _tempfile(suffix: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        return f.name


def _unlink(path: str) -> None:
    try:
        os.unlink(path)
    except OSError:
        pass


def _read_mono(path: str) -> tuple[np.ndarray, int]:
    data, rate = sf.read(path, dtype="float32")
    if data.ndim > 1:
        data = data.mean(axis=1)
    return data.astype(np.float32), int(rate)
