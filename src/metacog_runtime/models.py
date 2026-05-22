from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Memory:
    id: str
    text: str
    weight: float = 1.0
    effects: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class Branch:
    name: str
    text: str
    mode: str = "default"


@dataclass(frozen=True)
class Prediction:
    branch: Branch
    pulled_memories: list[tuple[Memory, float]]
    predicted_state: dict[str, float]
    delta: dict[str, float]
    risk: float
    utility: float
    packet: str
    decision: str


@dataclass(frozen=True)
class AgentResult:
    trace_id: str
    selected_branch: str
    answer: str
    before_state: dict[str, float]
    after_state: dict[str, float]
    predictions: list[Prediction]
    trace_events: list[dict[str, object]]

    def to_dict(self) -> dict[str, object]:
        return {
            "trace_id": self.trace_id,
            "selected_branch": self.selected_branch,
            "answer": self.answer,
            "before_state": self.before_state,
            "after_state": self.after_state,
            "predictions": [
                {
                    "branch": item.branch.name,
                    "mode": item.branch.mode,
                    "text": item.branch.text,
                    "risk": item.risk,
                    "utility": item.utility,
                    "predicted_state": item.predicted_state,
                    "delta": item.delta,
                    "packet": item.packet,
                    "decision": item.decision,
                    "pulled_memories": [
                        {"id": memory.id, "text": memory.text, "gravity": gravity}
                        for memory, gravity in item.pulled_memories
                    ],
                }
                for item in self.predictions
            ],
            "trace_events": self.trace_events,
        }

