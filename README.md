# 🌧️ HydroAlert – Niederschlagsbasierte Wassertiefenvorhersage

**HydroAlert** ist ein modulares Python-Tool zur Flächenvorhersage von Überschwemmungsrisiken auf Basis von Niederschlagsdaten. Es kombiniert öffentlich verfügbare Wetter-APIs, Rasteranalysen und Schwellenwertlogik zur Auswahl geeigneter Starkregenkarten (z. B. SRI7/SRI10).

---

## 🔧 Aktuelle Features (Stand: August 2025)

- 📡 Abruf stündlicher Niederschlagsprognose für 24h aus Open-Meteo API
- 🗺️ Flächenanalyse auf Raster um gegebene Orte aus `testorte.csv`
- 📄 CSV-Ausgabe aller Rasterpunkte mit Regenwerten (`rain_grid_24h.csv`)
- 🧪 Generierung reproduzierbarer Dummy-Regenfelder für Testszenarien
- 🛟 Dummy-Forecast als Fallback bei API-Ausfällen
- 🧠 Automatische Auswahl geeigneter Sturzflutkarten (SRI7 / SRI10)
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
HydroAlert/
├── data/                      # Eingabedaten
│   ├── testorte.csv           # Orte mit Koordinaten
│   └── wms_layers/            # heruntergeladene WMS-Layer
├── output/                    # Ausgabedateien
│   └── rain_grid_24h.csv      # Ergebnis der Rasterprognose
│
├── src/
│   ├── analysis/              # Analyse- und Klassifizierungslogik
│   │   ├── forecast_area.py
│   │   └── classify_rain_intensity.py
│   ├── io/                    # Datei- und API-Zugriff
│   │   ├── fetch_weather.py
│   │   ├── generate_dummy_data.py
│   │   └── flood_cache.py
│   ├── utils/                 # Logging, Grid-Hilfsfunktionen
│   └── config/                # `.env`-Konfiguration
│
├── tests/                     # Unit-Tests
├── main.py                   # Einstiegspunkt mit `argparse`
├── .env                      # Pfad-Konfiguration
└── requirements.txt
```

---

## ▶️ CLI-Nutzung

```bash
# 📡 Regen für 24h-Fläche mit realen Wetterdaten abrufen
PYTHONPATH=. python3 src/main.py forecast

# 🧪 Dummy-Regenfelder für SRI7 erzeugen (zum Testen)
PYTHONPATH=. python3 src/main.py generate-dummy SRI7

# 🧠 Analyse: Welche Starkregenkarten sind relevant?
PYTHONPATH=. python3 src/main.py evaluate

# 🌐 WMS-Karten (Sturzflutlayer) herunterladen
PYTHONPATH=. python3 src/main.py download-layers
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
RAIN_GRID_PATH=output/rain_grid_24h.csv
WMS_LAYERS_DIR=data/wms_layers
CACHE_DIR=data/cache
```

---

## 👨‍💻 Autor

Erstellt im Rahmen eines modularen Lernprojekts für Clean Code, Logging, CLI-Tools und reproduzierbare Data-Science-Pipelines mit Python.