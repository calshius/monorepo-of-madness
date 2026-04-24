/// rig ReAct-style agent benchmark.
///
/// - Real DuckDuckGo Instant Answer API web search (no API key required)
/// - LLM-as-judge eval for accuracy + completeness after each run
/// - All N runs execute in parallel via tokio::task::JoinSet
/// - JSONL output: { run, latency_ms, peak_memory_kb, tool_calls, answer_length,
///                   input_tokens, output_tokens, total_tokens,
///                   eval_accuracy, eval_completeness, eval_reasoning }
///
/// Usage:
///   cargo run --release -- [--runs N] [--model MODEL] [--output PATH]
use std::sync::Arc;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::{Duration, Instant};

use anyhow::Result;
use rig::agent::PromptRequest;
use rig::client::CompletionClient;
use rig::providers::openai;
use rig::tool::ToolDyn;
use serde_json::json;

mod tools;
mod eval;
mod config;

use crate::tools::search_knowledge_base::SearchKnowledgeBase;
use crate::tools::photosynthesis_data_collector::PhotosynthesisDataCollector;
use crate::eval::photosynthesis_evaluator::{evaluate_answer};
use crate::config::args::Config;

// ── Memory helper (Linux /proc) ───────────────────────────────────────────────

fn rss_kb() -> u64 {
    std::fs::read_to_string("/proc/self/status")
        .ok()
        .and_then(|s| {
            s.lines()
                .find(|l| l.starts_with("VmRSS:"))
                .and_then(|l| l.split_whitespace().nth(1))
                .and_then(|v| v.parse().ok())
        })
        .unwrap_or(0)
}

// ── Per-run benchmark ─────────────────────────────────────────────────────

const BENCHMARK_PROMPT: &str =
    "Compare photosynthesis in roses and sunflowers. Use both the search_knowledge_base tool and the photosynthesis_data_collector tool to gather comprehensive information about the biochemical pathways, environmental adaptations, and efficiency differences.";

async fn run_once(run_num: usize, api_key: String, model: String) -> Result<serde_json::Value> {
    let client = openai::CompletionsClient::builder()
        .api_key(&api_key)
        .base_url("https://openrouter.ai/api/v1")
        .build()?;

    let search_counter = Arc::new(AtomicUsize::new(0));
    let photosynthesis_counter = Arc::new(AtomicUsize::new(0));
    let search_tool = SearchKnowledgeBase { counter: search_counter.clone() };
    let photosynthesis_tool = PhotosynthesisDataCollector { counter: photosynthesis_counter.clone() };

    let agent = client
        .agent(&model)
        .preamble(
            "You are a helpful assistant. When asked about a topic, \
              use the search_knowledge_base tool and photosynthesis_data_collector tool to look it up before answering.",
        )
        .tools(vec![
            Box::new(search_tool) as Box<dyn ToolDyn>,
            Box::new(photosynthesis_tool) as Box<dyn ToolDyn>
        ])
        .default_max_turns(5)
        .build();

    let eval_agent = client
        .agent(&model)
        .preamble("You are an expert biology teacher evaluating student answers.")
        .build();

    let mem_before = rss_kb();

    let (prompt_response, latency_ms) = loop {
        let start = Instant::now();
        match PromptRequest::from_agent(&agent, BENCHMARK_PROMPT).extended_details().await {
            Ok(resp) => break (resp, start.elapsed().as_secs_f64() * 1000.0),
            Err(e) if e.to_string().contains("429") => {
                let wait = parse_retry_after(&e.to_string());
                println!("  Run {:>3}: [rate-limit] retry-after {}s — waiting...", run_num, wait);
                tokio::time::sleep(Duration::from_secs(wait)).await;
            }
            Err(e) => return Err(anyhow::anyhow!("{e}")),
        }
    };

      let mem_after = rss_kb();
      let peak_memory_kb = mem_after.saturating_sub(mem_before);
      let search_tool_calls = search_counter.load(Ordering::SeqCst);
      let photosynthesis_tool_calls = photosynthesis_counter.load(Ordering::SeqCst);
      let total_tool_calls = search_tool_calls + photosynthesis_tool_calls;
      let response = prompt_response.output;
      let usage = prompt_response.usage;

      let eval = evaluate_answer(&eval_agent, &response).await;

      println!(
          "  Run {:>3}: {:>8.1} ms  {:>8} KB  {} tool call(s) (search: {}, photosynthesis: {})  tokens={}  acc={}/5  comp={}/5",
          run_num, latency_ms, peak_memory_kb, total_tool_calls, search_tool_calls, photosynthesis_tool_calls, usage.total_tokens,
          eval.accuracy, eval.completeness
      );

      Ok(json!({
          "run": run_num,
          "latency_ms": (latency_ms * 10.0).round() / 10.0,
          "peak_memory_kb": peak_memory_kb,
          "tool_calls": total_tool_calls,
          "answer_length": response.len(),
          "input_tokens": usage.input_tokens,
          "output_tokens": usage.output_tokens,
          "total_tokens": usage.total_tokens,
          "eval_accuracy": eval.accuracy,
          "eval_completeness": eval.completeness,
          "eval_reasoning": eval.reasoning,
      }))
}

// ── Rate-limit retry helper ───────────────────────────────────────────────

fn parse_retry_after(err_msg: &str) -> u64 {
    for word in err_msg.split_whitespace() {
        if let Ok(n) = word.trim_matches(|c: char| !c.is_ascii_digit()).parse::<u64>() {
            if n > 0 && n < 3600 {
                return n;
            }
        }
    }
    60
}

// ── Main ──────────────────────────────────────────────────────────────────

#[tokio::main]
async fn main() -> Result<()> {
    let cfg = Config::from_env();

    let api_key = std::env::var("OPENROUTER_API_KEY")
        .map_err(|_| anyhow::anyhow!("OPENROUTER_API_KEY environment variable is not set"))?;

    println!("Building agent ({})...", cfg.model);
    println!("Running {} benchmark run(s) in parallel...", cfg.runs);

    let mut set = tokio::task::JoinSet::new();
    for i in 1..=cfg.runs {
        let api_key = api_key.clone();
        let model = cfg.model.clone();
        set.spawn(async move { run_once(i, api_key, model).await });
    }

    let mut records: Vec<serde_json::Value> = Vec::new();
    while let Some(result) = set.join_next().await {
        records.push(result??);
    }
    records.sort_by_key(|r| r["run"].as_u64().unwrap_or(0));

    // Write JSONL output
    if let Some(parent) = cfg.output.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let content = records
        .iter()
        .map(|r| r.to_string())
        .collect::<Vec<_>>()
        .join("\n")
        + "\n";
    std::fs::write(&cfg.output, content)?;

    let latencies: Vec<f64> = records
        .iter()
        .map(|r| r["latency_ms"].as_f64().unwrap_or(0.0))
        .collect();
    let accuracies: Vec<i64> = records
        .iter()
        .filter_map(|r| r["eval_accuracy"].as_i64())
        .filter(|&v| v >= 0)
        .collect();
    let completeness: Vec<i64> = records
        .iter()
        .filter_map(|r| r["eval_completeness"].as_i64())
        .filter(|&v| v >= 0)
        .collect();

    let n = latencies.len() as f64;
    println!("\nSummary ({} runs):", cfg.runs);
    println!("  Avg latency    : {:.1} ms", latencies.iter().sum::<f64>() / n);
    println!("  Min latency    : {:.1} ms", latencies.iter().cloned().fold(f64::INFINITY, f64::min));
    println!("  Max latency    : {:.1} ms", latencies.iter().cloned().fold(f64::NEG_INFINITY, f64::max));
    if !accuracies.is_empty() {
        println!("  Avg accuracy   : {:.1} / 5", accuracies.iter().sum::<i64>() as f64 / accuracies.len() as f64);
    }
    if !completeness.is_empty() {
        println!("  Avg completeness: {:.1} / 5", completeness.iter().sum::<i64>() as f64 / completeness.len() as f64);
    }
    println!("\nResults written to: {}", cfg.output.display());

    Ok(())
}