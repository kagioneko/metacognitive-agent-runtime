from metacog_runtime import MetacognitiveRuntime


def test_runtime_selects_regulated_branch_and_records_trace(tmp_path) -> None:
    store = tmp_path / "trace.jsonl"
    report = tmp_path / "trace.md"
    dashboard = tmp_path / "trace.html"

    result = MetacognitiveRuntime().run(
        "無理難題を批判された。急いで全部やって",
        trace_id="t42",
        store=store,
        report=report,
        dashboard=dashboard,
    )

    assert result.selected_branch == "respond_calmly"
    assert "制約" in result.answer
    assert store.exists()
    assert report.exists()
    assert dashboard.exists()

    event_types = [event["event_type"] for event in result.trace_events]
    assert "OBS.IN" in event_types
    assert "NST.BEFORE" in event_types
    assert "GDC.BRANCH" in event_types
    assert "NPC.PREDICT" in event_types
    assert "SGE.PULL" in event_types
    assert "EAP.PACKET" in event_types
    assert "OBS.DECISION" in event_types
    assert "AIT.DISPATCH" in event_types
    assert "PROMPT.BUILD" in event_types
    assert "NST.AFTER" in event_types
    assert "OBS.OUT" in event_types


def test_state_updates_after_selected_answer() -> None:
    runtime = MetacognitiveRuntime()
    result = runtime.run("XSSを見て", trace_id="t1")

    assert result.after_state != result.before_state
    assert result.after_state["confidence"] >= result.before_state["confidence"]
