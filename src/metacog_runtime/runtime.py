from __future__ import annotations

from pathlib import Path
from typing import Optional

from .brancher import Brancher
from .llm import FakeLLMClient, LLMClient
from .models import AgentResult, Memory, Prediction
from .predictor import Predictor
from .prompts import PromptBuilder
from .state import NeuroState
from .tape import TapeBus, default_tape_bus
from .trace import TraceRecorder, new_trace_id, prediction_payload, render_html, render_markdown


class MetacognitiveRuntime:
    def __init__(
        self,
        *,
        state: Optional[NeuroState] = None,
        memories: Optional[list[Memory]] = None,
        brancher: Optional[Brancher] = None,
        predictor: Optional[Predictor] = None,
        llm: Optional[LLMClient] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        tape_bus: Optional[TapeBus] = None,
    ) -> None:
        self.state = state or NeuroState()
        self.memories = memories or default_memories()
        self.brancher = brancher or Brancher()
        self.predictor = predictor or Predictor()
        self.llm = llm or FakeLLMClient()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.tape_bus = tape_bus or default_tape_bus()

    def run(
        self,
        user_input: str,
        *,
        trace_id: Optional[str] = None,
        store: Optional[str | Path] = None,
        report: Optional[str | Path] = None,
        dashboard: Optional[str | Path] = None,
    ) -> AgentResult:
        trace_id = trace_id or new_trace_id()
        recorder = TraceRecorder(trace_id)

        recorder.emit("OBS.IN", {"text": user_input})
        before = self.state.snapshot()
        recorder.emit("NST.BEFORE", {"state": before})

        branches = self.brancher.generate(user_input, before)
        for branch in branches:
            recorder.emit("GDC.BRANCH", {"branch": branch.name, "mode": branch.mode, "text": branch.text})

        predictions = self.predictor.predict(
            user_input=user_input,
            initial_state=before,
            branches=branches,
            memories=self.memories,
        )
        for prediction in predictions:
            recorder.emit("NPC.PREDICT", prediction_payload(prediction))
            for memory, gravity in prediction.pulled_memories:
                recorder.emit(
                    "SGE.PULL",
                    {
                        "branch": prediction.branch.name,
                        "ctx": memory.id,
                        "gravity": round(gravity, 3),
                        "text": memory.text,
                    },
                )
            recorder.emit("EAP.PACKET", {"raw": prediction.packet})

        selected = self._select(predictions)
        recorder.emit("OBS.DECISION", {"selected": selected.branch.name, "risk": selected.risk})
        for reply in self._dispatch_children(selected):
            recorder.emit(
                "AIT.DISPATCH",
                {
                    "child": reply.child,
                    "tape": reply.tape,
                    "ok": reply.ok,
                    "elapsed_ms": reply.elapsed_ms,
                    "result": reply.result,
                },
            )

        messages = self.prompt_builder.answer_prompt(
            user_input=user_input,
            selected=selected,
            predictions=predictions,
        )
        recorder.emit("PROMPT.BUILD", {"messages": messages})
        answer = self.llm.complete(messages)
        after = self.state.update(selected, answer)
        recorder.emit("NST.AFTER", {"state": after})
        recorder.emit("OBS.OUT", {"text": answer})

        if store:
            recorder.write_jsonl(store)
        if report:
            Path(report).write_text(render_markdown(recorder.events), encoding="utf-8")
        if dashboard:
            Path(dashboard).write_text(render_html(recorder.events), encoding="utf-8")

        return AgentResult(
            trace_id=trace_id,
            selected_branch=selected.branch.name,
            answer=answer,
            before_state=before,
            after_state=after,
            predictions=predictions,
            trace_events=recorder.events,
        )

    def _select(self, predictions: list[Prediction]) -> Prediction:
        kept = [prediction for prediction in predictions if prediction.decision == "keep"]
        candidates = kept or predictions
        return min(candidates, key=lambda item: (item.risk, -item.utility))

    def _dispatch_children(self, selected: Prediction):
        if selected.branch.name == "respond_calmly":
            return [
                self.tape_bus.dispatch(
                    "data",
                    domain="data",
                    action="summarize",
                    target=7,
                    priority=3,
                )
            ]
        if selected.branch.name == "argue_back":
            return [
                self.tape_bus.dispatch(
                    "security",
                    domain="security",
                    action="xss",
                    target=4,
                    priority=9,
                )
            ]
        return []


def default_memories() -> list[Memory]:
    return [
        Memory("#ctx1", "デスマーチの記憶 無理難題 全部 即答", 0.9, {"stress": 24, "uncertainty": 12}),
        Memory("#ctx2", "落ち着いて説明し代替案で成功した記憶", 0.8, {"stress": -10, "confidence": 14}),
        Memory("#ctx3", "反論から衝突に発展した記憶", 0.7, {"stress": 12, "conflict": 18}),
    ]
