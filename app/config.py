import json
from pathlib import Path
from pydantic import BaseModel
from typing import List

class Thresholds(BaseModel):
    amber: float
    red: float

class StationConfig(BaseModel):
    measure_id: str
    name: str
    type: str = "level" # 'level', 'flow'
    river: str = ""     # e.g. 'River Thames', 'River Cam'
    lat: float = 0.0
    long: float = 0.0
    thresholds: Thresholds

class AppConfig(BaseModel):
    stations: List[StationConfig]

def load_config(path: str = "config.json") -> AppConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {path}")
    
    with open(config_path, "r") as f:
        data = json.load(f)
        
    return AppConfig(**data)
