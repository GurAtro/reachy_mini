"""
LLM backend selection.

Both backends expose the same surface:

    backend.chat(history) -> str

where `history` is a plain [{"role": "user"|"assistant", "content": str}] list.
Tool calling is resolved inside `chat`, so the caller only ever sees text.

Pick with `llm.backend` in config.yaml:
    claude — Claude API, no VRAM, best Korean quality, needs internet
    ollama — local model, works offline, costs VRAM
"""
from __future__ import annotations


def create_llm(config: dict):
    backend = config["llm"].get("backend", "claude").lower()

    if backend == "claude":
        from core.llm_claude import ClaudeLLM
        return ClaudeLLM(config)

    if backend == "ollama":
        from core.llm_ollama import OllamaLLM
        return OllamaLLM(config)

    raise ValueError(
        f"Unknown llm.backend: {backend!r} (expected 'claude' or 'ollama')"
    )
