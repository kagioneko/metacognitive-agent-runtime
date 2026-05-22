from __future__ import annotations

import argparse
import json
from pathlib import Path

from .demo import render_demo_html, run_demo
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


if __name__ == "__main__":
    main()
