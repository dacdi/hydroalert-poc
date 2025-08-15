Hier ist dein überarbeitetes README, in dem dein bisheriger Inhalt **unverändert** bleibt, aber die Teststruktur-Empfehlung aus meinem Kommentar sauber eingearbeitet ist:

---

```markdown
# 🌧️ HydroAlert – Niederschlagsbasierte Wassertiefenvorhersage

**HydroAlert** ist ein modulares Python-Tool zur Flächenvorhersage von Überschwemmungsrisiken auf Basis von Niederschlagsdaten.  
Es kombiniert öffentlich verfügbare Wetter-APIs, Rasteranalysen und Schwellenwertlogik zur Auswahl geeigneter Sturzflutkarten (z. B. SRI7/SRI10).

---

## 🔧 Aktuelle Features (Stand: August 2025)

- 📡 Abruf stündlicher Niederschlagsprognosen (24h) aus Open-Meteo API
- 🗺️ Flächenanalyse auf Raster um gegebene Orte aus `testorte.csv`
- 📄 CSV-Ausgabe aller Rasterpunkte mit Regenwerten (`rain_grid_24h.csv`)
- 🧪 Generierung reproduzierbarer Dummy-Regenfelder für Testszenarien
- 🛟 Dummy-Forecast als Fallback bei API-Ausfällen
- 🧠 Automatische Auswahl geeigneter Sturzflutkarten (SRI7 / SRI10)
- 🌐 Download aller benötigten WMS-Layer
- 🧾 CSV-Cache überfluteter Straßen erzeugen
- 📲 Telegram-Bot zur Benachrichtigung
- 🧵 Logging aller Schritte für Nachvollziehbarkeit
- ✅ Unit-Tests für Kernfunktionen (z. B. Schwellenlogik)

---

## 🧱 Architekturüberblick

HydroAlert folgt den Prinzipien sauberer Softwareentwicklung für Data-Science-Projekte:

| Prinzip                      | Bedeutung                                                                 |
|------------------------------|---------------------------------------------------------------------------|
| Separation of Concerns       | Datenmodelle, Analyse, Orchestrierung, I/O und CLI klar getrennt          |
| Funktionale Projektstruktur  | Gliederung nach Aufgaben, nicht nach Objekten (z. B. `io/`, `analysis/`)  |
| Reproduzierbarkeit           | Datenpfade über `.env` konfiguriert, keine Hardcoded-Logik                |
| Keine Logik in `main.py`     | `main.py` dient nur zur CLI-Steuerung via `argparse`                      |
| Testbarkeit                  | Zentrale Funktionen modular und über `pytest` testbar                     |

---

## 🗂️ Projektstruktur und Schichten

```

src/
config/       # Zentrale Konfiguration und Defaults (Pfade, URLs, Layer-Listen)
domain/       # Reine Datenmodelle (z. B. BBox, LayerSpec) – keine I/O oder Fachlogik
io/           # Low-Level I/O: HTTP-Requests, Dateisystemzugriffe, DB-Adapter
services/     # Orchestrierung: kombiniert io/ und analysis/ zu anwendungsfertigen Services
analysis/     # Reine Datenverarbeitung/Algorithmen ohne Seiteneffekte
use\_cases/    # Einstiegspunkte für CLI/API – wandeln Eingaben in Service-Aufrufe um
utils/        # Generische Helfer (Logging, Naming, Zeit-Utilities)
main.py       # CLI-Parser und Routing zu use\_cases/

```

### Erlaubte Abhängigkeiten zwischen Schichten

- **use_cases** → darf `services`, `analysis`, `io`, `domain`, `config`, `utils` nutzen
- **services** → darf servicer, `io`, `analysis`, `domain`, `config`, `utils` nutzen
- **analysis** → darf `domain`, `utils` nutzen (**kein** direkter Zugriff auf `io`)
- **io** → darf `domain`, `config`, `utils` nutzen (**kein** Zugriff auf `analysis` oder `services`)
- **domain** → nutzt nur Standardbibliothek (keine Abhängigkeit zu anderen Schichten)
- **config**, **utils** → können von allen genutzt werden, enthalten keine Projektlogik

---

## 🧪 Teststrategie und Struktur

Um Chaos bei wachsenden Tests zu vermeiden, orientiert sich die Teststruktur an der `src/`-Architektur und trennt klar nach Testarten:

### Grundprinzip: Spiegelung der Projektstruktur
```

src/
├── analysis/
│   └── flood\_overlay.py
├── services/
│   └── cache\_generation\_service.py
...
tests/
├── analysis/
│   └── test\_flood\_overlay.py
├── services/
│   └── test\_cache\_generation\_service.py
...

```

**Vorteile:**
- Tests liegen dort, wo auch der zu testende Code ist.
- Einfache Navigation, da Ordnerstruktur parallel verläuft.
- Pytest findet automatisch alle Dateien, die mit `test_*.py` beginnen.

### Trennung nach Testarten
```

tests/
├── unit/            # isolierte Funktionalität (keine I/O, kein Netzwerk)
│   ├── analysis/
│   │   └── test\_flood\_overlay.py
│   └── utils/
│       └── test\_naming.py
├── integration/     # Zusammenspiel mehrerer Module, ggf. Fake-IO
│   └── services/
│       └── test\_cache\_generation\_service.py
└── e2e/             # kompletter Ablauf mit echten Daten
└── test\_full\_pipeline.py

````
- **Unit**: Einzelne Funktion oder Klasse mit kontrollierten Eingaben (`utm_to_pixel`, `depth_from_color`).
- **Integration**: Mehrere Module mit Testdaten (z. B. PNG+Straßen im Cache-Service).
- **E2E**: Voller Workflow mit echten APIs/WMS.

### Weitere Test-Ordner
- **fixtures/**: Gemeinsame Test-Helfer (`make_mini_tile`), `conftest.py`
- **golden/**: Erwartete Ausgabedateien (CSV, KML) für Golden-File-Vergleiche
- **data/**: Kleine statische Testdaten (Mini-PNGs, GeoJSONs)

### Namenskonventionen
- **Dateien:** `test_<modulname>.py`
- **Funktionen:** `test_<was_getestet_wird>()`
- **Fixtures:** aussagekräftige Namen wie `mini_tile_path`, `synthetic_streets_gdf`

### Pytest-Marks für gezieltes Ausführen
```python
import pytest

@pytest.mark.unit
def test_depth_from_color_valid_palette(): ...

@pytest.mark.integration
def test_overlay_with_synthetic_tile(): ...

@pytest.mark.e2e
def test_full_workflow_real_data(): ...
````

Ausführung:

```bash
pytest -m unit
pytest -m integration
pytest -m "unit or integration"
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

# 🧪 Dummy-Regenfelder erzeugen (z. B. SRI7)
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

Erstellt im Rahmen eines modularen Lernprojekts für Clean Code, Logging, CLI-Tools und reproduzierbare Data-Science-Pipelines mit Python.

```

---

Willst du, dass ich dir zusätzlich **eine Tabelle ins README setze**, die deine aktuellen Tests den Testarten und Ordnern zuordnet, damit auch neue Entwickler sofort sehen, wo welcher Test hingehört?
```
