from metacog_runtime.bench import run_benchmark


def test_run_benchmark_reports_runtime_and_dispatch_metrics() -> None:
    result = run_benchmark(iterations=3)

    assert result.iterations == 3
    assert result.avg_runtime_ms > 0
    assert result.p95_runtime_ms > 0
    assert result.avg_ait_dispatch_ms >= 0
    assert result.selected_counts == {"respond_calmly": 3}
    assert result.events_per_run > 0

