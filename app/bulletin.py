import json
from datetime import datetime, timedelta
import pytz
from typing import Dict, Any, List

from app.database import get_latest_readings, get_reading_at_time
from app.config import load_config

BULLETIN_FILE = "bulletin.json"

def generate_bulletin():
    """Generates an hourly bulletin summarizing Red/Amber statuses and changes."""
    config = load_config()
    current_time_utc = datetime.now(pytz.utc)
    one_hour_ago_utc = current_time_utc - timedelta(hours=1)
    
    current_readings = get_latest_readings()
    
    # Organize current by measure_id
    current_map = {r["measure_id"]: r for r in current_readings}
    
    bulletin_data: Dict[str, Any] = {
        "generated_at": current_time_utc.isoformat(),
        "amber_red_stations": [],
        "changes": []
    }
    
    for station in config.stations:
        measure_id = station.measure_id
        current = current_map.get(measure_id)
        if not current:
            continue
            
        current_status = current["status"]
        if current_status in ["Amber", "Red"]:
            bulletin_data["amber_red_stations"].append({
                "name": station.name,
                "measure_id": measure_id,
                "status": current_status,
                "value": current["value"],
                "timestamp": current["timestamp"]
            })
            
        # Get reading from ~1 hour ago
        previous = get_reading_at_time(
            measure_id=measure_id, 
            max_timestamp=one_hour_ago_utc.isoformat()
        )
        
        prev_status = previous["status"] if previous else "Unknown"
        
        if prev_status != current_status and prev_status != "Unknown":
            bulletin_data["changes"].append({
                "name": station.name,
                "measure_id": measure_id,
                "previous_status": prev_status,
                "current_status": current_status
            })
            
    # Save the bulletin to a file so FastAPI can easily serve the latest one
    with open(BULLETIN_FILE, "w") as f:
        json.dump(bulletin_data, f, indent=2)
        
    return bulletin_data

def get_latest_bulletin() -> Dict[str, Any]:
    try:
        with open(BULLETIN_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"status": "No bulletin generated yet."}

def check_bulletin_hourly():
    """Wrapper to be called by APScheduler"""
    generate_bulletin()
