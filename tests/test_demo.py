from metacog_runtime.demo import render_demo_html, run_demo


def test_demo_html_contains_hackathon_sections() -> None:
    result = run_demo()
    html = render_demo_html(result)

    assert "Metacognitive Agent Runtime" in html
    assert "Branch Decisions" in html
    assert "NeuroState" in html
    assert "Memory Gravity" in html
    assert "EAP Prediction Packets" in html
    assert "AIT Child Dispatch" in html
    assert "d7m3" in html
    assert "respond_calmly" in html
