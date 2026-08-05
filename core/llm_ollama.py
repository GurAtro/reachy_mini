"""
Ollama backend — local model, fully offline, but it costs VRAM.

Budget check on an 8 GB card:
    exaone3.5:7.8b (Q4) ~4.7 GB  +  Whisper small (int8_float16) ~0.7 GB  ≈ 5.4 GB
That fits, but leaves little headroom; move STT to CPU (`stt.device: cpu`)
if you hit out-of-memory errors, or use the Claude backend instead.
"""
from __future__ import annotations

import ollama

from tools.registry import TOOLS, execute_tool


class OllamaLLM:
    def __init__(self, config: dict):
        llm_cfg = config["llm"]
        cfg = llm_cfg["ollama"]

        self.model = cfg.get("model", "exaone3.5:7.8b")
        self.temperature = float(cfg.get("temperature", 0.7))
        self.max_iterations = int(llm_cfg.get("max_tool_iterations", 5))
        self.system_prompt = llm_cfg["system_prompt"]
        self.client = ollama.Client(host=cfg.get("base_url", "http://localhost:11434"))

        print(f"[LLM] Ollama backend - {self.model}")

    def chat(self, history: list[dict]) -> str:
        messages = [{"role": "system", "content": self.system_prompt}] + list(history)

        for _ in range(self.max_iterations):
            try:
                response = self.client.chat(
                    model=self.model,
                    messages=messages,
                    tools=TOOLS,
                    options={"temperature": self.temperature},
                )
            except Exception as e:
                print(f"[LLM] Ollama error: {e}")
                return "로컬 모델에 연결하지 못했어요. Ollama가 실행 중인지 확인해 주세요."

            msg = response.message

            if not msg.tool_calls:
                return (msg.content or "").strip() or "..."

            messages.append(msg)
            for call in msg.tool_calls:
                name = call.function.name
                args = call.function.arguments or {}
                print(f"[LLM] tool: {name}({args})")
                output = execute_tool(name, dict(args))
                print(f"[LLM] result: {output}")
                messages.append({
                    "role": "tool",
                    "tool_name": name,   # lets the model match result to call
                    "content": str(output),
                })

        print(f"[LLM] Hit the {self.max_iterations}-iteration tool limit.")
        return "작업이 생각보다 복잡해서 도중에 멈췄어요. 조금 더 구체적으로 말씀해 주시겠어요?"
