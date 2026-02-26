import json

with open("thames_candidates.json", "r") as f:
    candidates = json.load(f)

stations_dict = {}

for c in candidates:
    param = c["parameterName"]
    if param not in ["Flow", "Water Level"]:
        continue
    
    # We only want basic mASD levels, not downstage or arbitrary m/s
    if param == "Water Level" and c.get("qualifier") not in ["Stage"]:
        continue
    if param == "Water Level" and "mASD" not in c["measure_id"] and "----" not in c["measure_id"]:
        continue
        
    s_name = "River Thames at " + c["stationLabel"]
    s_type = "flow" if param == "Flow" else "level"
    
    # Simple thresholds
    thresholds = {"amber": 0.5, "red": 0.8}
    if s_type == "flow":
        thresholds = {"amber": 30.0, "red": 60.0}

    obj = {
        "measure_id": c["measure_id"],
        "name": s_name,
        "type": s_type,
        "lat": c["lat"],
        "long": c["long"],
        "thresholds": thresholds
    }
    
    # De-duplicate by preferring the first one we find per type
    key = f"{s_name}_{s_type}"
    if key not in stations_dict:
        stations_dict[key] = obj

out = {"stations": list(stations_dict.values())}

with open("config.json", "w") as f:
    json.dump(out, f, indent=2)

print(f"Generated {len(out['stations'])} total station sensors.")
