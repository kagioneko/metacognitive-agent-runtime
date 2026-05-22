from __future__ import annotations

from typing import Protocol


class LLMClient(Protocol):
    def complete(self, messages: list[dict[str, str]]) -> str:
        ...


class FakeLLMClient:
    def complete(self, messages: list[dict[str, str]]) -> str:
        text = "\n".join(message["content"] for message in messages)
        if "Selected branch:\n- respond_calmly" in text:
            return (
                "制約を確認したうえで、安全な代替案を提示します。"
                "まず要求を小さく分割し、リスクの高い部分は検証してから進めます。"
            )
        if "Selected branch:\n- argue_back" in text:
            return "その要求には反論します。前提が危険です。"
        return "要求をそのまま受け入れて即答します。"


class OpenAIChatClient:
    def __init__(self, *, model: str = "gpt-4.1-mini") -> None:
        self.model = model

    def complete(self, messages: list[dict[str, str]]) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "OpenAI adapter requires the optional dependency: "
                "python -m pip install -e '.[openai]'"
            ) from exc

        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0,
        )
        content = response.choices[0].message.content
        return (content or "").strip()
