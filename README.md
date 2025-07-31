Hier ist dein aktualisiertes `README.md`, **erweitert um die neuen Features zur Flächenanalyse und CSV-Ausgabe aller Rasterpunkte**:

---

````markdown
# 🌧️ HydroAlert – Niederschlagsbasierte Wassertiefenvorhersage

**HydroAlert** ist ein Python-Tool zur Vorhersage von Überschwemmungsrisiken anhand von Wetterdaten (Nowcasting) und einfachen Schwellenwerten für Starkregen. Es wurde mit dem Ziel entwickelt, sowohl reale Wetterdaten zu nutzen als auch reproduzierbare Tests mit künstlichem Regen zu ermöglichen.

---

## 🔧 Funktionen

- Holt stündliche Niederschlagsvorhersage von der Open-Meteo API
- Bestimmt Wassertiefe anhand einfacher Schwellenlogik
- Unterstützt festen oder zufälligen Testregen für reproduzierbare Tests
- Berechnet betroffene Regenfläche um Neustadt a. d. Weinstraße anhand eines Rasters
- CSV-Ausgabe:
  - 🔹 Wassertiefe-Vorhersage pro Ort (`prognose.csv`)
  - 🔹 Regenwerte für jeden Rasterpunkt der Fläche (`rain_grid.csv`)
- Logging auf DEBUG/INFO-Ebene

---

## 🚀 Schnellstart

### 📦 Voraussetzungen

- Python 3.8+
- Virtuelle Umgebung empfohlen

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
````

---

### ▶️ Nutzung

#### 📡 Echtdaten (Live-Wetter)

```bash
PYTHONPATH=. python3 src/main.py forecast
```

#### 🧪 Fester Testregen

```bash
PYTHONPATH=. python3 src/main.py forecast --testregen 35
```

#### 🎲 Zufälliger Testregen

```bash
PYTHONPATH=. python3 src/main.py forecast --testrandom
```

#### 🌍 Flächenanalyse um Neustadt (mit CSV-Ausgabe)

```bash
PYTHONPATH=. python3 src/main.py forecast --testregen 10 --with-area
```

Die Datei `data/output/rain_grid.csv` enthält:

| Breitengrad | Längengrad | Regen (mm/h) | Überschwellig | Zeitstempel                |
| ----------- | ---------- | ------------ | ------------- | -------------------------- |
| 49.35       | 8.15       | 12.3         | True          | 2025-07-28T15:34:01.123456 |
| ...         | ...        | ...          | ...           | ...                        |

#### 🗺️ WMS-Layer (Sturzflutkarten) herunterladen

```bash
PYTHONPATH=. python3 src/main.py download-layers
```

---

## 🗂️ Projektstruktur

```
HydroAlert/
├── data/
│   ├── testorte.csv         # Eingabedaten für Prognosen
│   └── output/
│       ├── prognose.csv     # Prognoseergebnisse pro Ort
│       └── rain_grid.csv    # Flächenanalyse-Rasterdaten
├── src/
│   ├── fetch_weather.py
│   ├── forecast_area.py     # Flächenanalyse
│   ├── geo_utils.py         # Rastergenerierung
│   ├── load_riskmap.py
│   ├── fetch_wms/
│   │   └── download_layers.py
│   ├── config.py
│   ├── main.py
│   └── utils_logger.py
├── tests/                   # pytest-Tests inkl. CLI-Test
├── requirements.txt
└── .env
```

---

## ⚙️ Beispielausgabe

### Prognose (pro Ort)

```csv
Ort,Regen [mm/h],Wassertiefe [m]
Stuttgart,35.0,0.5
Freiburg,12.1,0.1
```

### Flächenanalyse (Rasterpunkte um Neustadt)

```csv
Breitengrad,Längengrad,Regen (mm/h),Überschwellig,Zeitstempel
49.3517,8.1501,10.0,True,2025-07-28T18:13:45.124563
49.3497,8.1501,7.2,True,2025-07-28T18:13:45.124563
...
```

---

## 🧪 Testen

```bash
PYTHONPATH=. pytest
```

> ⚠️ CLI-Tests nutzen `subprocess` und testen vollständige Programmläufe.

---

## 📌 Konfiguration

Die Datei `.env` enthält:

```env
TESTORTE_CSV=data/testorte.csv
OUTPUT_CSV=data/output/prognose.csv
```

---

## 👨‍💻 Autor

Erstellt im Rahmen eines Lernprojekts zur sauberen Softwareentwicklung in Python (Clean Code, Logging, Testing, Strukturierung).

```

---

Wenn du möchtest, kann ich noch eine kurze Sektion zu "📈 Weiterentwicklungsideen" oder "🧠 Technisches Konzept" ergänzen. Sag einfach Bescheid!
```
