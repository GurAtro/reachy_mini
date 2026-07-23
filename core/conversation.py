"""
Conversation history manager
"""


class ConversationManager:
    def __init__(self, max_turns: int = 20):
        self.history: list[dict] = []
        self.max_turns = max_turns  # max user+assistant pairs to keep

    def add_user(self, text: str):
        self.history.append({"role": "user", "content": text})
        self._trim()

    def add_assistant(self, text: str):
        self.history.append({"role": "assistant", "content": text})

    def get_messages(self) -> list[dict]:
        return list(self.history)

    def _trim(self):
        """Keep only the last max_turns pairs to avoid context overflow."""
        max_messages = self.max_turns * 2
        if len(self.history) > max_messages:
            self.history = self.history[-max_messages:]

    def clear(self):
        self.history.clear()
        print("[Conversation] History cleared.")
