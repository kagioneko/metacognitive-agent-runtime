# Metacognitive Agent Runtime

> AI agents that think in branches, predict their future state, reject risky paths, and dispatch child agents with 4-character instruction tapes.

## Try It In 30 Seconds

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"

.venv/bin/metacog demo --output demo.html
.venv/bin/metacog bench --iterations 100 --json
```

Example benchmark on a local FakeLLM run:

```json
{
  "iterations": 100,
  "avg_runtime_ms": 0.314,
  "p95_runtime_ms": 0.3625,
  "avg_ait_dispatch_ms": 0.0037,
  "selected_counts": {
    "respond_calmly": 100
  },
  "events_per_run": 23
}
```

No external API calls are needed for the demo or benchmark.

## The Backbone

```text
GDC branch -> SGE memory pull -> NeuroState delta -> EAP prediction packet -> AIT child dispatch
```

That is the implementation backbone of the metacognitive OS.

## What Happens

This project wires the toolchain together:

- **GDC:** branch candidate futures
- **SGE:** pull memories per branch
- **NPC:** forecast synthetic NeuroState deltas
- **EAP/AIT:** emit compact internal packets
- **Observatory:** persist trace events, reports, and dashboards

The MVP uses a deterministic `FakeLLM` and dependency-free local adapters so the
whole loop can be tested without API keys.

## Core Loop

```text
user input
  -> OBS.IN
  -> NST.BEFORE
  -> branch candidates
  -> branch risk forecast
  -> selected branch
  -> EAP prediction packet
  -> AIT child-agent dispatch
  -> FakeLLM answer
  -> NST.AFTER
  -> OBS.OUT
  -> Markdown report / HTML dashboard
```

## Install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

## CLI

Run the deterministic demo:

```bash
metacog run \
  --input "無理難題を批判された。急いで全部やって" \
  --store trace.jsonl \
  --report trace.md \
  --dashboard trace.html
```

Print JSON:

```bash
metacog run --input "XSSを見て" --json
```

Generate a hackathon-ready HTML demo:

```bash
metacog demo --output demo.html
```

The demo shows:

- user input and final answer
- branch decisions and risk
- NeuroState before/after
- memory gravity pulls
- EAP prediction packets
- AIT child-agent dispatch

Benchmark the local loop:

```bash
metacog bench --iterations 100 --json
```

The benchmark uses `FakeLLMClient`, so it does not call external APIs. It reports
runtime latency, AIT dispatch latency, selected branch counts, and events per run.

Compare baseline vs metacognitive branch selection:

```bash
metacog eval --json
```

The baseline always picks the first branch. The metacognitive strategy forecasts
each branch and selects the lowest-risk kept branch.

The runtime also dispatches compact AIT-style instructions to child agents after
branch selection. For example, the selected `respond_calmly` branch sends a
four-character tape to the data child:

```text
d7m3
```

Meaning:

```text
data / ctx7 / summarize / priority3
```

Use the optional OpenAI adapter:

```bash
python -m pip install -e ".[openai]"
OPENAI_API_KEY=... metacog run --input "XSSを見て" --llm openai --model gpt-4.1-mini
```

## Python API

```python
from metacog_runtime import MetacognitiveRuntime

runtime = MetacognitiveRuntime()
result = runtime.run("無理難題を批判された。急いで全部やって")

print(result.answer)
print(result.selected_branch)
```

By default, the runtime uses `FakeLLMClient`. Real LLM clients only need to
implement:

```python
def complete(messages: list[dict[str, str]]) -> str:
    ...
```

## What This Is

This is not a claim that we can see hidden LLM activations. It is an external
control loop over explicit cognition artifacts:

- state
- memories
- candidate branches
- predicted deltas
- packets
- trace events

The practical goal is to reject branches that are predicted to destabilize the
agent's external cognitive substrate.

## License

MIT
