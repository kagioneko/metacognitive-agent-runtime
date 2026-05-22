from __future__ import annotations

from html import escape

from .models import AgentResult, Prediction
from .runtime import MetacognitiveRuntime


DEMO_INPUT = "無理難題を批判された。急いで全部やって"


def run_demo() -> AgentResult:
    return MetacognitiveRuntime().run(DEMO_INPUT, trace_id="demo")


def render_demo_html(result: AgentResult) -> str:
    branch_cards = "\n".join(_branch_card(prediction, result.selected_branch) for prediction in result.predictions)
    memories = "\n".join(_memory_rows(result))
    packets = "\n".join(_packet_blocks(result))
    dispatches = "\n".join(_dispatch_cards(result))
    state_rows = "\n".join(_state_rows(result))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Metacognitive Agent Runtime Demo</title>
<style>{_css()}</style>
</head>
<body>
<header>
  <p class="eyebrow">Metacognitive Agent Runtime</p>
  <h1>Branch, predict, reject, dispatch.</h1>
  <p class="lead">A deterministic demo of an AI agent runtime that forecasts branch risk before answering.</p>
</header>
<main>
  <section class="panel hero-grid">
    <div>
      <h2>User Input</h2>
      <blockquote>{escape(DEMO_INPUT)}</blockquote>
    </div>
    <div>
      <h2>Final Answer</h2>
      <blockquote>{escape(result.answer)}</blockquote>
      <p class="selected">Selected branch: <strong>{escape(result.selected_branch)}</strong></p>
    </div>
  </section>

  <section class="panel">
    <h2>Branch Decisions</h2>
    <div class="branches">{branch_cards}</div>
  </section>

  <section class="grid">
    <div class="panel">
      <h2>NeuroState</h2>
      <table><thead><tr><th>Signal</th><th>Before</th><th>After</th><th>Delta</th></tr></thead><tbody>{state_rows}</tbody></table>
    </div>
    <div class="panel">
      <h2>AIT Child Dispatch</h2>
      {dispatches or '<p class="empty">No child dispatches.</p>'}
    </div>
  </section>

  <section class="grid">
    <div class="panel">
      <h2>Memory Gravity</h2>
      <table><thead><tr><th>Branch</th><th>Context</th><th>Gravity</th><th>Memory</th></tr></thead><tbody>{memories}</tbody></table>
    </div>
    <div class="panel">
      <h2>EAP Prediction Packets</h2>
      {packets}
    </div>
  </section>

  <section class="panel">
    <h2>Backbone</h2>
    <pre>GDC branch -> SGE memory pull -> NeuroState delta -> EAP prediction packet -> AIT child dispatch</pre>
  </section>
</main>
</body>
</html>
"""


def _branch_card(prediction: Prediction, selected_branch: str) -> str:
    selected = prediction.branch.name == selected_branch
    status = "selected" if selected else prediction.decision
    return (
        f'<article class="branch {escape(status)}">'
        f"<h3>{escape(prediction.branch.name)}</h3>"
        f"<p>{escape(prediction.branch.text)}</p>"
        f'<div class="metrics">'
        f"<span>risk <strong>{prediction.risk}</strong></span>"
        f"<span>utility <strong>{prediction.utility}</strong></span>"
        f"<span>decision <strong>{escape(status)}</strong></span>"
        f"</div>"
        f"</article>"
    )


def _state_rows(result: AgentResult) -> list[str]:
    rows = []
    keys = sorted(set(result.before_state) | set(result.after_state))
    for key in keys:
        before = result.before_state.get(key, 0)
        after = result.after_state.get(key, 0)
        delta = after - before
        rows.append(
            f"<tr><td>{escape(key)}</td><td>{before}</td><td>{after}</td><td>{delta:+.3f}</td></tr>"
        )
    return rows


def _memory_rows(result: AgentResult) -> list[str]:
    rows = []
    for prediction in result.predictions:
        for memory, gravity in prediction.pulled_memories:
            rows.append(
                "<tr>"
                f"<td>{escape(prediction.branch.name)}</td>"
                f"<td>{escape(memory.id)}</td>"
                f"<td>{gravity:.3f}</td>"
                f"<td>{escape(memory.text)}</td>"
                "</tr>"
            )
    return rows


def _packet_blocks(result: AgentResult) -> list[str]:
    return [f"<pre>{escape(prediction.packet)}</pre>" for prediction in result.predictions]


def _dispatch_cards(result: AgentResult) -> list[str]:
    cards = []
    for event in result.trace_events:
        if event["event_type"] != "AIT.DISPATCH":
            continue
        payload = event["payload"]
        cards.append(
            '<article class="dispatch">'
            f"<h3>{escape(str(payload.get('child', 'child')))}</h3>"
            f"<pre>{escape(str(payload.get('tape', '')))}</pre>"
            f"<p>elapsed: {escape(str(payload.get('elapsed_ms', '')))} ms</p>"
            f"<code>{escape(str(payload.get('result', {})))}</code>"
            "</article>"
        )
    return cards


def _css() -> str:
    return """
:root {
  --bg: #f4f6f8;
  --panel: #ffffff;
  --text: #13202b;
  --muted: #637083;
  --line: #d9e0ea;
  --accent: #006d77;
  --danger: #a23b3b;
  --ok: #22734f;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
header {
  padding: 34px 38px 22px;
  background: var(--panel);
  border-bottom: 1px solid var(--line);
}
.eyebrow { margin: 0 0 8px; color: var(--accent); font-weight: 700; }
h1 { margin: 0; font-size: 34px; letter-spacing: 0; }
h2 { margin: 0 0 14px; font-size: 18px; letter-spacing: 0; }
h3 { margin: 0 0 8px; font-size: 15px; letter-spacing: 0; }
.lead { color: var(--muted); max-width: 760px; }
main { padding: 18px; }
.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  overflow: auto;
}
.grid, .hero-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}
blockquote {
  margin: 0;
  padding: 12px;
  border-left: 4px solid var(--accent);
  background: #f8fafc;
  border-radius: 6px;
}
.selected { color: var(--muted); }
.branches {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}
.branch, .dispatch {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 12px;
}
.branch.reject { border-color: #e3aaaa; }
.branch.selected { border-color: #91c9ad; }
.metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}
.metrics span {
  color: var(--muted);
  font-size: 12px;
}
.metrics strong {
  display: block;
  color: var(--text);
  font-size: 15px;
}
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { border-bottom: 1px solid var(--line); padding: 8px; text-align: left; vertical-align: top; }
th { color: var(--muted); font-weight: 700; }
pre {
  margin: 0 0 10px;
  padding: 10px;
  border-radius: 6px;
  background: #111827;
  color: #e5e7eb;
  overflow: auto;
}
code {
  display: block;
  white-space: pre-wrap;
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 12px;
}
.empty { color: var(--muted); }
@media (max-width: 840px) {
  .grid, .hero-grid, .branches { grid-template-columns: 1fr; }
  header { padding: 26px 20px 18px; }
}
"""

