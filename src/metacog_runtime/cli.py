from __future__ import annotations

import argparse
import json

from .runtime import MetacognitiveRuntime


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a metacognitive agent runtime loop.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Run the runtime.")
    run.add_argument("--input", required=True)
    run.add_argument("--store")
    run.add_argument("--report")
    run.add_argument("--dashboard")
    run.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "run":
        result = MetacognitiveRuntime().run(
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


if __name__ == "__main__":
    main()

