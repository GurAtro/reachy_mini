"""
Speech-to-Text using faster-whisper (local, English optimized)
"""
import io
import numpy as np
import pyaudio
import time
import yaml
from faster_whisper import WhisperModel


def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)


class SpeechToText:
    def __init__(self, config: dict):
        self.config = config
        stt_cfg = config["stt"]
        audio_cfg = config["audio"]

        print(f"[STT] Loading Whisper model '{stt_cfg['model']}'...")
        self.model = WhisperModel(
            stt_cfg["model"],
            device=stt_cfg["device"],
            compute_type="int8"
        )
        self.language = stt_cfg["language"]
        self.sample_rate = audio_cfg["sample_rate"]
        self.silence_threshold = audio_cfg["silence_threshold"]
        self.silence_duration = audio_cfg["silence_duration"]
        print("[STT] Ready.")

    def _is_silent(self, data: bytes) -> bool:
        audio_data = np.frombuffer(data, dtype=np.int16)
        return np.abs(audio_data).mean() < self.silence_threshold

    def listen(self) -> str | None:
        """Record audio until silence, then transcribe."""
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=1024
        )

        print("[STT] Listening... (speak now)")
        frames = []
        silent_chunks = 0
        speaking = False
        silence_limit = int(self.silence_duration * self.sample_rate / 1024)

        try:
            while True:
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)

                if self._is_silent(data):
                    if speaking:
                        silent_chunks += 1
                        if silent_chunks >= silence_limit:
                            break
                else:
                    speaking = True
                    silent_chunks = 0

                # Max 30 seconds
                if len(frames) > (30 * self.sample_rate // 1024):
                    break
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()

        if not speaking:
            return None

        # Convert to numpy array for whisper
        audio_bytes = b"".join(frames)
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        print("[STT] Transcribing...")
        segments, _ = self.model.transcribe(
            audio_np,
            language=self.language,
            beam_size=5,
            vad_filter=True
        )
        text = " ".join(seg.text.strip() for seg in segments).strip()
        if text:
            print(f"[STT] You said: {text}")
        return text or None
