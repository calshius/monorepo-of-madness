import pdfplumber
import os
import tempfile
import csv
import io
import asyncio
from data_pipeline_agent.utils.retry import retry_llm_call

def parse_csv_rows(csv_content):
    try:
        reader = csv.DictReader(io.StringIO(csv_content))
        return list(reader)
    except Exception:
        return []

async def process_pdf(idx, pdf_path, total, llm, temp_dir):
    if not pdf_path or not os.path.exists(pdf_path):
        print(f"[{idx}/{total}] Skipping missing PDF: {pdf_path}")
        return None
    print(f"[{idx}/{total}] Processing PDF: {pdf_path}")
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    print(f"[{idx}/{total}] Extracted text from PDF ({len(text)} characters). Sending to LLM...")
    prompt = (
        "You are a data extraction assistant. Given the following raw text from a UK government UFO report PDF, "
        "extract EVERY sighting that occurred in the United Kingdom. "
        "For each sighting, output a row in CSV with columns: date, time, town, area, occupation, incident. "
        "If a value is missing, use 'Not Given'. "
        "Do NOT invent or hallucinate locations or data. "
        "Do NOT drop or skip any UK sightings. "
        "Do NOT merge or summarize multiple sightings. "
        "Only output the CSV, no explanations, and do not include any non-UK locations.\n\n"
        f"Raw text:\n{text}\n\nCSV:"
    )
    response = await retry_llm_call(lambda: llm.ainvoke(prompt))
    csv_content = response.content if hasattr(response, "content") else str(response)
    rows = parse_csv_rows(csv_content)
    print(f"[{idx}/{total}] LLM returned {len(rows)} row(s).")
    # Retry logic if output is incomplete
    if not rows or len(rows) < 2:
        print(f"[{idx}/{total}] LLM output incomplete for {pdf_path}, retrying...")
        retry_response = await retry_llm_call(lambda: llm.ainvoke(prompt))
        retry_csv_content = retry_response.content if hasattr(retry_response, "content") else str(retry_response)
        retry_rows = parse_csv_rows(retry_csv_content)
        print(f"[{idx}/{total}] LLM retry returned {len(retry_rows)} additional row(s).")
        rows += [r for r in retry_rows if r not in rows]
    if rows:
        # Clean up rows: remove any keys not in fieldnames, ensure all fieldnames are present, and skip rows with None keys
        fieldnames = [k for k in rows[0].keys() if k is not None]
        cleaned_rows = []
        for row in rows:
            cleaned_row = {k: row.get(k, "") for k in fieldnames if k is not None}
            if any(cleaned_row.values()):
                cleaned_rows.append(cleaned_row)
        csv_path = os.path.join(temp_dir, f"{os.path.splitext(os.path.basename(pdf_path))[0]}.csv")
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cleaned_rows)
        print(f"[{idx}/{total}] Wrote {len(cleaned_rows)} rows to {csv_path}")
        return csv_path
    else:
        print(f"[{idx}/{total}] No rows extracted for {pdf_path}.")
        return None

async def pdf_to_csv_node(state):
    pdf_files = state.get("pdf_files")
    if not pdf_files:
        pdf_files = [state.get("pdf_path")]
    llm = state["llm"]
    temp_dir = tempfile.gettempdir()

    print(f"Found {len(pdf_files)} PDF(s) to process.")

    tasks = [
        process_pdf(idx, pdf_path, len(pdf_files), llm, temp_dir)
        for idx, pdf_path in enumerate(pdf_files, 1)
    ]
    csv_paths = [result for result in await asyncio.gather(*tasks) if result]

    print(f"Finished processing PDFs. {len(csv_paths)} CSV file(s) created.")
    return {**state, "csv_paths": csv_paths}