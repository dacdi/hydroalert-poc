import argparse
import logging
import pandas as pd
from src.fetch_weather import get_rain_forecast
from src.load_riskmap import get_flood_depth
from src.config import TESTORTE_CSV, OUTPUT_CSV
from src.utils_logger import get_logger

logger = get_logger(__name__)

def run(testregen=None, testrandom=False):
    df = pd.read_csv(TESTORTE_CSV)
    results = []

    for _, row in df.iterrows():
        if testregen is not None:
            rain = testregen
            logger.info(f"🧪 Testregen: {rain} mm/h (fest vorgegeben)")
        elif testrandom:
            import random
            rain = round(random.uniform(0, 50), 1)
            logger.info(f"🎲 Zufälliger Testregen: {rain} mm/h")
        else:
            rain = get_rain_forecast(row["lat"], row["lon"])

        if rain is None:
            logger.warning(f"⚠️ Kein Regenwert für {row['ort']}")
            continue

        depth = get_flood_depth(rain)
        results.append({
            "Ort": row["ort"],
            "Regen [mm/h]": rain,
            "Wassertiefe [m]": depth
        })

    output = pd.DataFrame(results)
    output.to_csv(OUTPUT_CSV, index=False)
    logger.info(f"✅ Ergebnis gespeichert unter {OUTPUT_CSV}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Starte HydroAlert Vorhersage")
    parser.add_argument("--testregen", type=float, help="Simuliere festen Regenwert (in mm/h)")
    parser.add_argument("--testrandom", action="store_true", help="Simuliere zufälligen Regenwert")
    args = parser.parse_args()
    run(testregen=args.testregen, testrandom=args.testrandom)
