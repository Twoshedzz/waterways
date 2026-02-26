import httpx
import json
import argparse
import sys

def discover_candidates(output_file: str):
    """Fetches Thames stations from the EA API and exports level/flow measures."""
    url = "https://environment.data.gov.uk/flood-monitoring/id/stations"
    params = {
        "riverName": "River Thames",
        "_limit": 1000  # Ensure we get all stations in one page if possible
    }
    
    print(f"Fetching Thames stations from EA API...")
    
    try:
        response = httpx.get(url, params=params, timeout=15.0)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching stations: {e}", file=sys.stderr)
        sys.exit(1)
        
    items = data.get("items", [])
    print(f"Found {len(items)} Thames stations. Fetching measures...")
    
    candidates = []
    
    for station in items:
        measures = station.get("measures", [])
        # The API can return measures as a dict if there's only one, or a list if there are multiple.
        if isinstance(measures, dict):
            measures = [measures]
            
        for measure in measures:
            parameter_key = measure.get("parameter", "")
            
            # Filter for level and flow parameters
            if parameter_key in ["level", "flow"]:
                measure_id = measure.get("@id", "").split("/")[-1]
                station_reference = station.get("stationReference", "")
                station_label = station.get("label", "")
                parameter_name = measure.get("parameterName", "")
                qualifier = measure.get("qualifier", "")
                lat = station.get("lat")
                lon = station.get("long")
                river_name = station.get("riverName", "")
                
                candidate = {
                    "measure_id": measure_id,
                    "stationReference": station_reference,
                    "stationLabel": station_label,
                    "parameterName": parameter_name,
                    "qualifier": qualifier,
                    "lat": lat,
                    "long": lon,
                    "riverName": river_name,
                    "suggested_reach_name": "" # Blank by default
                }
                candidates.append(candidate)
                
    print(f"Extracted {len(candidates)} candidate level/flow measures.")
    
    with open(output_file, "w") as f:
        json.dump(candidates, f, indent=2)
        
    print(f"Candidates exported to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discover Thames candidate measures.")
    parser.add_argument("--out", default="thames_candidates.json", help="Output JSON file path")
    args = parser.parse_args()
    
    discover_candidates(args.out)
