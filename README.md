# hf-perftest

Performance benchmarking tool for Gradio apps. Measures per-phase request timing, load tests with concurrent users, and supports mixed background traffic simulation.

## Installation

```bash
pip install hf-perftest
```

Or install from source:

```bash
git clone https://github.com/gradio-app/hf-perftest.git
cd hf-perftest
pip install -e .
```

### Claude Code Skill

To add `hf-perftest` as a Claude Code skill so Claude can help you run benchmarks:

```bash
claude install-skill https://github.com/gradio-app/hf-perftest
```

This installs the skill from `.claude/skills/hf-perftest/SKILL.md` in the repo. Once installed, you can use `/hf-perftest` in Claude Code or just ask Claude to benchmark a Gradio app.

## Quick Start

Run a benchmark against a Gradio app:

```bash
hf-perftest run \
    --app apps/echo_text.py \
    --tiers 1,10,100 \
    --requests-per-user 10 \
    --output-dir benchmark_results/my_run
```

This will:
1. Launch the app with `GRADIO_PROFILING=1`
2. Run warmup requests
3. For each tier, fire N concurrent users in burst mode for 10 rounds
4. Collect client latencies and server-side per-phase traces
5. Save results to `benchmark_results/my_run/<timestamp>/`

## Commands

### `hf-perftest run` — Local Benchmarks

```bash
# Minimal
hf-perftest run --app apps/echo_text.py

# Full options
hf-perftest run \
    --app apps/echo_text.py \
    --tiers 1,10,100 \
    --requests-per-user 50 \
    --mode burst \
    --concurrency-limit 1 \
    --mixed-traffic \
    --num-workers 2 \
    --output-dir results
```

#### Options

```
--app               Path to the Gradio app to test (required)
--tiers             Comma-separated concurrency tiers (default: 1,10,100)
--requests-per-user Number of rounds per tier (default: 10)
--mode              Load pattern: "burst" or "wave" (default: burst)
--concurrency-limit Concurrency limit for the app (default: 1, use "none" for unlimited)
--mixed-traffic     Run background traffic (page loads, uploads, downloads) alongside predictions
--num-workers       Number of Gradio workers via GRADIO_NUM_WORKERS (default: 1)
--output-dir        Output directory (default: benchmark_results)
--port              Port for the Gradio app (default: 7860)
--api-name          API endpoint name (auto-detected if not specified)
```

#### Burst vs Wave Mode

- **burst**: All N users fire simultaneously per round. Measures worst-case queue contention.
- **wave**: Each user waits a random 0–500ms jitter before firing. Simulates realistic staggered traffic.

#### Mixed Traffic

With `--mixed-traffic`, background workers run alongside predictions to simulate realistic server load:
- **Page loads**: `GET /`, `/config`, `/gradio_api/info`, `/theme.css`, plus discovered JS/CSS assets
- **Uploads**: `POST /gradio_api/upload` with files from `sample-inputs/`
- **Downloads**: `GET /gradio_api/file=...` for static files

### `hf-perftest run-remote` — Remote Benchmarks on HF Jobs

Submit benchmarks to HF Jobs infrastructure for reproducible results on standardized hardware.

#### Single Branch

```bash
hf-perftest run-remote run \
    --apps apps/echo_text.py apps/streaming_chat.py \
    --branch main \
    --tiers 1,10,100 \
    --requests-per-user 50 \
    --hardware cpu-upgrade
```

#### A/B Testing Two Branches

```bash
hf-perftest run-remote ab \
    --apps apps/echo_text.py apps/file_heavy.py \
    --base main \
    --branch my-optimization \
    --tiers 1,10,100 \
    --requests-per-user 50 \
    --hardware cpu-upgrade
```

#### Profiling a HF Space

```bash
hf-perftest run-remote run \
    --apps mrfakename/z-image-turbo \
    --sidecar apps/z-image-turbo.prompts.json \
    --api-name /generate_image \
    --branch main \
    --hardware gpu-l4-1
```

#### Remote Runner Options

```
--apps              Paths to local Gradio app files or a HF Space ID (required)
--branch/--base     Git branches to benchmark (resolved to commit SHA)
--commit            Direct commit SHA (overrides --branch)
--hardware          HF Jobs hardware flavor (default: cpu-basic)
--tiers             Comma-separated concurrency tiers (default: 1,10,100)
--requests-per-user Rounds per tier (default: 10)
--mode              Load pattern: "burst" or "wave" (default: burst)
--concurrency-limit App concurrency limit (default: 1)
--mixed-traffic     Run background traffic alongside predictions
--num-workers       Number of Gradio workers (default: 1)
--sidecar           Sidecar prompt files (.prompts.json) to upload alongside apps
--timeout           Job timeout (default: 90m)
--run-name          Human-readable label (default: auto-generated)
--dry-run           Print generated script without submitting
```

### `hf-perftest result-schema` — Result Directory Structure

```bash
hf-perftest result-schema
```

Prints the structure of the results directory.

## Test Apps

| App | What it tests |
|-----|---------------|
| `echo_text.py` | `lambda x: x` — pure framework overhead |
| `file_heavy.py` | 256x256 random image — exercises postprocess serialization |
| `image_to_image.py` | Image identity — tests file upload + download |
| `stateful_counter.py` | `gr.State` with dict — tests session state handling |
| `streaming_chat.py` | `ChatInterface` generator with 6 yields — tests streaming |
| `llm_chat.py` | LLM chat via HF Inference API — real-world chat workload |
| `text_to_image.py` | Text-to-image via HF Inference API — real-world image gen |

## Server-Side Profiling

The instrumentation (enabled via `GRADIO_PROFILING=1`) traces six phases per request:

| Phase | What it measures |
|-------|-----------------|
| `queue_wait` | Time from event creation to processing start |
| `preprocess` | Input deserialization |
| `fn_call` | User function execution (accumulated across generator yields) |
| `postprocess` | Output serialization (e.g. numpy → image → file cache) |
| `streaming_diff` | Computing incremental diffs for streaming output |
| `total` | Wall-clock time for the full `process_api()` call |

Profiling endpoints (only available when `GRADIO_PROFILING=1`):

```bash
curl http://localhost:7860/gradio_api/profiling/traces | python -m json.tool
curl http://localhost:7860/gradio_api/profiling/summary | python -m json.tool
curl -X POST http://localhost:7860/gradio_api/profiling/clear
```

## Monitoring Remote Jobs

```bash
hf jobs logs <job_id>
hf jobs inspect <job_id>
```
