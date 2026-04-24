#!/usr/bin/env bash
# Run both agents across multiple OpenRouter models, then generate the HTML report.
# Usage: ./run.sh [--runs N]
#
# Requires:
#   - OPENROUTER_API_KEY env var set
#   - Python venv at /home/callum/projects/.venv (or already activated)
#   - Rust toolchain installed

set -euo pipefail

RUNS=5
while [[ $# -gt 0 ]]; do
    case "$1" in
        --runs) RUNS="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR/.."
VENV="$ROOT/../../.venv"

# ── API key ───────────────────────────────────────────────────────
if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
    echo "ERROR: set OPENROUTER_API_KEY before running." >&2
    exit 1
fi

# ── Python venv ───────────────────────────────────────────────────
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
    if [[ -f "$VENV/bin/activate" ]]; then
        # shellcheck disable=SC1091
        source "$VENV/bin/activate"
    else
        echo "WARNING: could not find venv at $VENV — assuming python deps are on PATH"
    fi
fi

# ── Models to benchmark ───────────────────────────────────────────
MODELS=(
    "openai/gpt-5.4"
    "anthropic/claude-sonnet-4.6"
    "google/gemini-3.1-pro-preview"
)

echo "============================================================"
echo " Performance Comparison Benchmark  (runs=$RUNS)"
echo " Models: ${#MODELS[@]}"
echo "============================================================"

# ── Build Rust binary first so build time isn't in the benchmark ─
echo ""
echo "── Building Rust binary ──"
cd "$ROOT/rust_agent"
cargo build --release --quiet

# ── Loop over models ──────────────────────────────────────────────
for model in "${MODELS[@]}"; do
    slug=$(echo "$model" | sed 's|.*/||;s|:.*||')

    echo ""
    echo "══════════════════════════════════════════════════════════"
    echo " Model: $model"
    echo "══════════════════════════════════════════════════════════"

    echo ""
    echo "── Python / LangGraph ──"
    cd "$ROOT/python_agent"
    benchmark --runs "$RUNS" --model "$model" \
        --output "$ROOT/benchmark/results/python_results_${slug}.jsonl"

    echo ""
    echo "── Rust / rig ──"
    cd "$ROOT/rust_agent"
    ./target/release/benchmark --runs "$RUNS" --model "$model" \
        --output "$ROOT/benchmark/results/rust_results_${slug}.jsonl"
done

# ── Compare + HTML report ─────────────────────────────────────────
echo ""
echo "── Generating comparison report ──"
cd "$ROOT/benchmark"
python3 compare.py --html

echo ""
echo "============================================================"
echo " Done. Open benchmark/results/report.html to view charts."
echo "============================================================"
