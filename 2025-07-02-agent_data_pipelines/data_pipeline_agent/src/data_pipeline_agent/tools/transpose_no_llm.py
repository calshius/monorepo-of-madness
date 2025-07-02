import csv
import os
import tempfile
import asyncio
from data_pipeline_agent.utils.geo_utils import lookup_lat_lon

async def process_csv(idx, csv_path, total, temp_dir):
    print(f"[{idx}/{total}] Transposing and geolocating {csv_path}...")
    output_csv = os.path.join(temp_dir, f"{os.path.splitext(os.path.basename(csv_path))[0]}_geolocated.csv")
    with open(csv_path, newline="") as infile, open(output_csv, "w", newline="") as outfile:
        reader = csv.DictReader(infile)
        fieldnames = [
            "date",
            "time",
            "town",
            "area",
            "occupation",
            "incident",
            "coordinates",
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            date = row.get("Date", "") or row.get("date", "")
            time = row.get("Time", "") or row.get("time", "")
            town = row.get("Town / Village", "") or row.get("town", "")
            area = row.get("Area", "") or row.get("area", "")
            occupation = row.get("Occupation (Where Relevant)", "") or row.get("occupation", "")
            incident = row.get("Description", "") or row.get("incident", "")
            lat, lon = await lookup_lat_lon(town, area)
            writer.writerow(
                {
                    "date": date,
                    "time": time,
                    "town": town,
                    "area": area,
                    "occupation": occupation,
                    "incident": incident,
                    "coordinates": f'["{lat}", "{lon}"]',
                }
            )
    print(f"[{idx}/{total}] Wrote geolocated CSV to {output_csv}")
    return output_csv

async def transpose_node(state):
    csv_paths = state.get("csv_paths", [])
    temp_dir = tempfile.gettempdir()
    print(f"Found {len(csv_paths)} CSV file(s) to geolocate (no LLM).")
    tasks = [
        process_csv(idx, csv_path, len(csv_paths), temp_dir)
        for idx, csv_path in enumerate(csv_paths, 1)
    ]
    geo_csv_paths = [result for result in await asyncio.gather(*tasks) if result]
    print(f"Finished geolocating. {len(geo_csv_paths)} geolocated CSV file(s) created.")
    return {**state, "geo_csv_paths": geo_csv_paths}