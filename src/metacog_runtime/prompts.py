from __future__ import annotations

from .models import Prediction


class PromptBuilder:
    def answer_prompt(
        self,
        *,
        user_input: str,
        selected: Prediction,
        predictions: list[Prediction],
    ) -> list[dict[str, str]]:
        rejected = [item for item in predictions if item.branch.name != selected.branch.name]
        prompt = "\n".join(
            [
                "User input:",
                user_input,
                "",
                "Selected branch:",
                _branch_line(selected),
                "",
                "Rejected branches:",
                *[_branch_line(item) for item in rejected],
                "",
                "Relevant memories for selected branch:",
                *_memory_lines(selected),
                "",
                "Instruction:",
                "Answer using the selected branch. Do not follow rejected branches.",
                "Be concise, concrete, and keep the response stable under the predicted state.",
            ]
        )
        return [
            {
                "role": "system",
                "content": (
                    "You are controlled by an external metacognitive runtime. "
                    "Follow the selected branch and avoid rejected branches."
                ),
            },
            {"role": "user", "content": prompt},
        ]


def _branch_line(prediction: Prediction) -> str:
    return (
        f"- {prediction.branch.name} mode={prediction.branch.mode} "
        f"decision={prediction.decision} risk={prediction.risk} "
        f"delta={prediction.delta}"
    )


def _memory_lines(prediction: Prediction) -> list[str]:
    if not prediction.pulled_memories:
        return ["- none"]
    return [
        f"- {memory.id} gravity={gravity:.3f}: {memory.text}"
        for memory, gravity in prediction.pulled_memories
    ]
