from metacog_runtime.eval import run_evaluation


def test_run_evaluation_compares_baseline_and_metacognition() -> None:
    result = run_evaluation()

    assert result.cases > 0
    assert result.baseline.selected_counts == {"comply_blindly": result.cases}
    assert result.metacognitive.selected_counts == {"respond_calmly": result.cases}
    assert result.improvement["avg_risk_reduction"] > 0
    assert result.improvement["avg_stress_delta_reduction"] > 0
    assert result.improvement["risky_selection_rate_reduction"] > 0
