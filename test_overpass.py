import httpx
import json
import os

instances = [
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "http://overpass-api.de/api/interpreter"
]

overpass_query = """
[out:json];
relation["waterway"="river"]["name"="River Thames"];
out geom;
"""

data = None
for url in instances:
    try:
        print(f"Trying {url}...")
        response = httpx.post(url, data={'data': overpass_query}, timeout=30.0)
        if response.status_code == 200:
            data = response.json()
            if "elements" in data:
                print("Success from", url)
                break
    except Exception as e:
        print(f"Failed: {e}")

if not data:
    print("All overpass queries failed.")
    exit(1)

features = []
for el in data.get('elements', []):
    if el['type'] == 'relation':
        for idx, member in enumerate(el.get('members', [])):
            if member['type'] == 'way' and 'geometry' in member:
                coords = [[pt['lon'], pt['lat']] for pt in member['geometry']]
                features.append({
                    "type": "Feature",
                    "properties": {"index": idx, "role": member.get("role", "")},
                    "geometry": {
                        "type": "LineString",
                        "coordinates": coords
                    }
                })

geojson = {
    "type": "FeatureCollection",
    "features": list(features)
}

os.makedirs("static", exist_ok=True)
with open("static/thames.geojson", "w") as f:
    json.dump(geojson, f)

print(f"Saved {len(features)} lines to static/thames.geojson")
