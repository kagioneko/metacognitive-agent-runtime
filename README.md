# Metacognitive Agent Runtime

> A minimal runtime loop for external metacognition in AI agents.

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

The important spine:

```text
GDC branch -> SGE memory pull -> NeuroState delta -> EAP prediction packet
```

That is the implementation backbone of the metacognitive OS.

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
