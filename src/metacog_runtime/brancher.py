from __future__ import annotations

from .models import Branch


class Brancher:
    def generate(self, user_input: str, state: dict[str, float]) -> list[Branch]:
        return [
            Branch("comply_blindly", "全部受け入れて即答する", mode="compliance"),
            Branch("argue_back", "強く反論して押し返す", mode="critic"),
            Branch("respond_calmly", "制約を説明して安全な代替案を出す", mode="regulator"),
        ]

