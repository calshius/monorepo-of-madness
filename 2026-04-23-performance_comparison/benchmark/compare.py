"""Compare Python LangGraph vs Rust rig benchmark results across multiple models.

Reads benchmark/results/python_results_<slug>.jsonl and rust_results_<slug>.jsonl
for each model, then generates a multi-model HTML report with Chart.js.

Usage:
    python3 compare.py [--html]
"""

import argparse
import json
import sys
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"

# Models: (openrouter_id, display_name, hex_color)
MODELS = [
    ("openai/gpt-5.4", "GPT-5.4", "#3b82f6"),
    ("anthropic/claude-sonnet-4.6", "Claude Sonnet 4.6", "#10b981"),
    ("google/gemini-3.1-pro-preview", "Gemini 3.1 Pro Preview", "#f97316"),
]


def model_slug(model: str) -> str:
    return model.split("/")[-1].split(":")[0]


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def avg(records: list[dict], key: str) -> float:
    vals = [r[key] for r in records if key in r and r[key] is not None and r[key] >= 0]
    return round(sum(vals) / len(vals), 1) if vals else 0.0


def load_all() -> dict:
    """Return {slug: {display, color, python: [...], rust: [...]}} for models with data."""
    result = {}
    for model_id, display, color in MODELS:
        slug = model_slug(model_id)
        py = load_jsonl(RESULTS_DIR / f"python_results_{slug}.jsonl")
        rs = load_jsonl(RESULTS_DIR / f"rust_results_{slug}.jsonl")
        if py or rs:
            result[slug] = {"display": display, "color": color, "python": py, "rust": rs}
    return result


def print_table(all_data: dict) -> None:
    col = 12
    print()
    header = f"{'Model':<22} {'Agent':<8} {'Lat avg':>{col}} {'Tok avg':>{col}} {'Acc avg':>{col}} {'Comp avg':>{col}}"
    print(header)
    print("-" * len(header))
    for slug, d in all_data.items():
        for agent, records in [("Python", d["python"]), ("Rust", d["rust"])]:
            if not records:
                continue
            print(
                f"{d['display']:<22} {agent:<8} "
                f"{avg(records,'latency_ms'):>{col}.1f} "
                f"{avg(records,'total_tokens'):>{col}.1f} "
                f"{avg(records,'eval_accuracy'):>{col}.1f} "
                f"{avg(records,'eval_completeness'):>{col}.1f}"
            )
    print()


def save_html(all_data: dict) -> None:
    import json as _json

    if not all_data:
        print("No data to report.", file=sys.stderr)
        return

    labels = [d["display"] for d in all_data.values()]
    colors = [d["color"] for d in all_data.values()]

    # Build dataset arrays: one value per model
    py_lat  = [avg(d["python"], "latency_ms")        for d in all_data.values()]
    rs_lat  = [avg(d["rust"],   "latency_ms")        for d in all_data.values()]
    py_tok  = [avg(d["python"], "total_tokens")      for d in all_data.values()]
    rs_tok  = [avg(d["rust"],   "total_tokens")      for d in all_data.values()]
    py_acc  = [avg(d["python"], "eval_accuracy")     for d in all_data.values()]
    rs_acc  = [avg(d["rust"],   "eval_accuracy")     for d in all_data.values()]
    py_comp = [avg(d["python"], "eval_completeness") for d in all_data.values()]
    rs_comp = [avg(d["rust"],   "eval_completeness") for d in all_data.values()]

    total_runs_py = sum(len(d["python"]) for d in all_data.values())
    total_runs_rs = sum(len(d["rust"])   for d in all_data.values())

    # Build per-model per-run line data for latency sparklines
    per_model_py_lat = {slug: [round(r.get("latency_ms", 0), 1) for r in d["python"]]
                        for slug, d in all_data.items()}
    per_model_rs_lat = {slug: [round(r.get("latency_ms", 0), 1) for r in d["rust"]]
                        for slug, d in all_data.items()}

    # Summary table rows
    table_rows = []
    for slug, d in all_data.items():
        for agent_label, records in [("Python", d["python"]), ("Rust", d["rust"])]:
            if not records:
                continue
            table_rows.append((
                d["display"], agent_label,
                avg(records, "latency_ms"),
                avg(records, "total_tokens"),
                avg(records, "eval_accuracy"),
                avg(records, "eval_completeness"),
                len(records),
            ))

    table_html = "\n".join(
        f"<tr><td>{m}</td><td>{a}</td><td>{lat:.1f}</td><td>{tok:.1f}</td>"
        f"<td>{acc:.1f}/5</td><td>{comp:.1f}/5</td><td>{n}</td></tr>"
        for m, a, lat, tok, acc, comp, n in table_rows
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Multi-Model Benchmark — LangGraph vs rig</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0f172a; color: #e2e8f0; margin: 0; padding: 2rem;
    }}
    h1 {{ font-size: 1.8rem; margin-bottom: 0.25rem; }}
    .subtitle {{ color: #94a3b8; margin-bottom: 2rem; font-size: 0.9rem; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem; }}
    .grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem; }}
    .card {{
      background: #1e293b; border-radius: 12px; padding: 1.5rem;
      border: 1px solid #334155;
    }}
    .card h2 {{ font-size: 0.9rem; color: #94a3b8; margin: 0 0 1rem; text-transform: uppercase; letter-spacing: 0.05em; }}
    canvas {{ max-height: 300px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
    th {{ text-align: left; padding: 0.6rem 0.75rem; color: #94a3b8; border-bottom: 1px solid #334155; }}
    td {{ padding: 0.55rem 0.75rem; border-bottom: 1px solid #1e293b; }}
    tr:nth-child(even) td {{ background: #162032; }}
    .note {{ color: #64748b; font-size: 0.78rem; margin-top: 1rem; }}
    .legend {{ display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem; font-size: 0.85rem; }}
    .dot {{ width: 12px; height: 12px; border-radius: 50%; display: inline-block; margin-right: 6px; }}
  </style>
</head>
<body>
  <h1>Multi-Model Benchmark: Python (LangGraph) vs Rust (rig)</h1>
  <p class="subtitle">
    Task: "What is photosynthesis?" — {len(all_data)} free OpenRouter models — parallel runs —
    {total_runs_py} Python / {total_runs_rs} Rust runs total
  </p>

  <div class="legend">
    <strong style="color:#94a3b8">Models:</strong>
    {" ".join(f'<span><span class="dot" style="background:{d["color"]}"></span>{d["display"]}</span>' for d in all_data.values())}
  </div>

  <div class="grid">
    <div class="card">
      <h2>Avg Latency (ms) — Python</h2>
      <canvas id="pyLatChart"></canvas>
    </div>
    <div class="card">
      <h2>Avg Latency (ms) — Rust</h2>
      <canvas id="rsLatChart"></canvas>
    </div>
  </div>

  <div class="grid">
    <div class="card">
      <h2>Avg Total Tokens — Python</h2>
      <canvas id="pyTokChart"></canvas>
    </div>
    <div class="card">
      <h2>Avg Total Tokens — Rust</h2>
      <canvas id="rsTokChart"></canvas>
    </div>
  </div>

  <div class="grid">
    <div class="card">
      <h2>Latency per run — Python (ms)</h2>
      <canvas id="pyLatLine"></canvas>
    </div>
    <div class="card">
      <h2>Latency per run — Rust (ms)</h2>
      <canvas id="rsLatLine"></canvas>
    </div>
  </div>

  <div class="grid">
    <div class="card">
      <h2>Eval Accuracy (/5)</h2>
      <canvas id="accChart"></canvas>
    </div>
    <div class="card">
      <h2>Eval Completeness (/5)</h2>
      <canvas id="compChart"></canvas>
    </div>
  </div>

  <div class="card">
    <h2>Summary Table</h2>
    <table>
      <thead>
        <tr><th>Model</th><th>Agent</th><th>Avg Latency (ms)</th><th>Avg Tokens</th>
            <th>Avg Accuracy</th><th>Avg Completeness</th><th>Runs</th></tr>
      </thead>
      <tbody>{table_html}</tbody>
    </table>
    <p class="note">Runs executed in parallel within each agent. Latency = wall-clock time per individual run.</p>
  </div>

  <script>
    const labels  = {_json.dumps(labels)};
    const colors  = {_json.dumps(colors)};
    const pyLat   = {_json.dumps(py_lat)};
    const rsLat   = {_json.dumps(rs_lat)};
    const pyTok   = {_json.dumps(py_tok)};
    const rsTok   = {_json.dumps(rs_tok)};
    const pyAcc   = {_json.dumps(py_acc)};
    const rsAcc   = {_json.dumps(rs_acc)};
    const pyComp  = {_json.dumps(py_comp)};
    const rsComp  = {_json.dumps(rs_comp)};
    const perModelPyLat = {_json.dumps(per_model_py_lat)};
    const perModelRsLat = {_json.dumps(per_model_rs_lat)};
    const slugs   = {_json.dumps(list(all_data.keys()))};

    const AXIS = {{
      x: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#1e293b' }} }},
      y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }},
    }};

    function barChart(id, vals, yLabel) {{
      new Chart(document.getElementById(id), {{
        type: 'bar',
        data: {{
          labels,
          datasets: [{{ data: vals, backgroundColor: colors, borderRadius: 6 }}]
        }},
        options: {{
          responsive: true,
          plugins: {{ legend: {{ display: false }} }},
          scales: {{
            x: AXIS.x,
            y: {{ ...AXIS.y, title: {{ display: true, text: yLabel, color: '#94a3b8' }} }}
          }}
        }}
      }});
    }}

    function groupedBar(id, pyVals, rsVals, yLabel, yMax) {{
      new Chart(document.getElementById(id), {{
        type: 'bar',
        data: {{
          labels,
          datasets: [
            {{ label: 'Python', data: pyVals, backgroundColor: colors.map(c => c + 'cc'), borderRadius: 4 }},
            {{ label: 'Rust',   data: rsVals, backgroundColor: colors.map(c => c + '66'),
               borderColor: colors, borderWidth: 2, borderRadius: 4 }},
          ]
        }},
        options: {{
          responsive: true,
          plugins: {{ legend: {{ labels: {{ color: '#e2e8f0' }} }} }},
          scales: {{
            x: AXIS.x,
            y: {{ ...AXIS.y,
              ...(yMax ? {{ min: 0, max: yMax }} : {{}}),
              title: {{ display: true, text: yLabel, color: '#94a3b8' }}
            }}
          }}
        }}
      }});
    }}

    function lineChart(id, perModel, yLabel) {{
      const datasets = slugs.map((slug, i) => ({{
        label: labels[i],
        data: perModel[slug] || [],
        borderColor: colors[i],
        backgroundColor: colors[i] + '33',
        pointRadius: 3,
        tension: 0.3,
      }}));
      const maxRuns = Math.max(...slugs.map(s => (perModel[s] || []).length));
      new Chart(document.getElementById(id), {{
        type: 'line',
        data: {{
          labels: Array.from({{length: maxRuns}}, (_, i) => i + 1),
          datasets,
        }},
        options: {{
          responsive: true,
          plugins: {{ legend: {{ labels: {{ color: '#e2e8f0' }} }} }},
          scales: {{
            x: {{ ...AXIS.x, title: {{ display: true, text: 'Run #', color: '#94a3b8' }} }},
            y: {{ ...AXIS.y, title: {{ display: true, text: yLabel, color: '#94a3b8' }} }}
          }}
        }}
      }});
    }}

    barChart('pyLatChart', pyLat, 'ms');
    barChart('rsLatChart', rsLat, 'ms');
    barChart('pyTokChart', pyTok, 'tokens');
    barChart('rsTokChart', rsTok, 'tokens');
    groupedBar('accChart',  pyAcc,  rsAcc,  'Score / 5', 5);
    groupedBar('compChart', pyComp, rsComp, 'Score / 5', 5);
    lineChart('pyLatLine', perModelPyLat, 'ms');
    lineChart('rsLatLine', perModelRsLat, 'ms');
  </script>
</body>
</html>
"""

    out_path = RESULTS_DIR / "report.html"
    out_path.write_text(html)
    print(f"HTML report saved to: {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare multi-model benchmark results")
    parser.add_argument("--html", action="store_true", help="Generate an HTML report with charts")
    args = parser.parse_args()

    all_data = load_all()
    if not all_data:
        print("No results found. Run ./run.sh first.")
        sys.exit(1)

    print_table(all_data)

    if args.html:
        save_html(all_data)


if __name__ == "__main__":
    main()
