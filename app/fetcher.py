import httpx
import asyncio
from datetime import datetime
import pytz
from typing import Optional, Dict, Any, List
import logging

from app.config import AppConfig, StationConfig, Thresholds
from app.database import insert_reading
from app.bulletin import check_bulletin_hourly

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def determine_status(value: float, thresholds: Thresholds) -> str:
    """Determine status based on thresholds."""
    if value >= thresholds.red:
        return "Red"
    elif value >= thresholds.amber:
        return "Amber"
    return "Green"

async def fetch_station_data(client: httpx.AsyncClient, station: StationConfig):
    url = f"https://environment.data.gov.uk/flood-monitoring/id/measures/{station.measure_id}/readings?_limit=2&_sorted"
    try:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        items = data.get("items", [])
        if not items:
            logger.warning(f"No recent readings found for {station.measure_id}")
            return
        
        # Limit=2 returns up to 2 items sorted natively descending by dateTime
        latest = items[0]
        
        timestamp = latest.get("dateTime")
        value = latest.get("value")
        
        if value is None or not timestamp:
            logger.warning(f"Missing value or timestamp for {station.measure_id}")
            return
            
        status = determine_status(value, station.thresholds)
        
        # Calculate Trend
        trend = "Steady"
        if len(items) > 1:
            prev_value = items[1].get("value")
            if prev_value is not None:
                if value > prev_value:
                    trend = "Rising"
                elif value < prev_value:
                    trend = "Falling"
        
        insert_reading(
            measure_id=station.measure_id,
            timestamp=timestamp,
            value=value,
            status=status,
            name=station.name,
            type=station.type,
            lat=station.lat,
            long=station.long,
            trend=trend,
            river=station.river
        )
        logger.info(f"Recorded {station.river}/{station.name} at {timestamp}: {value} ({status}) [{trend}]")
        
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching data for {station.measure_id}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error fetching data for {station.measure_id}: {e}")

# Semaphore to limit concurrent EA API requests
FETCH_SEMAPHORE = asyncio.Semaphore(10)

async def _fetch_with_semaphore(client: httpx.AsyncClient, station: StationConfig):
    async with FETCH_SEMAPHORE:
        await fetch_station_data(client, station)

async def run_fetch_cycle(config: AppConfig):
    """Fetches data for all configured stations concurrently and evaluates alert status."""
    logger.info(f"Starting fetch cycle for {len(config.stations)} stations")
    async with httpx.AsyncClient() as client:
        tasks = [_fetch_with_semaphore(client, station) for station in config.stations]
        await asyncio.gather(*tasks)
    logger.info("Finished fetch cycle")
