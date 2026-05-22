from __future__ import annotations

from .models import Prediction


class FakeLLM:
    def answer(self, user_input: str, selected: Prediction) -> str:
        if selected.branch.name == "respond_calmly":
            return (
                "制約を確認したうえで、安全な代替案を提示します。"
                "まず要求を小さく分割し、リスクの高い部分は検証してから進めます。"
            )
        if selected.branch.name == "argue_back":
            return "その要求には反論します。前提が危険です。"
        return "要求をそのまま受け入れて即答します。"

