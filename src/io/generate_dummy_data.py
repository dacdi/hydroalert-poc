import csv
import os
from typing import List
from src.utils.utils_logger import get_logger

logger = get_logger()

# Für 24 Stunden Regen
HOURS = 24

# Schwellenwerte – sollten mit evaluate_rain.py übereinstimmen
SRI7_VAL = 16.0             # >15 mm/h
SRI10_VAL = 26.0            # >25 mm/h
SRI10_4H_TOTAL = 42.0       # >40 mm in 4h ⇒ ~10.5 mm/h im Schnitt

def generate_dummy_rain_data(
    output_path: str = "output/rain_grid_24h.csv",
    variant: str = "SRI7"
) -> None:
    """
    Überschreibt eine bestehende CSV-Datei mit Dummy-Regenwerten.

    Args:
        output_path (str): Pfad zur Zieldatei (existierend!).
        variant (str): "SRI7", "SRI10", "SRI10_4h", "none", "flat"

    Returns:
        None
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
            values = [SRI7_VAL] * HOURS

        elif variant == "SRI10":
            values = [SRI10_VAL] * HOURS

        elif variant == "SRI10_4h":
            # 4 Stunden mit hohem Regen, Rest trocken
            values = [0.0] * HOURS
            start_index = 10  # z. B. Stunde 10–13
            for i in range(start_index, start_index + 4):
                values[i] = SRI10_4H_TOTAL / 4.0

        elif variant == "none":
            values = [0.0] * HOURS

        elif variant == "flat":
            values = [5.0] * HOURS  # unter allen Schwellen

        else:
            logger.warning(f"⚠️ Unbekannte Variante: {variant} – benutze 'none'")
            values = [0.0] * HOURS

        new_row = [lat, lon] + [str(v) for v in values]
        updated_rows.append(new_row)

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(updated_rows)

    logger.info(f"✅ Dummy-Daten erfolgreich geschrieben nach: {output_path}")
