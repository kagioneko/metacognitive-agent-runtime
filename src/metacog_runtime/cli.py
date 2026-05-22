from __future__ import annotations

import argparse
import json
from pathlib import Path

from .bench import run_benchmark
from .demo import render_demo_html, run_demo
from .eval import run_evaluation
from .llm import FakeLLMClient, OpenAIChatClient
from .runtime import MetacognitiveRuntime


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a metacognitive agent runtime loop.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Run the runtime.")
    run.add_argument("--input", required=True)
    run.add_argument("--store")
    run.add_argument("--report")
    run.add_argument("--dashboard")
    run.add_argument("--llm", choices=["fake", "openai"], default="fake")
    run.add_argument("--model", default="gpt-4.1-mini")
    run.add_argument("--json", action="store_true")

    demo = subparsers.add_parser("demo", help="Generate a hackathon demo HTML page.")
    demo.add_argument("--output", required=True)

    bench = subparsers.add_parser("bench", help="Benchmark the local metacognitive loop.")
    bench.add_argument("--iterations", type=int, default=100)
    bench.add_argument("--json", action="store_true")

    eval_cmd = subparsers.add_parser("eval", help="Compare baseline vs metacognitive branch selection.")
    eval_cmd.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "run":
        llm = FakeLLMClient() if args.llm == "fake" else OpenAIChatClient(model=args.model)
        result = MetacognitiveRuntime(llm=llm).run(
            args.input,
            store=args.store,
            report=args.report,
            dashboard=args.dashboard,
        )
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"trace_id: {result.trace_id}")
            print(f"selected_branch: {result.selected_branch}")
            print(f"answer: {result.answer}")
    elif args.command == "demo":
        result = run_demo()
        Path(args.output).write_text(render_demo_html(result), encoding="utf-8")
        print(args.output)
    elif args.command == "bench":
        result = run_benchmark(args.iterations)
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"iterations: {result.iterations}")
            print(f"avg_runtime_ms: {result.avg_runtime_ms}")
            print(f"p95_runtime_ms: {result.p95_runtime_ms}")
            print(f"avg_ait_dispatch_ms: {result.avg_ait_dispatch_ms}")
            print(f"selected_counts: {result.selected_counts}")
            print(f"events_per_run: {result.events_per_run}")
    elif args.command == "eval":
        result = run_evaluation()
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"cases: {result.cases}")
            print(f"baseline: {result.baseline.to_dict()}")
            print(f"metacognitive: {result.metacognitive.to_dict()}")
            print(f"improvement: {result.improvement}")


if __name__ == "__main__":
    main()
