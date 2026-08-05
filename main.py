"""
Reachy Mini AI Assistant — entry point.

    python main.py

음성 명령 예시:
    "유튜브 열어줘"          "유튜브에서 로파이 음악 찾아줘"
    "C드라이브 남은 용량 알려줘"   "CPU 사용률 어때?"
    "메모장 열어줘"          "스크린샷 찍어줘"
    "초기화" / "리셋"        — 대화 기록을 지웁니다
    "종료" / "그만"          — 프로그램을 끝냅니다

하드웨어 없이 실행하려면 config.yaml에서 `reachy.enabled: false`(기본값)로
두세요. 로봇 동작은 콘솔에 출력됩니다.
"""
from __future__ import annotations

import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Korean Windows consoles default to cp949, which cannot encode characters
# outside that codepage; force UTF-8 so log output never crashes the app.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

QUIT_WORDS = {"종료", "그만", "잘가", "안녕히", "바이",
              "quit", "exit", "goodbye", "bye"}
CLEAR_WORDS = {"초기화", "리셋", "기억 지워", "다 잊어",
               "clear", "reset", "forget everything"}

GREETING = "안녕하세요, 리치입니다. 무엇을 도와드릴까요?"
FAREWELL = "안녕히 계세요. 좋은 하루 보내세요!"


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize(text: str) -> str:
    """Lowercase and strip trailing punctuation so command words still match."""
    return text.lower().strip().rstrip(".!?~ ")


def main() -> int:
    print("=" * 52)
    print("  Reachy Mini AI Assistant")
    print("=" * 52)

    config = load_config()

    from core.audio import create_audio_source, record_utterance
    from core.conversation import ConversationManager
    from core.llm import create_llm
    from core.stt import SpeechToText
    from core.tts import TextToSpeech
    from reachy.robot import Robot

    robot = Robot(config)

    try:
        audio = create_audio_source(config, robot)
    except RuntimeError as e:
        print(f"[Audio] {e}")
        robot.disconnect()
        return 1

    stt = SpeechToText(config)
    tts = TextToSpeech(config)
    llm = create_llm(config)
    conversation = ConversationManager()

    audio.start()
    robot.idle()
    tts.speak(GREETING, audio)
    print("\n[System] 말을 걸어 보세요. '종료'라고 하면 끝납니다.\n")

    try:
        while True:
            try:
                robot.listening()
                clip = record_utterance(audio, config)
                if clip is None:
                    continue

                text = stt.transcribe(clip, audio.input_samplerate)
                if not text:
                    continue
                print(f"[You] {text}")

                command = normalize(text)
                if command in QUIT_WORDS:
                    tts.speak(FAREWELL, audio)
                    break
                if command in CLEAR_WORDS:
                    conversation.clear()
                    tts.speak("네, 대화 기록을 지웠어요.", audio)
                    continue

                conversation.add_user(text)
                robot.speaking()
                reply = llm.chat(conversation.get_messages())
                conversation.add_assistant(reply)

                print(f"[Reachy] {reply}")
                tts.speak(reply, audio)
                robot.nod()

            except KeyboardInterrupt:
                print("\n[System] 사용자 중단.")
                break
            except Exception as e:
                print(f"[Error] {e}")
                robot.confused()
                tts.speak("죄송해요, 문제가 생겼어요. 다시 말씀해 주세요.", audio)
    finally:
        audio.stop()
        robot.disconnect()
        print("[System] 종료합니다.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
