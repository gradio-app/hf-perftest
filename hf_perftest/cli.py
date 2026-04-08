"""Unified CLI entry point for hf-perftest."""

from __future__ import annotations

import sys


RESULT_SCHEMA = """\
hf://buckets/gradio/backend-benchmarks/{run_name}/{branch}/
├── runner.py                      # Copy of the benchmark runner script (for reproducibility)
├── run_params.json                # Job parameters (branch, commit, apps, tiers, etc.)
└── {app_stem}/                    # One directory per app (e.g. "echo_text")
    └── {timestamp}/               # e.g. "20260330_142500"
        ├── summary.json           # Overall results: app name, timestamp, all tier results
        ├── summary_table.txt      # Human-readable table (client/server p50/p90/p99, success%)
        ├── tier_1/
        │   ├── client_latencies.jsonl   # One JSON object per request (client-side timing)
        │   ├── traces.jsonl             # Server-side profiling traces
        │   ├── background_page_loads.jsonl   # (if --mixed-traffic) page load latencies
        │   ├── background_uploads.jsonl      # (if --mixed-traffic) upload latencies
        │   ├── background_downloads.jsonl    # (if --mixed-traffic) download latencies
        │   └── samples/                      # Random sample of output files per round
        ├── tier_10/
        │   └── ...
        └── tier_100/
            └── ...\
"""


def main():
    if len(sys.argv) < 2:
        print("Usage: hf-perftest <command> [args...]")
        print()
        print("Commands:")
        print("  run              Run benchmarks locally against a Gradio app")
        print("  run-remote       Submit benchmarks to HF Jobs infrastructure")
        print("  result-schema    Print the result directory structure")
        sys.exit(1)

    command = sys.argv[1]

    if command == "result-schema":
        print(RESULT_SCHEMA)
    elif command == "run":
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        from hf_perftest.runner import main as runner_main
        runner_main()
    elif command == "run-remote":
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        from hf_perftest.remote_runner import main as remote_main
        remote_main()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: run, run-remote, result-schema")
        sys.exit(1)


if __name__ == "__main__":
    main()
