# 🌧️ HydroAlert – Niederschlagsbasierte Wassertiefenvorhersage

**HydroAlert** ist ein Python-Tool zur Vorhersage von Überschwemmungsrisiken anhand von Wetterdaten (Nowcasting) und einfachen Schwellenwerten für Starkregen. Es wurde mit dem Ziel entwickelt, sowohl reale Wetterdaten zu nutzen als auch reproduzierbare Tests mit künstlichem Regen zu ermöglichen.

---

## 🔧 Funktionen

- Holt stündliche Niederschlagsvorhersage von der Open-Meteo API
- Bestimmt Wassertiefe anhand einfacher Schwellenlogik
- Unterstützt festen oder zufälligen Testregen für reproduzierbare Tests
- Logging auf DEBUG/INFO-Ebene
- CSV-Ausgabe der Ergebnisse für mehrere Orte

---

## 🚀 Schnellstart

### 📦 Voraussetzungen

- Python 3.8+
- Virtuelle Umgebung empfohlen

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### ▶️ Nutzung

#### 📡 Echtdaten (Live-Wetter)

```bash
python main.py
```

#### 🧪 Fester Testregen

```bash
python main.py --testregen 35
```

#### 🎲 Zufälliger Testregen

```bash
python main.py --testrandom
```

---

## 🗂️ Projektstruktur

```
HydroAlert/
├── data/               # Testorte (CSV)
├── output/             # Ergebnisdateien
├── src/                # Hauptmodule
│   ├── fetch_weather.py
│   ├── load_riskmap.py
│   ├── config.py
│   └── utils_logger.py
├── tests/              # pytest-Tests
├── main.py             # Einstiegspunkt
├── requirements.txt
└── .env                # Konfiguration der Pfade
```

---

## ⚙️ Beispielausgabe

Die CSV-Ausgabe `output/prognose.csv` enthält:

| Ort        | Regen [mm/h] | Wassertiefe [m] |
|------------|---------------|-----------------|
| Stuttgart  | 35.0          | 0.5             |
| Freiburg   | 35.0          | 0.5             |

---

## 🧪 Testen

```bash
PYTHONPATH=. pytest
```

---

## 📌 Konfiguration

Die Datei `.env` enthält:

```env
TESTORTE_CSV=data/testorte.csv
OUTPUT_CSV=output/prognose.csv
```

---

## 👨‍💻 Autor

Erstellt im Rahmen eines Lernprojekts zur sauberen Softwareentwicklung in Python (Clean Code, Logging, Testing, Strukturierung).

