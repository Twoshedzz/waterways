import argparse
import json
import sys

# Official lock-to-lock reach order (Teddington -> Oxford)
REACH_LIST = [
    "Teddington",
    "Molesey",
    "Sunbury",
    "Shepperton",
    "Chertsey",
    "Penton Hook",
    "Bell Weir",
    "Old Windsor",
    "Romney",
    "Boveney",
    "Bray",
    "Boulter's",
    "Cookham",
    "Marlow",
    "Temple",
    "Hurley",
    "Hambleden",
    "Marsh",
    "Shiplake",
    "Sonning",
    "Blakes",
    "Caversham",
    "Mapledurham",
    "Whitchurch",
    "Goring",
    "Cleeve",
    "Benson",
    "Days",
    "Clifton",
    "Culham",
    "Abingdon",
    "Sandford",
    "Iffley",
    "Osney"
]

def generate_stub(candidates_file: str, output_file: str):
    """Generates a YAML configuration stub based on the candidate measures and reach list."""
    try:
        with open(candidates_file, "r") as f:
            candidates = json.load(f)
    except FileNotFoundError:
        print(f"Error: Candidates file '{candidates_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not parse '{candidates_file}' as JSON.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Loaded {len(candidates)} candidates from {candidates_file}")
    
    # Grab a couple of random candidates specifically to use as template examples
    # (Optional, but user requested "populated with a few example entries using candidate measure IDs")
    examples = candidates[:2] if len(candidates) >= 2 else candidates
    
    yaml_lines = [
        "# River Status App Configuration",
        "# ------------------------------",
        "# This configuration defines the 'thin slice' of measures to monitor",
        "# for the non-tidal Thames (Teddington to Oxford).",
        "",
        "patch_name: \"Thames (Teddington→Oxford)\"",
        "poll_interval_minutes: 15",
        "compute_interval_minutes: 60",
        "max_age_minutes: 90",
        "",
        "# ------------------------------",
        "# REACHES",
        "# ------------------------------",
        "# These are the official lock-to-lock reach names for this patch.",
        "# Use these EXACT names in the `thin_slice_measures` array below.",
        "reaches:"
    ]
    
    for reach in REACH_LIST:
        yaml_lines.append(f"  - \"{reach}\"")
        
    yaml_lines.extend([
        "",
        "# ------------------------------",
        "# MEASURES (CURATION REQUIRED)",
        "# ------------------------------",
        "# Directions:",
        "# 1. Review the generated `thames_candidates.json` file.",
        "# 2. Find the JSON blocks for the measures you want to track.",
        "# 3. Copy the `measure_id` and map it to the appropriate `reach_name`",
        "#    from the list above.",
        "# 4. Define the Amber and Red thresholds for that measure.",
        "",
        "thin_slice_measures:"
    ])
    
    if examples:
        # Provide commented-out example blocks using real candidate keys
        yaml_lines.append("  # --- EXAMPLES ---")
        for ex in examples:
            yaml_lines.extend([
                f"  # - measure_id: \"{ex['measure_id']}\"",
                f"  #   name: \"{ex['stationLabel']} ({ex['parameterName']} - {ex['qualifier']})\"",
                f"  #   reach_name: \"\" # Fill with a reach from above",
                f"  #   thresholds:",
                f"  #     amber: 0.50",
                f"  #     red:   0.80",
                "  #"
            ])
            
    # Include an active empty array if none are specified yet, but we'll leave it as a list format commented out
    # or just an empty list.
    yaml_lines.append("  []")
    
    with open(output_file, "w") as f:
        f.write("\n".join(yaml_lines) + "\n")
        
    print(f"Generated config stub at {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Thames config stub.")
    parser.add_argument("--candidates", default="thames_candidates.json", help="Input candidates JSON file path")
    parser.add_argument("--out", default="config.thames.teddington-oxford.yaml", help="Output YAML file path")
    args = parser.parse_args()
    
    generate_stub(args.candidates, args.out)
