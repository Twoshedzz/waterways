from fastapi import FastAPI, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
from typing import Optional

from app.config import load_config
from app.database import init_db, get_latest_readings
from app.fetcher import run_fetch_cycle
from app.bulletin import check_bulletin_hourly, get_latest_bulletin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config once on startup
app_config = load_config()

# Setup Scheduler
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    init_db()
    
    # Scheduler Setup
    scheduler.add_job(
        run_fetch_cycle, 
        'interval', 
        minutes=15, 
        args=[app_config], 
        id='fetch_data'
    )
    scheduler.add_job(
        check_bulletin_hourly, 
        'interval', 
        hours=1, 
        id='generate_bulletin'
    )
    scheduler.start()
    
    # Run an initial fetch and bulletin on startup
    await run_fetch_cycle(app_config)
    check_bulletin_hourly()
    
    yield
    
    # Shutdown Scheduler
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    readings = get_latest_readings()
    return templates.TemplateResponse(
        request=request, name="index.html", context={"readings": readings}
    )

@app.get("/api/rivers")
async def api_rivers():
    """Returns a list of all rivers that have data, with station counts."""
    readings = get_latest_readings()
    river_counts = {}
    for r in readings:
        river = r.get("river", "Unknown")
        if river not in river_counts:
            river_counts[river] = set()
        river_counts[river].add(r["name"])
    
    rivers = sorted([
        {"name": river, "station_count": len(names)}
        for river, names in river_counts.items()
        if river  # skip empty strings
    ], key=lambda x: x["name"])
    return rivers

@app.get("/api/status")
async def api_status(river: Optional[str] = Query(None, description="Filter by river name")):
    readings = get_latest_readings()
    
    # Filter by river if specified
    if river:
        readings = [r for r in readings if r.get("river") == river]
    
    # Group readings by station name
    stations = {}
    
    for r in readings:
        key = r["name"]
        
        if key not in stations:
            stations[key] = {
                "lat": r.get("lat"),
                "long": r.get("long"),
                "name": key,
                "river": r.get("river", ""),
                "readings": [],
                "worst_status": "Green",
                "_seen_types": set()
            }
            
        # Only add one reading per type (e.g. one level, one flow)
        if r["type"] not in stations[key]["_seen_types"]:
            stations[key]["_seen_types"].add(r["type"])
            stations[key]["readings"].append({
                "measure_id": r["measure_id"],
                "type": r["type"],
                "value": r["value"],
                "status": r["status"],
                "timestamp": r["timestamp"],
                "name": r["name"],
                "trend": r.get("trend", "Steady")
            })
        
        # Calculate worst status for the marker color
        curr_worst = stations[key]["worst_status"]
        if r["status"] == "Red":
             stations[key]["worst_status"] = "Red"
        elif r["status"] == "Amber" and curr_worst != "Red":
             stations[key]["worst_status"] = "Amber"
             
    # Remove the temporary _seen_types loop tracker
    for s in stations.values():
        s.pop("_seen_types", None)
        
    # Sort alphabetically by name
    sorted_stations = sorted(stations.values(), key=lambda x: x["name"])
    return sorted_stations

@app.get("/api/bulletin")
async def api_bulletin():
    return get_latest_bulletin()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

