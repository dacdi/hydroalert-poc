# 🌧️ HydroAlert – Niederschlagsbasierte Wassertiefenvorhersage

**HydroAlert** ist ein modulares Python-Tool zur Flächenvorhersage von Überschwemmungsrisiken auf Basis von Niederschlagsdaten. Es kombiniert öffentlich verfügbare Wetter-APIs, Rasteranalysen und Schwellenwertlogik zur Auswahl geeigneter Starkregenkarten (z. B. SRI7/SRI10).

---

## 🔧 Aktuelle Features (Stand: August 2025)

- 📡 Abruf stündlicher Niederschlagsprognose für 24h aus Open‑Meteo API
- 🗺️ Flächenanalyse auf Raster um gegebene Orte aus `testorte.csv`
- 📄 CSV-Ausgabe aller Rasterpunkte mit Regenwerten (`rain_grid_24h.csv`)
- 🧪 Generierung reproduzierbarer Dummy-Regenfelder für Testszenarien
- 🛟 Dummy-Forecast als Fallback bei API-Ausfällen
- 🧠 Automatische Auswahl geeigneter Sturzflutkarten (SRI7 / SRI10)
- 🌐 Download aller benötigten WMS-Layer
- 🧾 CSV-Cache überfluteter Straßen erzeugen
- 📲 Telegram-Bot zur Benachrichtigung
- 🧵 Logging aller Schritte für Nachvollziehbarkeit
- ✅ Unit-Tests für Kernfunktionen (z. B. Schwellenlogik)

---

## 🧱 Architekturüberblick

HydroAlert folgt den Prinzipien sauberer Softwareentwicklung für Data-Science-Projekte:

| Prinzip                      | Bedeutung                                                                 |
|-----------------------------|---------------------------------------------------------------------------|
| Separation of Concerns      | Datenzugriff, Analyse, Auswertung und Logging sind klar getrennt         |
| Funktionale Projektstruktur | Gliederung nach Aufgaben, nicht nach Objekten (z. B. `io/`, `analysis/`) |
| Reproduzierbarkeit          | Datenpfade über `.env` konfiguriert, keine Hardcoded-Logik               |
| Keine Logik in `main.py`    | `main.py` dient nur zur CLI-Steuerung via `argparse`                     |
| Testbarkeit                 | Zentrale Funktionen sind modular und über `pytest` testbar               |

---

## 🗂️ Projektstruktur

```

hydroalert-poc/
├── data/                      # Eingabedaten und WMS-Layer
│   ├── WMS_Layer__bersicht.csv
│   ├── testorte.csv
│   └── wms_layers/
│
├── output/                    # Modell- und Log-Ausgaben
│   ├── rain_grid_24h.csv
│   └── run.log
│
├── src/
│   ├── analysis/              # Analyse- und Klassifizierungslogik
│   │   ├── classify_rain_intensity.py
│   │   ├── flood_overlay.py
│   │   └── forecast_area.py
│   ├── io/                    # Datei- und API-Zugriff
│   │   ├── download_layers.py
│   │   ├── fetch_weather.py
│   │   ├── flood_cache.py
│   │   ├── generate_dummy_data.py
│   │   ├── load_locations.py
│   │   └── telegram_bot.py
│   ├── utils/                 # Logging, Grid-Hilfsfunktionen
│   │   ├── geo_utils.py
│   │   └── utils_logger.py
│   └── config/
│       └── config.py
│
├── tests/                     # Unit-Tests
│   ├── analysis/
│   └── utils/
│
├── main.py                    # Einstiegspunkt mit `argparse`
├── requirements.txt
└── README.md
```

---

## ▶️ CLI-Nutzung

```bash
# 🌐 WMS-Karten (Sturzflutlayer) herunterladen
PYTHONPATH=. python3 main.py download-layers

# 📡 Regen für 24h-Fläche mit realen Wetterdaten abrufen
PYTHONPATH=. python3 main.py forecast

# 🧠 Analyse: Welche Starkregenkarten sind relevant?
PYTHONPATH=. python3 main.py evaluate

# 🧪 Dummy-Regenfelder erzeugen (z. B. SRI7)
PYTHONPATH=. python3 main.py generate-dummy SRI7

# 🗄 CSV-Cache der überfluteten Straßen erzeugen
PYTHONPATH=. python3 main.py generate-cache --radius 200 --sample-distance 5

# 📲 Telegram-Bot starten
PYTHONPATH=. python3 main.py telegram
```

---

## 📄 Beispielausgabe (`rain_grid_24h.csv`)

```csv
lat,lon,2025-08-01T12:00,2025-08-01T13:00,...,2025-08-02T11:00
49.9821,8.2403,0.1,0.2,...,0.0
49.9819,8.2401,15.3,20.7,...,3.2
...
```

---

## 🧪 Testen

```bash
pytest
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

Erstellt im Rahmen eines modularen Lernprojekts für Clean Code, Logging, CLI-Tools und reproduzierbare Data-Science-Pipelines mit Python.
