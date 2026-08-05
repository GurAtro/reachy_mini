"""
Audio I/O abstraction.

Two interchangeable sources:
  LocalAudio  — this PC's microphone + speaker (development, no robot needed)
  ReachyAudio — the robot's 4-mic array + 5W speaker via `mini.media`

Everything downstream (STT, TTS) works with float32 mono numpy arrays, so the
rest of the app never needs to know which source is active.
"""
from __future__ import annotations

import time
from abc import ABC, abstractmethod

import numpy as np

INT16_MAX = 32768.0


def _resample(samples: np.ndarray, src_rate: int, dst_rate: int) -> np.ndarray:
    """Resample a mono float32 signal. Uses scipy when available."""
    if src_rate == dst_rate or samples.size == 0:
        return samples
    n_out = int(round(len(samples) * dst_rate / src_rate))
    try:
        from scipy.signal import resample
        return resample(samples, n_out).astype(np.float32)
    except ImportError:
        # Linear interpolation fallback — lower quality but dependency-free.
        src_idx = np.linspace(0, len(samples) - 1, num=n_out, dtype=np.float64)
        return np.interp(src_idx, np.arange(len(samples)), samples).astype(np.float32)


class AudioSource(ABC):
    """Microphone in, speaker out."""

    input_samplerate: int = 16000

    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def read(self) -> np.ndarray:
        """Return the next chunk of microphone audio as float32 mono (may be empty)."""

    @abstractmethod
    def play(self, samples: np.ndarray, samplerate: int) -> None:
        """Play float32 mono audio, blocking until playback finishes."""


class LocalAudio(AudioSource):
    """PC microphone (pyaudio) and speaker (sounddevice)."""

    CHUNK = 1024

    def __init__(self, config: dict):
        self.input_samplerate = int(config["audio"]["sample_rate"])
        self._pa = None
        self._stream = None

    def start(self):
        import pyaudio
        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.input_samplerate,
            input=True,
            frames_per_buffer=self.CHUNK,
        )

    def stop(self):
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        if self._pa is not None:
            self._pa.terminate()
            self._pa = None

    def read(self) -> np.ndarray:
        data = self._stream.read(self.CHUNK, exception_on_overflow=False)
        return np.frombuffer(data, dtype=np.int16).astype(np.float32) / INT16_MAX

    def play(self, samples: np.ndarray, samplerate: int):
        import sounddevice as sd
        sd.play(samples, samplerate)
        sd.wait()


class ReachyAudio(AudioSource):
    """Robot 4-mic array and speaker through the Reachy Mini media backend.

    `get_audio_sample()` returns float32 (samples, channels); `push_audio_sample()`
    is non-blocking, so `play()` sleeps for the clip's duration.
    """

    def __init__(self, config: dict, robot):
        if not robot.connected:
            raise RuntimeError(
                "audio.source is 'reachy' but the robot is not connected. "
                "Set reachy.enabled: true, or switch audio.source to 'local'."
            )
        self._media = robot.media
        self._started = False
        self.input_samplerate = int(config["audio"]["sample_rate"])
        self.output_samplerate = self.input_samplerate

    def start(self):
        self._media.start_recording()
        self._media.start_playing()
        self._started = True
        # Trust the device's reported rates over the config values.
        try:
            self.input_samplerate = int(self._media.get_input_audio_samplerate())
            self.output_samplerate = int(self._media.get_output_audio_samplerate())
        except Exception:
            pass
        print(f"[Audio] Reachy mics @ {self.input_samplerate} Hz, "
              f"speaker @ {self.output_samplerate} Hz")

    def stop(self):
        if not self._started:
            return
        try:
            self._media.stop_recording()
            self._media.stop_playing()
        finally:
            self._started = False

    def read(self) -> np.ndarray:
        samples = self._media.get_audio_sample()
        if samples is None or len(samples) == 0:
            time.sleep(0.01)
            return np.empty(0, dtype=np.float32)
        arr = np.asarray(samples, dtype=np.float32)
        if arr.ndim > 1:                       # (n, channels) -> mono
            arr = arr.mean(axis=1)
        return arr

    def play(self, samples: np.ndarray, samplerate: int):
        audio = _resample(samples, samplerate, self.output_samplerate)
        audio = np.clip(audio, -1.0, 1.0).astype(np.float32).reshape(-1, 1)
        self._media.push_audio_sample(audio)
        # push_audio_sample returns immediately; wait out the clip.
        time.sleep(len(audio) / float(self.output_samplerate))

    def speech_detected(self) -> bool:
        """Built-in VAD from the mic array's direction-of-arrival estimator."""
        try:
            _doa, is_speech = self._media.get_DoA()
            return bool(is_speech)
        except Exception:
            return False


def create_audio_source(config: dict, robot) -> AudioSource:
    kind = config["audio"].get("source", "local")
    if kind == "reachy":
        return ReachyAudio(config, robot)
    if kind == "local":
        return LocalAudio(config)
    raise ValueError(f"Unknown audio.source: {kind!r} (expected 'local' or 'reachy')")


def record_utterance(source: AudioSource, config: dict) -> np.ndarray | None:
    """Record until the speaker goes quiet. Returns float32 mono, or None.

    Energy-based VAD: start capturing on the first chunk above the threshold,
    stop after `silence_duration` seconds of continuous silence.

    Returns None when nobody spoke within `idle_timeout` seconds, so the caller
    keeps control instead of blocking forever on a silent room. Set
    `idle_timeout: 0` to wait indefinitely.
    """
    cfg = config["audio"]
    threshold = float(cfg["silence_threshold"]) / INT16_MAX
    rate = source.input_samplerate

    silence_limit = int(float(cfg["silence_duration"]) * rate)
    max_samples = int(float(cfg.get("max_record_seconds", 30)) * rate)
    idle_timeout = float(cfg.get("idle_timeout", 30))
    idle_limit = int(idle_timeout * rate) if idle_timeout > 0 else 0

    frames: list[np.ndarray] = []
    speaking = False
    silent_samples = 0     # consecutive silence once speech started
    spoken_samples = 0     # audio actually captured
    idle_samples = 0       # audio heard before speech started

    print("[Audio] Listening...")
    while True:
        chunk = source.read()
        if chunk.size == 0:
            continue

        loud = float(np.abs(chunk).mean()) >= threshold

        if not speaking:
            if loud:
                speaking = True
                silent_samples = 0
            else:
                idle_samples += chunk.size
                # Nobody is talking - hand control back so the caller can
                # re-pose the robot, check for interrupts, and come back.
                if idle_limit and idle_samples >= idle_limit:
                    return None
                continue

        if loud:
            silent_samples = 0
        else:
            silent_samples += chunk.size

        frames.append(chunk)
        spoken_samples += chunk.size

        if silent_samples >= silence_limit:
            break
        if spoken_samples >= max_samples:
            print("[Audio] Max recording length reached.")
            break

    if not frames:
        return None
    return np.concatenate(frames)
