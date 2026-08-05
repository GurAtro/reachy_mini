"""
Qwen3-TTS backend — local, offline, supports 3-second voice cloning.

Two generation modes, chosen by config:
  * `ref_audio` + `ref_text` set  -> generate_voice_clone (Base models)
  * `speaker` set                 -> generate_custom_voice (CustomVoice models)

Model sizes (weights):
    Qwen3-TTS-12Hz-0.6B-Base   ~0.9 GB
    Qwen3-TTS-12Hz-1.7B-Base   ~3.4 GB
Either fits an 8 GB card alongside Whisper with room to spare.

Install:
    pip install -U qwen-tts
    pip install -U flash-attn --no-build-isolation   # optional, faster
"""
from __future__ import annotations

import numpy as np

from core.tts import TTSBackend, to_mono_float32

_DTYPES = {"bfloat16": "bfloat16", "float16": "float16", "float32": "float32"}


class QwenTTS(TTSBackend):
    def __init__(self, config: dict):
        cfg = config.get("tts", {}).get("qwen", {})

        self.model_id = cfg.get("model", "Qwen/Qwen3-TTS-12Hz-0.6B-Base")
        self.language = cfg.get("language", "Korean")
        self.ref_audio = (cfg.get("ref_audio") or "").strip()
        self.ref_text = (cfg.get("ref_text") or "").strip()
        self.speaker = (cfg.get("speaker") or "").strip()

        if self.ref_audio and not self.ref_text:
            raise ValueError(
                "tts.qwen.ref_audio is set but ref_text is empty. "
                "Voice cloning needs the transcript of the reference clip."
            )
        if not self.ref_audio and not self.speaker:
            raise ValueError(
                "Configure either tts.qwen.ref_audio + ref_text (voice cloning, "
                "Base models) or tts.qwen.speaker (preset voice, CustomVoice models)."
            )

        self.mode = "clone" if self.ref_audio else "preset"
        self._load(cfg)

    def _load(self, cfg: dict):
        try:
            import torch
            from qwen_tts import Qwen3TTSModel
        except ImportError as e:
            raise RuntimeError(
                f"Qwen3-TTS backend needs `qwen-tts` and `torch` ({e}). "
                "Install with: pip install -U qwen-tts"
            ) from e

        dtype_name = _DTYPES.get(cfg.get("dtype", "bfloat16"), "bfloat16")
        kwargs = {
            "device_map": cfg.get("device", "cuda:0"),
            "dtype": getattr(torch, dtype_name),
        }
        # Only pass flash attention when explicitly requested - it needs a
        # separate install and errors out if missing.
        attn = (cfg.get("attn_implementation") or "").strip()
        if attn:
            kwargs["attn_implementation"] = attn

        print(f"[TTS] Loading {self.model_id} ({dtype_name}, {kwargs['device_map']})...")
        self.model = Qwen3TTSModel.from_pretrained(self.model_id, **kwargs)

        detail = f"clone from {self.ref_audio}" if self.mode == "clone" \
            else f"speaker={self.speaker}"
        print(f"[TTS] Qwen3-TTS ready - {self.language}, {detail}")

    def synthesize(self, text: str) -> tuple[np.ndarray, int] | None:
        if not text or not text.strip():
            return None
        try:
            if self.mode == "clone":
                wavs, sr = self.model.generate_voice_clone(
                    text=text,
                    language=self.language,
                    ref_audio=self.ref_audio,
                    ref_text=self.ref_text,
                )
            else:
                wavs, sr = self.model.generate_custom_voice(
                    text=text,
                    language=self.language,
                    speaker=self.speaker,
                )
        except Exception as e:
            print(f"[TTS] Qwen3-TTS generation failed: {e}")
            return None

        if wavs is None or len(wavs) == 0:
            return None
        return to_mono_float32(wavs[0]), int(sr)
