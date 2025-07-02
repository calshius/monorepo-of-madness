import csv
import json
import os
import asyncio

async def process_geo_csv(idx, geo_csv, total):
    print(f"[{idx}/{total}] Converting {geo_csv} to JSON objects...")
    objects = []
    with open(geo_csv, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            objects.append(
                {
                    "area": row.get("area", ""),
                    "coordinates": json.loads(row.get("coordinates", '["NA", "NA"]')),
                    "date": row.get("date", ""),
                    "id": "",
                    "incident": row.get("incident", ""),
                    "town": row.get("town", ""),
                    "time": row.get("time", ""),
                    "occupation": row.get("occupation", ""),
                }
            )
    print(f"[{idx}/{total}] Found {len(objects)} objects in {geo_csv}")
    return objects

async def to_json_node(state):
    geo_csv_paths = state.get("geo_csv_paths", [])
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../..")
    )
    json_path = os.path.join(project_root, "uk_map/src/data/sighting_geos.json")
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    print(f"Found {len(geo_csv_paths)} geolocated CSV file(s) to convert to JSON (no LLM).")
    tasks = [
        process_geo_csv(idx, geo_csv, len(geo_csv_paths))
        for idx, geo_csv in enumerate(geo_csv_paths, 1)
    ]
    results = await asyncio.gather(*tasks)
    all_objects = []
    for objs in results:
        all_objects.extend(objs)
    with open(json_path, "w") as jsonfile:
        json.dump(all_objects, jsonfile, indent=2)
    print(f"Wrote {len(all_objects)} objects to {json_path}")
    return {**state, "json_path": json_path}