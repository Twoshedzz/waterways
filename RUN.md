# Running the River Status App

This application fetches data from Environment Agency stations, stores readings locally in SQLite, and provides a real-time summary dashboard.

## Requirements

Ensure you are using Python 3.11+.

```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Web Web server

The application expects `config.json` defining the required slices.

```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## Thames Quick-Start (Teddington to Oxford)

We include a custom patch pack specifically for monitoring the non-tidal River Thames. Here is how to use it:

### 1. Discover Candidate Measures

First, run the discovery helper to query the EA API for all Thames stations exporting level or flow data.

```bash
python -m app.thames_discover --out thames_candidates.json
```

This command produces `thames_candidates.json`, mapping API internals.

### 2. Generate configuration stub

Next, generate a configuration file stub tailored for the 34 lock-to-lock reaches between Teddington and Oxford:

```bash
python -m app.thames_config_stub --candidates thames_candidates.json --out config.thames.teddington-oxford.yaml
```

### 3. Curate the YAML configuration

Open `config.thames.teddington-oxford.yaml`. Inspect `thames_candidates.json` to find the specific `measure_id`s you are interested in.
Populate the `thin_slice_measures` array in the YAML file. Be sure to map each measure to one of the exact `reach_name`s provided in the file and specify the Green/Amber/Red thresholds.
*Note: Our current application core is still hard-coded to read `config.json`, but you can transpile or adapt the application logic to parse YAML later.*

### 4. Run the application

Once your measures are mapped, you can update the main application config parser to load this new YAML slice and view the board!
