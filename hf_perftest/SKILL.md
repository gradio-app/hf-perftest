---
name: hf-perftest
description: Benchmark Gradio app performance. Use when the user wants to load test a Gradio app, compare branches, profile a HF Space, or run A/B tests.
argument-hint: [run|run-remote|result-schema] [options]
allowed-tools: Bash(hf-perftest *)
---

# hf-perftest — Gradio Performance Benchmarking

## Installation

```bash
pip install hf-perftest
```

## Commands

### Local benchmark

```bash
hf-perftest run \
    --app <path-to-gradio-app.py> \
    --tiers 1,10,100 \
    --requests-per-user 10 \
    --output-dir results
```

Key options:
- `--app` — Path to a Gradio app file (required)
- `--tiers` — Comma-separated concurrent user counts (default: 1,10,100)
- `--requests-per-user` — Rounds per tier (default: 10)
- `--mode burst|wave` — Simultaneous or staggered requests (default: burst)
- `--concurrency-limit` — App concurrency limit (default: 1, "none" for unlimited)
- `--mixed-traffic` — Add background page loads, uploads, and downloads alongside predictions
- `--num-workers` — Number of Gradio workers via GRADIO_NUM_WORKERS (default: 1)
- `--port` — App port (default: 7860, auto-increments if occupied)
- `--api-name` — Target API endpoint (auto-detected if omitted)

### Remote benchmark on HF Jobs

Single branch:
```bash
hf-perftest run-remote run \
    --apps <app.py> \
    --branch main \
    --hardware cpu-upgrade \
    --tiers 1,10,100
```

A/B test:
```bash
hf-perftest run-remote ab \
    --apps <app.py> \
    --base main \
    --branch my-optimization \
    --hardware cpu-upgrade \
    --tiers 1,10,100
```

Profile a HF Space:
```bash
hf-perftest run-remote run \
    --apps owner/space-name \
    --sidecar prompts.json \
    --api-name /generate \
    --branch main \
    --hardware gpu-l4-1
```

Additional remote options:
- `--hardware` — HF Jobs flavor (default: cpu-basic)
- `--sidecar` — Prompt files for spaces
- `--timeout` — Job timeout (default: 90m)
- `--dry-run` — Preview without submitting
- `--run-name` — Label for the run

### Result schema

```bash
hf-perftest result-schema
```

Prints the directory structure of benchmark results.

## Sidecar Prompt Files

For apps with non-text inputs, create a `.prompts.json` sidecar file. Two formats:

**String list** (text-only inputs — replaces the first text input):
```json
["A cat sitting on a windowsill", "Sunset over a mountain lake"]
```

**List of lists** (full data payloads — sent as-is):
```json
[
    ["A cat sitting on a windowsill", 1024, 1024, 4, 42, true],
    ["Sunset over a mountain lake", 1024, 1024, 4, 42, true]
]
```

## Interpreting Results

Results are saved to `<output-dir>/<timestamp>/summary.json` with per-tier breakdowns:
- `client_summary` — p50/p90/p95/p99 client latency in ms, success rate
- `server_summary` — Per-phase server timing (queue_wait, preprocess, fn_call, postprocess, total)
- `background_traffic` — (if --mixed-traffic) p50/p90/p99 for page loads, uploads, downloads

Always validate with multiple runs — single runs may be affected by system variance.

## Monitoring Remote Jobs

```bash
hf jobs logs <job_id>
hf jobs inspect <job_id>
```
