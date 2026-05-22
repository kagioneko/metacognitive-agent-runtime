from __future__ import annotations

from dataclasses import dataclass, field

from .models import Prediction


def clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


@dataclass
class NeuroState:
    values: dict[str, float] = field(
        default_factory=lambda: {
            "stress": 35.0,
            "confidence": 55.0,
            "uncertainty": 30.0,
            "conflict": 10.0,
        }
    )

    def snapshot(self) -> dict[str, float]:
        return dict(self.values)

    def update(self, prediction: Prediction, answer: str) -> dict[str, float]:
        next_state = dict(self.values)
        for key, delta in prediction.delta.items():
            next_state[key] = clamp(next_state.get(key, 0.0) + delta * 0.5)
        if "制約" in answer or "代替" in answer:
            next_state["confidence"] = clamp(next_state.get("confidence", 0.0) + 4)
            next_state["uncertainty"] = clamp(next_state.get("uncertainty", 0.0) - 3)
        if prediction.risk > 0.6:
            next_state["stress"] = clamp(next_state.get("stress", 0.0) + 6)
        self.values = {key: round(value, 3) for key, value in sorted(next_state.items())}
        return self.snapshot()

