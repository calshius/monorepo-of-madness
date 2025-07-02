import os
import csv
import json
import asyncio
from data_pipeline_agent.utils.retry import retry_llm_call

def parse_partial_json(json_content):
    try:
        parsed = json.loads(json_content)
        return parsed, True
    except Exception:
        objects = []
        buffer = ""
        in_object = False
        for char in json_content:
            if char == "{":
                in_object = True
                buffer = "{"
            elif char == "}" and in_object:
                buffer += "}"
                try:
                    obj = json.loads(buffer)
                    objects.append(obj)
                except Exception:
                    break
                in_object = False
                buffer = ""
            elif in_object:
                buffer += char
        return objects, False

def fix_llm_json_object(obj):
    import ast
    if "location" in obj:
        loc = obj["location"]
        if isinstance(loc, list) and len(loc) == 2:
            obj["town"], obj["area"] = loc
        elif isinstance(loc, str) and "," in loc:
            parts = [x.strip() for x in loc.split(",")]
            if len(parts) == 2:
                obj["town"], obj["area"] = parts
        elif isinstance(loc, str) and loc.startswith("["):
            try:
                loc_list = ast.literal_eval(loc)
                if isinstance(loc_list, list) and len(loc_list) == 2:
                    obj["town"], obj["area"] = loc_list
            except Exception:
                pass
        del obj["location"]
    if "description" in obj:
        desc = obj["description"]
        if isinstance(desc, list):
            obj["incident"] = " ".join(desc)
        elif isinstance(desc, str) and desc.startswith("["):
            try:
                desc_list = ast.literal_eval(desc)
                if isinstance(desc_list, list):
                    obj["incident"] = " ".join(desc_list)
                else:
                    obj["incident"] = desc
            except Exception:
                obj["incident"] = desc
        else:
            obj["incident"] = desc
        del obj["description"]
    if "witnesses" in obj:
        wit = obj["witnesses"]
        if isinstance(wit, list):
            obj["occupation"] = ", ".join(wit)
        elif isinstance(wit, str) and wit.startswith("["):
            try:
                wit_list = ast.literal_eval(wit)
                if isinstance(wit_list, list):
                    obj["occupation"] = ", ".join(wit_list)
                else:
                    obj["occupation"] = wit
            except Exception:
                obj["occupation"] = wit
        else:
            obj["occupation"] = wit
        del obj["witnesses"]
    keys = ["area", "coordinates", "date", "id", "incident", "town", "time", "occupation"]
    for k in keys:
        obj.setdefault(k, "")
    if isinstance(obj["time"], str) and obj["time"].startswith("["):
        try:
            t = ast.literal_eval(obj["time"])
            if isinstance(t, list) and t:
                obj["time"] = t[0]
        except Exception:
            pass
    coords = obj.get("coordinates", ["NA", "NA"])
    if isinstance(coords, str):
        try:
            coords_list = ast.literal_eval(coords)
            if isinstance(coords_list, list) and len(coords_list) == 2:
                obj["coordinates"] = [str(coords_list[0]), str(coords_list[1])]
            else:
                obj["coordinates"] = ["NA", "NA"]
        except Exception:
            obj["coordinates"] = ["NA", "NA"]
    elif isinstance(coords, list) and len(coords) == 2:
        obj["coordinates"] = [str(coords[0]), str(coords[1])]
    else:
        obj["coordinates"] = ["NA", "NA"]
    obj["id"] = str(obj.get("id", ""))
    return {k: obj[k] for k in keys}

async def process_geo_csv(idx, geo_csv, total, llm, example):
    print(f"[{idx}/{total}] Processing geolocated CSV: {geo_csv}")
    with open(geo_csv, newline="") as csvfile:
        csv_data = csvfile.read()
        csvfile.seek(0)
        reader = list(csv.DictReader(csvfile))
    prompt = (
        "You are a data transformation assistant. Given the following CSV of UK UFO sightings, "
        "output a JSON array where each object has keys: area, coordinates (as a list of two strings), "
        "date, id (leave blank), incident, town, time, occupation. "
        "For each CSV row, create exactly one JSON object, preserving all values exactly as they appear. "
        "Do NOT drop, merge, or summarize any rows. "
        "The output JSON array MUST have the same number of objects as the input CSV rows. "
        "Do NOT invent or hallucinate data. "
        "Do NOT change or reformat any existing data fields. "
        "If a value is missing, use an empty string or [\"NA\", \"NA\"] for coordinates. "
        "Make sure there are no spaces in the coordinates values.\n\n"
        "Here is an example of the correct structure:\n"
        f"{json.dumps(example, indent=2)}\n"
        f"CSV:\n{csv_data}\n\nJSON:"
    )
    response = await retry_llm_call(lambda: llm.ainvoke(prompt))
    json_content = response.content if hasattr(response, "content") else str(response)
    parsed_objects, _ = parse_partial_json(json_content)
    parsed_objects = [fix_llm_json_object(obj) for obj in parsed_objects]
    print(f"[{idx}/{total}] Appended {len(parsed_objects)} objects from {geo_csv}")
    return parsed_objects

async def to_json_node(state):
    geo_csv_paths = state.get("geo_csv_paths", [])
    llm = state["llm"]
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../..")
    )
    json_path = os.path.join(project_root, "uk_map/src/data/sighting_geos.json")
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    all_objects = []

    example = {
        "area": "Manchester",
        "coordinates": ["53.5333", "-2.4500"],
        "date": "16-Feb-09",
        "id": "",
        "incident": "A dome shaped orange ball of light. It suddenly took off from a field. It was organic like a jellyfish. Transparent, and you could see its internal workings. It departed swaying left to right and made a droning noise. 150-200ft in the air.",
        "town": "Leigh",
        "time": "19:19",
        "occupation": "Not Given"
    }

    print(f"Found {len(geo_csv_paths)} geolocated CSV file(s) to convert to JSON.")

    tasks = [
        process_geo_csv(idx, geo_csv, len(geo_csv_paths), llm, example)
        for idx, geo_csv in enumerate(geo_csv_paths, 1)
    ]
    results = await asyncio.gather(*tasks)
    for objs in results:
        all_objects.extend(objs)

    # Write all objects to the final JSON file
    with open(json_path, "w") as jsonfile:
        json.dump(all_objects, jsonfile, indent=2)
    print(f"Wrote {len(all_objects)} objects to {json_path}")
    return {**state, "json_path": json_path}