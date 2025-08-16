Hier ist das **aktualisierte vollständige README** mit deinen gewünschten Erweiterungen:

---

````markdown
# 🌧️ HydroAlert – Niederschlagsbasierte Wassertiefenvorhersage

**HydroAlert** ist ein modulares Python-Tool zur Flächenvorhersage von Überschwemmungsrisiken auf Basis von Niederschlagsdaten.  
Es kombiniert öffentlich verfügbare Wetter-APIs, Rasteranalysen und Schwellenwertlogik zur Auswahl geeigneter Sturzflutkarten (z. B. SRI7/SRI10).

---

## 🔧 Aktuelle Features (Stand: August 2025)

- 📍 Steuerung **aller Use Cases über Koordinaten** (`--lat`, `--lon`) – darunter:
  - 📡 Abruf stündlicher Niederschlagsprognosen (24h) aus Open-Meteo API
  - 🗺️ Flächenanalyse über Raster um gegebene Orte
  - 🌐 Download aller benötigten WMS-Layer
  - 🧾 Erstellung von Sturzflutkarten (CSV + KML)
  - 🧠 Klassifikation nach Schwellenwerten (SRI7/SRI10)
  - 🧪 Erzeugung synthetischer Dummy-Forecasts für Tests
- 🤖 Telegram-Bot: Nutzer können einfach Koordinaten senden – Bot führt obige Schritte automatisiert aus
- 💾 Caching: CSV-Cache überfluteter Straßen (inkl. Tiefe)
- 🛟 Dummy-Forecast als Fallback bei API-Ausfällen
- 🧵 Logging aller Schritte für Nachvollziehbarkeit
- ✅ Unit-Tests für Kernfunktionen

---

## 🧱 Architekturüberblick

HydroAlert folgt den Prinzipien sauberer Softwareentwicklung für Data-Science-Projekte:

| Prinzip                      | Bedeutung                                                                 |
|------------------------------|---------------------------------------------------------------------------|
| Separation of Concerns       | Datenmodelle, Analyse, Orchestrierung, I/O und CLI klar getrennt          |
| Funktionale Projektstruktur  | Gliederung nach Aufgaben, nicht nach Objekten (z. B. `io/`, `analysis/`)  |
| Reproduzierbarkeit           | Datenpfade über `.env` konfiguriert, keine Hardcoded-Logik                |
| Keine Logik in `main.py`     | `main.py` dient nur zur CLI-Steuerung via `argparse`                      |
| Testbarkeit                  | Zentrale Funktionen modular und über `pytest` testbar                     |

---

## 🗂️ Projektstruktur und Schichten

```bash
src/
config/       # Zentrale Konfiguration und Defaults (Pfade, URLs, Layer-Listen)
domain/       # Reine Datenmodelle (z. B. BBox, LayerSpec) – keine I/O oder Fachlogik
io/           # Low-Level I/O: HTTP-Requests, Dateisystemzugriffe, DB-Adapter
services/     # Orchestrierung: kombiniert io/ und analysis/ zu anwendungsfertigen Services
analysis/     # Reine Datenverarbeitung/Algorithmen ohne Seiteneffekte
use_cases/    # Einstiegspunkte für CLI/API – wandeln Eingaben in Service-Aufrufe um
utils/        # Generische Helfer (Logging, Naming, Zeit-Utilities)
main.py       # CLI-Parser und Routing zu use_cases/
````

### Erlaubte Abhängigkeiten zwischen Schichten

* **use\_cases** → darf `services`, `analysis`, `io`, `domain`, `config`, `utils` nutzen
* **services** → darf `io`, `analysis`, `domain`, `config`, `utils` nutzen
* **analysis** → darf `domain`, `utils` nutzen (**kein** direkter Zugriff auf `io`)
* **io** → darf `domain`, `config`, `utils` nutzen (**kein** Zugriff auf `analysis` oder `services`)
* **domain** → nutzt nur Standardbibliothek
* **config**, **utils** → von allen nutzbar, enthalten keine Projektlogik

---

## 🧪 Teststrategie und Struktur

Die Teststruktur spiegelt die Architektur und trennt klar nach Testarten:

### Grundprinzip: Spiegelung der Projektstruktur

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

### Trennung nach Testarten

```bash
tests/
├── unit/            # isolierte Funktionalität (keine I/O, kein Netzwerk)
│   └── analysis/
│       └── test_flood_overlay.py
├── integration/     # Zusammenspiel mehrerer Module, ggf. Fake-IO
│   └── services/
│       └── test_cache_generation_service.py
└── e2e/             # kompletter Ablauf mit echten Daten
    └── test_full_pipeline.py
```

* **Unit**: Einzelne Funktion mit kontrollierten Eingaben (`utm_to_pixel`, `depth_from_color`)
* **Integration**: Module + Testdaten (z. B. PNG+Straßen im Cache-Service)
* **E2E**: Kompletter Ablauf (API, WMS, Klassifikation)

### Weitere Testordner

* `fixtures/`: Gemeinsame Testhelfer (`make_mini_tile`, `conftest.py`)
* `golden/`: Erwartete Ausgabedateien für Golden-File-Vergleiche
* `data/`: Statische Testdaten (Mini-PNGs, GeoJSONs)

### Namenskonventionen

* Dateien: `test_<modulname>.py`
* Funktionen: `test_<was_getestet_wird>()`
* Fixtures: sprechend benennen, z. B. `mini_tile_path`

### Pytest-Marks für gezielte Ausführung

```python
@pytest.mark.unit
def test_depth_from_color(): ...

@pytest.mark.integration
def test_overlay_synthetic(): ...

@pytest.mark.e2e
def test_full_workflow(): ...
```

Beispiel:

```bash
pytest -m unit
pytest -m integration
pytest -m "unit or integration"
```

---

## ▶️ CLI-Nutzung

> **Hinweis:** Alle Befehle (außer `telegram`) erfordern explizite Koordinatenangabe:

```bash
--lat <Breitengrad> --lon <Längengrad>
# z. B.
--lat 49.35 --lon 8.10
```

### 🌍 Standortbasierte Befehle

```bash
# 🌐 WMS-Karten (Sturzflutlayer) herunterladen
PYTHONPATH=. python3 main.py download-layers --lat 49.35 --lon 8.10

# 📡 Regen für 24h-Fläche mit realen Wetterdaten abrufen
PYTHONPATH=. python3 main.py forecast --lat 49.35 --lon 8.10

# 🧠 Analyse: Welche Starkregenkarten sind relevant?
PYTHONPATH=. python3 main.py evaluate --lat 49.35 --lon 8.10

# 🧪 Dummy-Regenfelder erzeugen (z. B. SRI7)
PYTHONPATH=. python3 main.py generate-dummy SRI7 --lat 49.35 --lon 8.10

# 🗄 CSV-Cache der überfluteten Straßen erzeugen
PYTHONPATH=. python3 main.py generate-cache --lat 49.35 --lon 8.10 --radius 200 --sample-distance 5
```

### 🤖 Telegram-Bot (automatische Steuerung via Koordinaten)

```bash
# 📲 Telegram-Bot starten
PYTHONPATH=. python3 main.py telegram
```

Der Bot erkennt Koordinaten in Nutzeranfragen automatisch
(z. B. `49.35, 8.10`) und führt daraufhin alle Analyse- und Vorhersageprozesse aus.

---

## 📄 Beispielausgabe (`rain_grid_24h.csv`)

```csv
lat,lon,2025-08-01T12:00,2025-08-01T13:00,...,2025-08-02T11:00
49.98,8.24,0.1,0.2,...,0.0
49.97,8.23,15.3,20.7,...,3.2
```

---

## 📌 Konfiguration (.env)

```env
TESTORTE_CSV=data/testorte.csv
LOG_FILE_PATH=output/run.log
TERMINAL_LOG_LEVEL=INFO
FILE_LOG_LEVEL=DEBUG
TELEGRAM_BOT_TOKEN=
```

---

## 👨‍💻 Autor

dacdi

```

Wenn du möchtest, speichere ich dir das direkt als Datei oder pushe es in dein Projekt. Sag einfach Bescheid.
```
