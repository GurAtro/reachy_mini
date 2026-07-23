"""
Text-to-Speech
  Primary:  edge-tts (Microsoft Edge TTS, free, very natural English voices)
  Fallback: pyttsx3 (fully offline, Windows SAPI voices)
"""
import asyncio
import io
import tempfile
import os
import sounddevice as sd
import soundfile as sf


class TextToSpeech:
    def __init__(self, config: dict):
        tts_cfg = config["tts"]
        self.voice = tts_cfg.get("voice", "en-US-JennyNeural")  # natural female
        self.speed = tts_cfg.get("speed", "+0%")                # e.g. "+10%" to speed up
        self._has_edge_tts = self._check_edge_tts()
        backend = "edge-tts" if self._has_edge_tts else "pyttsx3 (offline)"
        print(f"[TTS] Ready — using {backend}, voice: {self.voice}")

    def _check_edge_tts(self) -> bool:
        try:
            import edge_tts
            return True
        except ImportError:
            return False

    def speak(self, text: str):
        if not text:
            return
        print(f"[TTS] Reachy: {text}")
        if self._has_edge_tts:
            try:
                asyncio.run(self._speak_edge(text))
                return
            except Exception as e:
                print(f"[TTS] edge-tts error: {e} — falling back to pyttsx3")
        self._speak_pyttsx3(text)

    async def _speak_edge(self, text: str):
        import edge_tts
        communicate = edge_tts.Communicate(text, self.voice, rate=self.speed)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tmp_path = f.name
        try:
            await communicate.save(tmp_path)
            data, samplerate = sf.read(tmp_path)
            sd.play(data, samplerate)
            sd.wait()
        finally:
            os.unlink(tmp_path)

    def _speak_pyttsx3(self, text: str):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", 175)
            voices = engine.getProperty("voices")
            for v in voices:
                if "zira" in v.name.lower() or "david" in v.name.lower() or "jenny" in v.name.lower():
                    engine.setProperty("voice", v.id)
                    break
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"[TTS] pyttsx3 error: {e}")
