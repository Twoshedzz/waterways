"""
Multi-river discovery script for EA Navigation Waterways.

Queries the EA Flood Monitoring API for all configured navigation rivers,
filters for level/flow measures, applies exclusion rules, and generates
a complete config.json ready for the app.

Usage:
    python -m app.waterway_discover
    python -m app.waterway_discover --out config.json
"""

import httpx
import json
import argparse
import sys
from typing import List, Dict, Any

# ── EA Navigation Waterways Registry ──────────────────────────────────────────
# Only rivers managed by the Environment Agency for navigation purposes.
# Excludes: Canal & River Trust, Broads Authority, Middle Level Commissioners,
#           Port of London Authority (Thames tidal).

TARGET_RIVERS = [
    "River Thames",
    "River Medway",
    "River Great Ouse",
    "River Nene",
    "River Ancholme",
    "River Welland",
    "River Glen",
    "River Stour",
    "River Cam",
    "River Lark",
    "River Wissey",
    "River Wye",
    "River Lugg",
    "River Rye",
    # "River Lydney"  — 0 results from EA API; may use a different name
]

# ── Exclusion Rules ───────────────────────────────────────────────────────────
# Teddington Lock: approximate lon = -0.322
# Stations EAST of this on the Thames are tidal (Port of London Authority).
TEDDINGTON_LOCK_LON = -0.322

# Allington Lock: approximate lon = 0.493
# Stations EAST of this on the Medway are tidal.
ALLINGTON_LOCK_LON = 0.493


def is_excluded(station: Dict[str, Any], river_name: str) -> bool:
    """Returns True if a station should be excluded based on navigation rules."""
    lon = station.get("long", 0)

    # Thames: exclude tidal section (east of Teddington Lock)
    if river_name == "River Thames" and lon > TEDDINGTON_LOCK_LON:
        return True

    # Medway: exclude tidal section (east of Allington Lock)
    if river_name == "River Medway" and lon > ALLINGTON_LOCK_LON:
        return True

    return False


def default_thresholds(param_type: str) -> Dict[str, float]:
    """Returns sensible default thresholds based on measure type."""
    if param_type == "flow":
        return {"amber": 30.0, "red": 60.0}
    else:  # level
        return {"amber": 0.5, "red": 0.8}


def discover_all_waterways(output_file: str):
    """Fetches stations for all EA navigation rivers and generates config.json."""
    all_stations: List[Dict[str, Any]] = []
    stats = {}

    print(f"Discovering stations for {len(TARGET_RIVERS)} EA navigation rivers...\n")

    for river in TARGET_RIVERS:
        url = "https://environment.data.gov.uk/flood-monitoring/id/stations"
        params = {"riverName": river, "_limit": 1000}

        try:
            response = httpx.get(url, params=params, timeout=15.0)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"  ✗ {river}: ERROR — {e}", file=sys.stderr)
            stats[river] = {"stations": 0, "measures": 0, "excluded": 0}
            continue

        items = data.get("items", [])
        river_measures = 0
        river_excluded = 0

        for station in items:
            # Apply exclusion rules
            if is_excluded(station, river):
                river_excluded += 1
                continue

            measures = station.get("measures", [])
            if isinstance(measures, dict):
                measures = [measures]

            for measure in measures:
                param_key = measure.get("parameter", "")

                if param_key not in ["level", "flow"]:
                    continue

                measure_id = measure.get("@id", "").split("/")[-1]
                if not measure_id:
                    continue

                # Skip non-mASD level measures (avoid duplicates)
                if param_key == "level":
                    unit = measure.get("unitName", "")
                    if "mASD" not in measure_id and "----" not in measure_id:
                        continue

                station_label = station.get("label", "")
                if isinstance(station_label, list):
                    station_label = station_label[0] if station_label else ""

                param_name = measure.get("parameterName", "")
                param_type = "flow" if param_key == "flow" else "level"

                entry = {
                    "measure_id": measure_id,
                    "name": f"{river} at {station_label}",
                    "type": param_type,
                    "river": river,
                    "lat": station.get("lat", 0),
                    "long": station.get("long", 0),
                    "thresholds": default_thresholds(param_type)
                }
                all_stations.append(entry)
                river_measures += 1

        stats[river] = {
            "stations": len(items),
            "measures": river_measures,
            "excluded": river_excluded
        }
        print(f"  ✓ {river}: {len(items)} stations, {river_measures} measures"
              f"{f' ({river_excluded} excluded)' if river_excluded else ''}")

    # Write config
    config = {"stations": all_stations}
    with open(output_file, "w") as f:
        json.dump(config, f, indent=2)

    total_measures = sum(s["measures"] for s in stats.values())
    total_excluded = sum(s["excluded"] for s in stats.values())

    print(f"\n{'─' * 50}")
    print(f"Total: {total_measures} level/flow measures across {len(TARGET_RIVERS)} rivers")
    if total_excluded:
        print(f"Excluded: {total_excluded} tidal/non-navigation stations")
    print(f"Config written to: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Discover EA navigation waterway stations and generate config."
    )
    parser.add_argument(
        "--out", default="config.json",
        help="Output config JSON file path (default: config.json)"
    )
    args = parser.parse_args()
    discover_all_waterways(args.out)
