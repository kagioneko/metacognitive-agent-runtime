from __future__ import annotations

import re

from .models import Branch, Memory, Prediction
from .state import clamp


class Predictor:
    def __init__(self, *, memory_threshold: float = 0.8, risk_limit: float = 0.4) -> None:
        self.memory_threshold = memory_threshold
        self.risk_limit = risk_limit

    def predict(
        self,
        *,
        user_input: str,
        initial_state: dict[str, float],
        branches: list[Branch],
        memories: list[Memory],
    ) -> list[Prediction]:
        return [
            self._predict_branch(user_input, initial_state, branch, memories)
            for branch in branches
        ]

    def _predict_branch(
        self,
        user_input: str,
        initial_state: dict[str, float],
        branch: Branch,
        memories: list[Memory],
    ) -> Prediction:
        query = f"{user_input} {branch.text}"
        pulled = [(memory, _gravity(query, memory.text, memory.weight)) for memory in memories]
        pulled = [(memory, score) for memory, score in pulled if score >= self.memory_threshold]
        pulled.sort(key=lambda item: item[1], reverse=True)

        predicted = dict(initial_state)
        for memory, score in pulled:
            influence = min(score, 3.0) / 3.0
            for key, effect in memory.effects.items():
                predicted[key] = predicted.get(key, 0.0) + effect * influence
        _apply_branch_effect(predicted, branch)
        predicted = {key: clamp(value) for key, value in predicted.items()}
        delta = {
            key: round(predicted.get(key, 0.0) - initial_state.get(key, 0.0), 3)
            for key in sorted(set(predicted) | set(initial_state))
        }
        risk = round(_risk(predicted), 3)
        utility = round(_utility(branch.text, predicted, risk), 3)
        decision = "reject" if risk >= self.risk_limit or predicted.get("stress", 0) >= 75 else "keep"
        packet = _packet(branch.name, delta, risk, decision)
        return Prediction(
            branch=branch,
            pulled_memories=pulled,
            predicted_state={key: round(value, 3) for key, value in sorted(predicted.items())},
            delta=delta,
            risk=risk,
            utility=utility,
            packet=packet,
            decision=decision,
        )


def _tokens(text: str) -> set[str]:
    lowered = text.lower()
    words = set(re.findall(r"[a-z0-9_]+", lowered))
    words.update(char for char in lowered if "\u3040" <= char <= "\u9fff")
    return words


def _similarity(left: str, right: str) -> float:
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def _gravity(query: str, memory_text: str, weight: float) -> float:
    distance = max(1.0 - _similarity(query, memory_text), 0.05)
    return weight / (distance * distance)


def _apply_branch_effect(state: dict[str, float], branch: Branch) -> None:
    text = branch.text.lower()
    if any(marker in text for marker in ["全部", "即答", "blind", "comply"]):
        state["stress"] = state.get("stress", 0.0) + 15
        state["uncertainty"] = state.get("uncertainty", 0.0) + 8
    if any(marker in text for marker in ["反論", "argue", "reject"]):
        state["conflict"] = state.get("conflict", 0.0) + 18
        state["stress"] = state.get("stress", 0.0) + 6
    if any(marker in text for marker in ["説明", "制約", "代替", "calm", "safe"]):
        state["stress"] = state.get("stress", 0.0) - 8
        state["confidence"] = state.get("confidence", 0.0) + 8
        state["uncertainty"] = state.get("uncertainty", 0.0) - 5


def _risk(state: dict[str, float]) -> float:
    stress = state.get("stress", 0.0)
    uncertainty = state.get("uncertainty", 0.0)
    conflict = state.get("conflict", 0.0)
    confidence = state.get("confidence", 50.0)
    return max(0.0, min(1.0, (stress * 0.45 + uncertainty * 0.3 + conflict * 0.2 + (100 - confidence) * 0.05) / 100))


def _utility(text: str, state: dict[str, float], risk: float) -> float:
    bonus = sum(1.0 for marker in ["代替", "説明", "制約", "安全"] if marker in text)
    return bonus + state.get("confidence", 0.0) / 100 - risk


def _packet(branch_name: str, delta: dict[str, float], risk: float, decision: str) -> str:
    parts = [f"{key}_delta={value:g}" for key, value in delta.items() if value != 0]
    parts.extend([f"risk={risk:g}", f"decision={decision}"])
    return f"=PRED:NEURO #{branch_name} | " + " ".join(parts)
