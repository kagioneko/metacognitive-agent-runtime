from __future__ import annotations

from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
from uuid import uuid4

from .models import Prediction


def new_trace_id() -> str:
    return uuid4().hex[:8]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class TraceRecorder:
    def __init__(self, trace_id: str) -> None:
        self.trace_id = trace_id
        self.events: list[dict[str, object]] = []

    def emit(self, event_type: str, payload: dict[str, object]) -> None:
        self.events.append(
            {
                "trace_id": self.trace_id,
                "event_type": event_type,
                "timestamp": now_iso(),
                "payload": payload,
            }
        )

    def write_jsonl(self, path: str | Path) -> None:
        with Path(path).open("w", encoding="utf-8") as file:
            for event in self.events:
                file.write(json.dumps(event, ensure_ascii=False) + "\n")


def render_markdown(events: list[dict[str, object]]) -> str:
    trace_id = events[0]["trace_id"] if events else "unknown"
    lines = [f"# Metacognitive Trace: {trace_id}", "", "## Timeline", ""]
    for event in events:
        lines.append(f"- `{event['event_type']}`: `{event['payload']}`")
    return "\n".join(lines) + "\n"


def render_html(events: list[dict[str, object]]) -> str:
    trace_id = events[0]["trace_id"] if events else "unknown"
    rows = "\n".join(
        "<tr>"
        f"<td>{escape(str(event.get('timestamp', '')))}</td>"
        f"<td>{escape(str(event['event_type']))}</td>"
        f"<td><code>{escape(str(event['payload']))}</code></td>"
        "</tr>"
        for event in events
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Metacognitive Trace {escape(str(trace_id))}</title>
<style>
body {{ margin: 0; font-family: system-ui, sans-serif; background: #f6f7f9; color: #17202a; }}
header {{ padding: 24px 32px; background: #fff; border-bottom: 1px solid #d8dee8; }}
main {{ padding: 18px; }}
table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #d8dee8; }}
th, td {{ padding: 9px; border-bottom: 1px solid #d8dee8; text-align: left; vertical-align: top; }}
code {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 12px; }}
</style>
</head>
<body>
<header><h1>Metacognitive Trace {escape(str(trace_id))}</h1></header>
<main>
<table>
<thead><tr><th>Time</th><th>Event</th><th>Payload</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>
</main>
</body>
</html>
"""


def prediction_payload(prediction: Prediction) -> dict[str, object]:
    return {
        "branch": prediction.branch.name,
        "mode": prediction.branch.mode,
        "decision": prediction.decision,
        "risk": prediction.risk,
        "utility": prediction.utility,
        "packet": prediction.packet,
    }

