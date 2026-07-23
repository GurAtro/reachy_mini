"""
Reachy Mini AI Assistant — Main entry point
Run: python main.py

Voice commands (examples):
  "Open YouTube"
  "Search YouTube for lo-fi music"
  "How much space is left on my C drive?"
  "What's my CPU usage?"
  "Open notepad"
  "Shut down the computer"
  "Take a screenshot"
  "Clear" / "Reset" — clears conversation history
  "Quit" / "Exit" — exits the program
"""
import sys
import os
import yaml

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(__file__))


def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    print("=" * 50)
    print("  Reachy Mini AI Assistant")
    print("=" * 50)

    config = load_config()

    # Initialize components
    from core.stt import SpeechToText
    from core.tts import TextToSpeech
    from core.llm import LLM
    from core.conversation import ConversationManager
    from reachy.robot import ReachyMini

    stt = SpeechToText(config)
    tts = TextToSpeech(config)
    llm = LLM(config)
    conversation = ConversationManager()
    robot = ReachyMini(config)

    tts.speak("Hello! I'm Reachy, your AI assistant. How can I help you today?")

    print("\n[System] Say something to Reachy. Say 'quit' to exit.\n")

    while True:
        try:
            robot.listening_pose()
            user_text = stt.listen()

            if not user_text:
                continue

            # Handle control commands
            lower = user_text.lower().strip()
            if lower in ("quit", "exit", "goodbye", "bye"):
                tts.speak("Goodbye! Have a great day!")
                robot.idle()
                break

            if lower in ("clear", "reset", "forget everything"):
                conversation.clear()
                tts.speak("Got it, I've cleared our conversation history.")
                continue

            # Send to LLM
            conversation.add_user(user_text)
            robot.speaking_pose()

            response = llm.chat(conversation.get_messages())
            conversation.add_assistant(response)

            print(f"[Reachy] {response}")
            tts.speak(response)
            robot.nod()

        except KeyboardInterrupt:
            print("\n[System] Interrupted by user.")
            tts.speak("See you later!")
            break
        except Exception as e:
            print(f"[Error] {e}")
            tts.speak("Sorry, I ran into an error. Please try again.")

    robot.disconnect()
    print("[System] Shutting down.")


if __name__ == "__main__":
    main()
