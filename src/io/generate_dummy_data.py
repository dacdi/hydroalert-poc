#!/usr/bin/env python3
"""
generate_dummy_rain_data.py

Erzeugt Dummy-Regenwerte für 24h, um alle Rain-Stage-Varianten (SRI7, SRI10, SRI10_4h, none, flat) zu testen.

HydroPrompt-Richtlinien:
- Klare Parameter und Schwellenwerte
- Einheitliche Log-Ausgaben
- Variablen so gesetzt, dass jeder Variant korrekt ausgelöst wird
"""
import csv
import os
from typing import List
from src.utils.utils_logger import get_logger

logger = get_logger()

# Für 24 Stunden Regen
HOURS = 24

# Dummy-Werte, die oberhalb der jeweiligen Schwellen liegen:
# SRI7: Schwelle >15 mm/h ⇒ dummy 16 mm/h
# SRI10: Schwelle >25 mm/h ⇒ dummy 26 mm/h
# SRI10_4h: Schwelle >40 mm in 4h ⇒ dummy 44 mm in 4h ⇒ 11 mm/h im Schnitt
SRI7_VAL = 16.0             # >15 mm/h, löst SRI7 aus
SRI10_VAL = 26.0            # >25 mm/h, löst SRI10 aus
SRI10_4H_TOTAL = 44.0       # >40 mm in 4h, löst SRI10_4h aus


def generate_dummy_rain_data(
    output_path: str = "output/rain_grid_24h.csv",
    variant: str = "SRI7"
) -> None:
    """
    Überschreibt eine bestehende CSV-Datei mit Dummy-Regenwerten.

    Args:
        output_path (str): Pfad zur Zieldatei (existierend!).
        variant (str): "SRI7", "SRI10", "SRI10_4h", "none", "flat"
    """
    if not os.path.exists(output_path):
        logger.error(f"❌ Datei nicht gefunden: {output_path}")
        return

    logger.info(f"🧪 Erzeuge Dummy-Regenwerte: Variante = {variant}")

    with open(output_path, "r", newline="") as f:
        reader = list(csv.reader(f))
        header, rows = reader[0], reader[1:]

    updated_rows: List[List[str]] = []

    for row in rows:
        lat, lon = row[:2]

        if variant == "SRI7":
            # Alternierende Stunden oberhalb SRI7-Schwelle, um 4h-Fenster unter Schwelle für SRI10_4h zu halten
            values = [SRI7_VAL if i % 2 == 0 else 0.0 for i in range(HOURS)]

        elif variant == "SRI10":
            # Einzelne Stunde oberhalb SRI10-Schwelle, Rest trocken, um 4h-Schwelle nicht zu überschreiten
            values = [0.0] * HOURS
            values[0] = SRI10_VAL  # z.B. nur Stunde 0 mit starkem Regen

        elif variant == "SRI10_4h":
            # 4 Stunden hoher Regen, Rest trocken
            values = [0.0] * HOURS
            # z.B. Stunden 8–11
            start_index = 8
            for i in range(start_index, start_index + 4):
                values[i] = SRI10_4H_TOTAL / 4.0  # 11 mm/h für 4h

        elif variant == "none":
            # kein Regen
            values = [0.0] * HOURS

        elif variant == "flat":
            # konstante Niederschläge unter allen Schwellen
            values = [5.0] * HOURS

        else:
            logger.warning(f"⚠️ Unbekannte Variante: {variant} – benutze 'none'")
            values = [0.0] * HOURS

        new_row = [lat, lon] + [f"{v:.1f}" for v in values]
        updated_rows.append(new_row)

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(updated_rows)

    logger.info(f"✅ Dummy-Daten erfolgreich geschrieben nach: {output_path}")


if __name__ == "__main__":
    # Beispiel: python generate_dummy_rain_data.py output/rain_grid_24h.csv SRI10_4h
    import sys
    if len(sys.argv) >= 3:
        _, path, var = sys.argv
        generate_dummy_rain_data(output_path=path, variant=var)
    else:
        logger.error("Usage: generate_dummy_rain_data.py <csv_path> <variant>")
