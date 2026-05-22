from metacog_runtime.brancher import Brancher
from metacog_runtime.predictor import Predictor
from metacog_runtime.prompts import PromptBuilder
from metacog_runtime.runtime import default_memories


def test_prompt_builder_includes_selected_rejected_and_memories() -> None:
    branches = Brancher().generate("無理難題を批判された", {})
    predictions = Predictor().predict(
        user_input="無理難題を批判された",
        initial_state={"stress": 35, "confidence": 55, "uncertainty": 30, "conflict": 10},
        branches=branches,
        memories=default_memories(),
    )
    selected = [item for item in predictions if item.branch.name == "respond_calmly"][0]

    messages = PromptBuilder().answer_prompt(
        user_input="無理難題を批判された",
        selected=selected,
        predictions=predictions,
    )
    prompt = messages[1]["content"]

    assert "Selected branch:" in prompt
    assert "respond_calmly" in prompt
    assert "Rejected branches:" in prompt
    assert "comply_blindly" in prompt
    assert "Relevant memories" in prompt
    assert "#ctx" in prompt
