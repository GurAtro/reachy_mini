"""
LLM interface via Ollama — supports tool/function calling
"""
import json
import yaml
import ollama
from tools.registry import TOOLS, execute_tool


class LLM:
    def __init__(self, config: dict):
        self.config = config
        llm_cfg = config["llm"]
        self.model = llm_cfg["model"]
        self.temperature = llm_cfg["temperature"]
        self.system_prompt = llm_cfg["system_prompt"]
        self.client = ollama.Client(host=llm_cfg["base_url"])
        print(f"[LLM] Using model: {self.model}")

    def chat(self, messages: list[dict]) -> str:
        """Send messages to LLM, handle tool calls, return final response."""
        full_messages = [
            {"role": "system", "content": self.system_prompt}
        ] + messages

        while True:
            response = self.client.chat(
                model=self.model,
                messages=full_messages,
                tools=TOOLS,
                options={"temperature": self.temperature}
            )

            msg = response.message

            # No tool calls → return text response
            if not msg.tool_calls:
                return msg.content

            # Handle tool calls
            full_messages.append(msg)
            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args = tool_call.function.arguments
                print(f"[LLM] Tool call: {fn_name}({fn_args})")

                result = execute_tool(fn_name, fn_args)
                print(f"[LLM] Tool result: {result}")

                full_messages.append({
                    "role": "tool",
                    "content": str(result)
                })
