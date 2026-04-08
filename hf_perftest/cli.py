"""Unified CLI entry point for hf-perftest."""

from __future__ import annotations

import sys
from pathlib import Path

_SKILL_FILE = Path(__file__).parent / "SKILL.md"

INSTALL_TARGETS = {
    "claude": {
        "dir": ".claude/skills/hf-perftest",
        "file": "SKILL.md",
    },
    "cursor": {
        "dir": ".cursor/rules",
        "file": "hf-perftest.mdc",
    },
    "codex": {
        "dir": ".",
        "file": "AGENTS.md",
        "append": True,
    },
}


def cmd_install_skill(args):
    """Install the hf-perftest skill/rules file for an AI coding tool."""
    content = _SKILL_FILE.read_text()

    targets = args if args else list(INSTALL_TARGETS.keys())
    for target in targets:
        if target not in INSTALL_TARGETS:
            print(f"Unknown target: {target}")
            print(f"Available targets: {', '.join(INSTALL_TARGETS.keys())}")
            sys.exit(1)

    for target in targets:
        cfg = INSTALL_TARGETS[target]
        dest_dir = Path(cfg["dir"])
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / cfg["file"]

        if cfg.get("append") and dest.exists():
            existing = dest.read_text()
            if "hf-perftest" in existing:
                print(f"  {target}: already present in {dest}, skipping")
                continue
            with open(dest, "a") as f:
                f.write("\n\n" + content)
            print(f"  {target}: appended to {dest}")
        else:
            dest.write_text(content)
            print(f"  {target}: wrote {dest}")

    print("\nDone! The skill is now available in your project.")


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
        print("  install-skill    Install AI coding tool skill (claude, cursor, codex)")
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
    elif command == "install-skill":
        cmd_install_skill(sys.argv[2:])
    else:
        print(f"Unknown command: {command}")
        print("Available commands: run, run-remote, result-schema, install-skill")
        sys.exit(1)


if __name__ == "__main__":
    main()
