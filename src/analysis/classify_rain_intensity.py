import csv
from typing import List

# Schwellenwerte in mm/h
SRI7_THRESHOLD = 15
SRI10_THRESHOLD = 25
MIN_AREA_FRACTION = 0.5  # 50 %

def classify_rain_stage(csv_path: str = "output/rain_grid_24h.csv",) -> str:
    """
    Analysiert ein CSV mit 24h-Regenraster und gibt den passenden Layernamen zurück.
    """
    rain_max_values: List[float] = []

    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header
        for row in reader:
            try:
                rain_values = [float(v) for v in row[2:] if v]
                max_rain = max(rain_values)
                rain_max_values.append(max_rain)
            except ValueError:
                continue  # falls leere oder ungültige Werte enthalten sind

    if not rain_max_values:
        return "Schummerung"  # fallback, wenn keine Daten

    total = len(rain_max_values)
    count_sri10 = sum(1 for r in rain_max_values if r >= SRI10_THRESHOLD)
    count_sri7 = sum(1 for r in rain_max_values if r >= SRI7_THRESHOLD)

    if count_sri10 / total >= MIN_AREA_FRACTION:
        return "Wassertiefe_SRI10_1h"
    elif count_sri7 / total >= MIN_AREA_FRACTION:
        return "Wassertiefe_SRI7_1h"
    else:
        return "Schummerung"  # kein ausreichender Regen

