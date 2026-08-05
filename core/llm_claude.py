"""
Claude API backend.

Uses no VRAM at all, which is the whole point on an 8 GB card: the GPU is left
entirely to Whisper. Korean quality and tool-calling reliability are both well
above anything that fits locally alongside STT.

Notes on the request shape (Claude Opus 5):
  * `temperature` / `top_p` / `top_k` are rejected — steer with the prompt.
  * Thinking is on by default. We set it explicitly and control depth with
    `effort` instead of disabling it: with thinking disabled the model can
    emit a tool call as plain text, which would silently never run.
  * `cache_control` on the last system block caches tools + system prompt
    together (tools render before system), so every turn after the first
    re-reads them at ~10% of the input price.
"""
from __future__ import annotations

import os

import anthropic

from tools.registry import ANTHROPIC_TOOLS, execute_tool

FALLBACK_BETA = "server-side-fallback-2026-07-01"


class ClaudeLLM:
    def __init__(self, config: dict):
        llm_cfg = config["llm"]
        cfg = llm_cfg["claude"]

        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("[LLM] Warning: ANTHROPIC_API_KEY is not set.")

        self.client = anthropic.Anthropic()
        self.model = cfg.get("model", "claude-opus-5")
        self.max_tokens = int(cfg.get("max_tokens", 8192))
        self.effort = cfg.get("effort", "low")
        self.max_iterations = int(llm_cfg.get("max_tool_iterations", 5))
        # Server-side refusal fallback: if a safety classifier declines the
        # request, the API re-runs it on the recommended fallback model in the
        # same call instead of returning nothing.
        self.refusal_fallback = bool(cfg.get("refusal_fallback", True))

        self.system = [{
            "type": "text",
            "text": llm_cfg["system_prompt"],
            "cache_control": {"type": "ephemeral"},
        }]

        print(f"[LLM] Claude backend - {self.model} (effort={self.effort})")

    # ── request helper ───────────────────────────────────────────────

    def _create(self, messages: list[dict]):
        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": self.system,
            "messages": messages,
            "tools": ANTHROPIC_TOOLS,
            "thinking": {"type": "adaptive"},
            # Sent via extra_body so this works regardless of how new the
            # installed SDK is — the field goes straight into the JSON body.
            "extra_body": {"output_config": {"effort": self.effort}},
        }
        if self.refusal_fallback:
            kwargs["extra_body"]["fallbacks"] = "default"
            kwargs["extra_headers"] = {"anthropic-beta": FALLBACK_BETA}

        try:
            return self.client.messages.create(**kwargs)
        except anthropic.BadRequestError as e:
            if self.refusal_fallback and "fallback" in str(e).lower():
                # Older API surface — drop the beta and carry on without it.
                print("[LLM] Refusal fallback unavailable; disabling it.")
                self.refusal_fallback = False
                return self._create(messages)
            raise

    @staticmethod
    def _text_of(response) -> str:
        return "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()

    @staticmethod
    def _log_usage(response):
        u = getattr(response, "usage", None)
        if u is None:
            return
        cached = getattr(u, "cache_read_input_tokens", 0) or 0
        print(f"[LLM] tokens in={u.input_tokens} out={u.output_tokens} cached={cached}")

    # ── main entry point ─────────────────────────────────────────────

    def chat(self, history: list[dict]) -> str:
        """Run one turn, resolving any tool calls, and return the reply text."""
        messages: list[dict] = list(history)

        for _ in range(self.max_iterations):
            try:
                response = self._create(messages)
            except anthropic.RateLimitError:
                return "요청이 몰려서 잠시 처리가 어려워요. 조금 뒤에 다시 말씀해 주세요."
            except anthropic.APIConnectionError:
                return "인터넷 연결이 끊긴 것 같아요. 연결을 확인해 주세요."
            except anthropic.APIStatusError as e:
                print(f"[LLM] API error {e.status_code}: {e.message}")
                return "지금 응답을 만들지 못했어요. 잠시 후 다시 시도해 주세요."

            self._log_usage(response)

            # Safety classifiers can decline — check before reading content.
            if response.stop_reason == "refusal":
                return "그 요청은 제가 도와드리기 어려워요. 다른 걸 도와드릴까요?"

            if response.stop_reason != "tool_use":
                return self._text_of(response) or "..."

            # Keep the assistant turn verbatim: thinking blocks and tool_use
            # blocks must be echoed back unchanged.
            messages.append({"role": "assistant", "content": response.content})

            results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                print(f"[LLM] tool: {block.name}({block.input})")
                output = execute_tool(block.name, dict(block.input))
                print(f"[LLM] result: {output}")
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(output),
                })

            # All tool results go back in a single user message.
            messages.append({"role": "user", "content": results})

        print(f"[LLM] Hit the {self.max_iterations}-iteration tool limit.")
        return "작업이 생각보다 복잡해서 도중에 멈췄어요. 조금 더 구체적으로 말씀해 주시겠어요?"
