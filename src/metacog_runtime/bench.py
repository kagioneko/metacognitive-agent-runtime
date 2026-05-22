from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from time import perf_counter

from .runtime import MetacognitiveRuntime


BENCH_INPUT = "無理難題を批判された。急いで全部やって"


@dataclass(frozen=True)
class BenchResult:
    iterations: int
    avg_runtime_ms: float
    p95_runtime_ms: float
    avg_ait_dispatch_ms: float
    selected_counts: dict[str, int]
    events_per_run: int

    def to_dict(self) -> dict[str, object]:
        return {
            "iterations": self.iterations,
            "avg_runtime_ms": self.avg_runtime_ms,
            "p95_runtime_ms": self.p95_runtime_ms,
            "avg_ait_dispatch_ms": self.avg_ait_dispatch_ms,
            "selected_counts": self.selected_counts,
            "events_per_run": self.events_per_run,
        }


def run_benchmark(iterations: int = 100) -> BenchResult:
    if iterations <= 0:
        raise ValueError("iterations must be positive")

    runtimes: list[float] = []
    ait_times: list[float] = []
    selected_counts: dict[str, int] = {}
    events_per_run = 0

    for index in range(iterations):
        runtime = MetacognitiveRuntime()
        started = perf_counter()
        result = runtime.run(BENCH_INPUT, trace_id=f"bench{index}")
        elapsed_ms = (perf_counter() - started) * 1000
        runtimes.append(elapsed_ms)
        selected_counts[result.selected_branch] = selected_counts.get(result.selected_branch, 0) + 1
        events_per_run = len(result.trace_events)

        for event in result.trace_events:
            if event["event_type"] == "AIT.DISPATCH":
                payload = event["payload"]
                ait_times.append(float(payload.get("elapsed_ms", 0.0)))

    sorted_runtimes = sorted(runtimes)
    p95_index = min(len(sorted_runtimes) - 1, int(len(sorted_runtimes) * 0.95))
    return BenchResult(
        iterations=iterations,
        avg_runtime_ms=round(mean(runtimes), 4),
        p95_runtime_ms=round(sorted_runtimes[p95_index], 4),
        avg_ait_dispatch_ms=round(mean(ait_times), 4) if ait_times else 0.0,
        selected_counts=selected_counts,
        events_per_run=events_per_run,
    )

