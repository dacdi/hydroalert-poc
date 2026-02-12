
# 🌧️ HydroAlert – Rainfall-Based Water Depth Forecasting

**HydroAlert** is a modular Python tool for spatial flood risk forecasting based on precipitation data.
It combines publicly available weather APIs, raster analysis, and threshold logic to select suitable flash flood maps (e.g., SRI7/SRI10).

---

## 🔧 Current Features (Status: September 2025)

* 📍 Control of **all use cases via coordinates** (`--lat`, `--lon`), including:

  * 📡 Retrieval of hourly precipitation forecasts (24h) from the Open-Meteo API
  * 🗺️ Spatial raster analysis around given locations
  * 🌐 Download of all required WMS layers
  * 🧾 Generation of flash flood maps (CSV + KML)
  * 🧠 Threshold-based classification (SRI7/SRI10)
  * 🧪 Generation of synthetic dummy forecasts for testing (CLI & Telegram)

* 🤖 Telegram bot:

  * Users simply send coordinates, the bot automatically executes all processing steps
  * 🆕 **LLM-supported input dialogue:** If coordinates are entered incorrectly, the LLM automatically provides short help texts and example inputs until a valid entry is detected
  * 🆕 **Dummy data via Telegram:** Users can explicitly request dummy forecasts (e.g., SRI7, SRI10) without using the CLI

* 💾 Caching: CSV cache of flooded streets (including depth)

* 🛟 Dummy forecast as fallback in case of API outages

* 🧵 Full logging of all processing steps for traceability

* ✅ Unit tests for core functions

---

## 🐞 Known Bugs

### BUG-001 – Invalid GPS points do not trigger an error message

Any GPS coordinates can currently be entered, even outside the coverage area.
For unsupported regions (currently only **Rhineland-Palatinate** is available), no error message is displayed.
This can lead to empty or misleading results.

---

### BUG-002 – Streets with variable flood depth are oversimplified

For street segments with varying flood depths, only the **first recorded value** is applied to the **entire street segment**.
Local variations are therefore lost and maps become inaccurate.

---

### BUG-003 – Forecast grid resolution does not match input data

The system currently creates a **2 × 2 km forecast grid** and evaluates precipitation thresholds within it.
However, the underlying meteorological data has a resolution of **10 × 10 km**.
This introduces pseudo-precision and inconsistent results.

---

### BUG-004 – Time series calculated only for the first GPS point

When multiple GPS points are selected, the full **time series** is correctly evaluated, but only for the **first GPS point**.
All additional points are ignored, leading to incomplete analyses.

---

## 🧱 Architecture Overview

HydroAlert follows clean software engineering principles for data science projects:

| Principle                    | Meaning                                                                |
| ---------------------------- | ---------------------------------------------------------------------- |
| Separation of Concerns       | Clear separation of data models, analysis, orchestration, I/O, and CLI |
| Functional Project Structure | Organized by responsibilities (e.g., `io/`, `analysis/`)               |
| Reproducibility              | Data paths configured via `.env`, no hardcoded logic                   |
| No Logic in `main.py`        | `main.py` only handles CLI parsing via `argparse`                      |
| Testability                  | Core functions are modular and testable with `pytest`                  |

---

## 🗂️ Project Structure and Layers

```bash
src/
config/       # Central configuration and defaults (paths, URLs, layer lists)
domain/       # Pure data models (e.g., BBox, LayerSpec) – no I/O or business logic
io/           # Low-level I/O: HTTP requests, filesystem access, DB adapters
services/     # Orchestration: combines io/ and analysis/ into usable services
analysis/     # Pure data processing/algorithms without side effects
use_cases/    # Entry points for CLI/API – translate inputs into service calls
utils/        # Generic helpers (logging, naming, time utilities)
main.py       # CLI parser and routing to use_cases/
```

### Allowed Layer Dependencies

* **use_cases** → may use `services`, `analysis`, `io`, `domain`, `config`, `utils`
* **services** → may use `io`, `analysis`, `domain`, `config`, `utils`
* **analysis** → may use `domain`, `utils` (**no direct access to `io`**)
* **io** → may use `domain`, `config`, `utils` (**no access to `analysis` or `services`**)
* **domain** → standard library only
* **config**, **utils** → usable by all, contain no business logic

---

## 🧪 Testing Strategy and Structure

The test structure mirrors the architecture and clearly separates test types.

### Core Principle: Mirror the Project Structure

```bash
src/
├── analysis/
│   └── flood_overlay.py
├── services/
│   └── cache_generation_service.py
...

tests/
├── analysis/
│   └── test_flood_overlay.py
├── services/
│   └── test_cache_generation_service.py
...
```

### Separation by Test Type

```bash
tests/
├── unit/            # isolated functionality (no I/O, no network)
│   └── analysis/
│       └── test_flood_overlay.py
├── integration/     # interaction of multiple modules, possibly fake I/O
│   └── services/
│       └── test_cache_generation_service.py
└── e2e/             # full workflow with real data
    └── test_full_pipeline.py
```

* **Unit**: Individual function with controlled input (`utm_to_pixel`, `depth_from_color`)
* **Integration**: Modules + test data (e.g., PNG + streets in cache service)
* **E2E**: Full workflow (API, WMS, classification)

### Additional Test Folders

* `fixtures/`: Shared test helpers (`make_mini_tile`, `conftest.py`)
* `golden/`: Expected output files for golden file comparisons
* `data/`: Static test data (mini PNGs, GeoJSONs)

### Naming Conventions

* Files: `test_<module_name>.py`
* Functions: `test_<what_is_tested>()`
* Fixtures: descriptive names, e.g., `mini_tile_path`

### Pytest Marks for Selective Execution

```python
@pytest.mark.unit
def test_depth_from_color(): ...

@pytest.mark.integration
def test_overlay_synthetic(): ...

@pytest.mark.e2e
def test_full_workflow(): ...
```

Example:

```bash
pytest -m unit
pytest -m integration
pytest -m "unit or integration"
```

---

## ▶️ CLI Usage

> **Note:** All commands (except `telegram`) require explicit coordinates:

```bash
--lat <latitude> --lon <longitude>
# e.g.
--lat 49.35 --lon 8.10
```

### 🌍 Location-Based Commands

```bash
# 🌐 Download WMS maps (flash flood layers)
PYTHONPATH=. python3 main.py download-layers --lat 49.35 --lon 8.10

# 📡 Retrieve 24h precipitation data using real weather data
PYTHONPATH=. python3 main.py forecast --lat 49.35 --lon 8.10

# 🧠 Evaluate: Which heavy rainfall maps are relevant?
PYTHONPATH=. python3 main.py evaluate --lat 49.35 --lon 8.10

# 🧪 Generate dummy rainfall fields (e.g., SRI7)
PYTHONPATH=. python3 main.py generate-dummy SRI7 --lat 49.35 --lon 8.10

# 🗄 Generate CSV cache of flooded streets
PYTHONPATH=. python3 main.py generate-cache --lat 49.35 --lon 8.10 --radius 200 --sample-distance 5
```

### 🤖 Telegram Bot (Automated via Coordinates & Dummy Data)

```bash
# 📲 Start Telegram bot
PYTHONPATH=. python3 main.py telegram
```

The bot automatically detects coordinates in user messages
(e.g., `49.35, 8.10`) and executes all forecast and analysis steps.

🆕 **LLM Support:**
If the input does not contain valid coordinates, the bot uses a language model to provide short hints and example inputs (e.g., correct format `49.35, 8.10`).
Once valid input is detected, the normal analysis workflow starts.

🆕 **Dummy Data via Telegram:**
Users can explicitly request dummy analyses, for example:

```
dummy SRI7 49.35, 8.10
dummy SRI10 49.40, 8.12
```

The bot generates the requested **synthetic forecasts** and returns maps + CSV files.
Useful for testing without real API calls.

---

## 📄 Example Output (`rain_grid_24h.csv`)

```csv
lat,lon,2025-08-01T12:00,2025-08-01T13:00,...,2025-08-02T11:00
49.98,8.24,0.1,0.2,...,0.0
49.97,8.23,15.3,20.7,...,3.2
```

---

## 📌 Configuration (.env)

```env
TESTORTE_CSV=data/testorte.csv
LOG_FILE_PATH=output/run.log
TERMINAL_LOG_LEVEL=INFO
FILE_LOG_LEVEL=DEBUG
TELEGRAM_BOT_TOKEN=
```

---

## External Map Data (Flash Flood Hazard Maps)

* Visualization via WMS service of the Rhineland-Palatinate Water Management Authority (flash flood hazard maps).
* License: **Creative Commons Attribution 4.0 (CC BY 4.0)** – see mapping services of the Water Management Administration Rhineland-Palatinate.
* Attribution: Map material © Water Portal Rhineland-Palatinate, licensed under CC BY 4.0.

---

## 👨‍💻 Author

David Mühlfeld
