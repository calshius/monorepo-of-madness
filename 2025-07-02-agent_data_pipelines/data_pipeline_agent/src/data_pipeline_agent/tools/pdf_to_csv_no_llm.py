import pdfplumber
import csv
import os
import tempfile
import asyncio

async def process_pdf(idx, pdf_path, total, temp_dir):
    if not pdf_path or not os.path.exists(pdf_path):
        print(f"[{idx}/{total}] Skipping missing PDF: {pdf_path}")
        return None
    print(f"[{idx}/{total}] Extracting tables from {pdf_path}...")
    csv_path = os.path.join(temp_dir, f"{os.path.splitext(os.path.basename(pdf_path))[0]}.csv")
    with pdfplumber.open(pdf_path) as pdf, open(csv_path, "w", newline="") as csvfile:
        writer = None
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                if writer is None:
                    writer = csv.writer(csvfile)
                    writer.writerow(table[0])
                for row in table[1:]:
                    writer.writerow(row)
    print(f"[{idx}/{total}] Wrote CSV to {csv_path}")
    return csv_path

async def pdf_to_csv_node(state):
    pdf_files = state.get("pdf_files")
    if not pdf_files:
        pdf_files = [state.get("pdf_path")]
    temp_dir = tempfile.gettempdir()
    print(f"Found {len(pdf_files)} PDF(s) to process (no LLM).")
    tasks = [
        process_pdf(idx, pdf_path, len(pdf_files), temp_dir)
        for idx, pdf_path in enumerate(pdf_files, 1)
    ]
    csv_paths = [result for result in await asyncio.gather(*tasks) if result]
    print(f"Finished processing PDFs. {len(csv_paths)} CSV file(s) created.")
    return {**state, "csv_paths": csv_paths}