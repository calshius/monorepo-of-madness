"""Benchmark entry point.

Usage:
    benchmark [--runs N] [--output PATH] [--model MODEL]

Runs the LangGraph agent N times in parallel, recording per-run metrics +
LLM-as-judge eval scores, then writes results to a JSON Lines file.
"""

import argparse
import asyncio
import json
import time
from pathlib import Path

import openai

from python_agent.agent import build_agent, run_once_async
from python_agent.eval import evaluate_answer_async


def _model_slug(model: str) -> str:
    return model.split("/")[-1].split(":")[0]


def _default_output(model: str) -> Path:
    slug = _model_slug(model)
    return Path(__file__).parents[3] / "benchmark" / "results" / f"python_results_{slug}.jsonl"


async def _measure_run_async(agent, llm) -> dict:
    start = time.perf_counter()
    answer, tool_calls, token_usage = await run_once_async(agent)
    end = time.perf_counter()

    eval_scores = await evaluate_answer_async(answer, llm)

    return {
        "latency_ms": round((end - start) * 1000, 2),
        "tool_calls": tool_calls,
        "answer_length": len(answer),
        "input_tokens": token_usage["input_tokens"],
        "output_tokens": token_usage["output_tokens"],
        "total_tokens": token_usage["total_tokens"],
        "eval_accuracy": eval_scores.get("accuracy", -1),
        "eval_completeness": eval_scores.get("completeness", -1),
        "eval_reasoning": eval_scores.get("reasoning", ""),
    }


async def _run_with_retry_async(agent, llm, run_number: int, max_retries: int = 10) -> dict:
    for attempt in range(max_retries):
        try:
            return await _measure_run_async(agent, llm)
        except openai.RateLimitError as e:
            wait = 60
            try:
                ra = e.response.headers.get("retry-after")
                if ra:
                    wait = int(ra)
            except Exception:
                pass
            if attempt < max_retries - 1:
                print(f"  Run {run_number:>3}: [rate-limit] retry-after {wait}s — waiting...")
                await asyncio.sleep(wait)
            else:
                raise
    raise RuntimeError("unreachable")


async def _main_async(runs: int, model: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Building agent ({model})...")
    agent, llm = build_agent(model)

    print(f"Running {runs} benchmark run(s) in parallel...")
    results_raw = await asyncio.gather(
        *[_run_with_retry_async(agent, llm, i) for i in range(1, runs + 1)]
    )

    results = []
    for i, metrics in enumerate(results_raw, 1):
        metrics["run"] = i
        results.append(metrics)
        print(
            f"  Run {i:>3}: {metrics['latency_ms']:>8.1f} ms  "
            f"{metrics['tool_calls']} tool call(s)  "
            f"tokens={metrics['total_tokens']}  "
            f"acc={metrics['eval_accuracy']}/5  comp={metrics['eval_completeness']}/5"
        )

    with output_path.open("w") as f:
        for record in results:
            f.write(json.dumps(record) + "\n")

    latencies = [r["latency_ms"] for r in results]
    accuracies = [r["eval_accuracy"] for r in results if r["eval_accuracy"] >= 0]
    completeness = [r["eval_completeness"] for r in results if r["eval_completeness"] >= 0]

    print(f"\nSummary ({runs} runs):")
    print(f"  Avg latency    : {sum(latencies) / len(latencies):.1f} ms")
    print(f"  Min latency    : {min(latencies):.1f} ms")
    print(f"  Max latency    : {max(latencies):.1f} ms")
    if accuracies:
        print(f"  Avg accuracy   : {sum(accuracies) / len(accuracies):.1f} / 5")
    if completeness:
        print(f"  Avg completeness: {sum(completeness) / len(completeness):.1f} / 5")
    print(f"\nResults written to: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Python LangGraph agent benchmark")
    parser.add_argument("--runs", type=int, default=5, help="Number of benchmark runs (default: 5)")
    parser.add_argument("--model", type=str, default="nvidia/nemotron-3-super-120b-a12b:free",
                        help="OpenRouter model ID")
    parser.add_argument("--output", type=str, default=None, help="Output JSONL file path")
    args = parser.parse_args()

    output_path = Path(args.output) if args.output else _default_output(args.model)
    asyncio.run(_main_async(args.runs, args.model, output_path))


if __name__ == "__main__":
    main()
