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

async def process_csv(idx, csv_path, total, llm, temp_dir):
    print(f"[{idx}/{total}] Processing CSV: {csv_path}")
    with open(csv_path, newline="") as infile:
        csv_data = infile.read()
        infile.seek(0)
        original_rows = list(csv.DictReader(infile))

    prompt = (
        "You are a data cleaning and enrichment assistant. Given the following CSV of UK UFO sightings, "
        "add a new column called 'coordinates' containing a list: [latitude, longitude] as strings, "
        "using best-effort geolocation for each row based on the 'town' and 'area' columns (UK only). "
        "If location is unknown, use ['NA', 'NA']. "
        "Make sure the co0ordinates are in the format ['latitude', 'longitude'] with no spaces in the values. "
        "Return the result as CSV with ALL the original columns (date, time, town, area, occupation, incident) "
        "PLUS the new coordinates column. "
        "Do NOT drop, merge, or summarize any rows. "
        "The output CSV MUST have the same number of rows as the input. "
        "Do NOT invent or hallucinate data. "
        "Do NOT change or reformat any existing data fields.\n\n"
        f"CSV:\n{csv_data}\n\nCleaned CSV:"
    )
    response = await retry_llm_call(lambda: llm.ainvoke(prompt))
    cleaned_csv = response.content if hasattr(response, "content") else str(response)
    rows = parse_csv_rows(cleaned_csv)
    print(f"[{idx}/{total}] LLM returned {len(rows)} geolocated row(s).")
    # Retry logic if output is incomplete
    if len(rows) < len(original_rows):
        print(f"[{idx}/{total}] LLM output incomplete for {csv_path}, retrying...")
        retry_response = await retry_llm_call(lambda: llm.ainvoke(prompt))
        retry_cleaned_csv = retry_response.content if hasattr(retry_response, "content") else str(retry_response)
        retry_rows = parse_csv_rows(retry_cleaned_csv)
        print(f"[{idx}/{total}] LLM retry returned {len(retry_rows)} additional row(s).")
        rows += [r for r in retry_rows if r not in rows]
    if rows:
        geo_csv_path = os.path.join(temp_dir, f"{os.path.splitext(os.path.basename(csv_path))[0]}_geolocated.csv")
        with open(geo_csv_path, "w", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"[{idx}/{total}] Wrote {len(rows)} geolocated rows to {geo_csv_path}")
        return geo_csv_path
    else:
        print(f"[{idx}/{total}] No geolocated rows extracted for {csv_path}.")
        return None

async def transpose_node(state):
    csv_paths = state.get("csv_paths", [])
    llm = state["llm"]
    temp_dir = tempfile.gettempdir()

    print(f"Found {len(csv_paths)} CSV file(s) to geolocate.")

    tasks = [
        process_csv(idx, csv_path, len(csv_paths), llm, temp_dir)
        for idx, csv_path in enumerate(csv_paths, 1)
    ]
    geo_csv_paths = [result for result in await asyncio.gather(*tasks) if result]

    print(f"Finished geolocating. {len(geo_csv_paths)} geolocated CSV file(s) created.")
    return {**state, "geo_csv_paths": geo_csv_paths}