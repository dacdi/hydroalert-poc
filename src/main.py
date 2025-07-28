import argparse
import logging
import random
import pandas as pd
from src.fetch_weather import get_rain_forecast
from src.load_riskmap import get_flood_depth
from src.fetch_wms.download_layers import download_all_wms_layers
from src.config import TESTORTE_CSV, OUTPUT_CSV
from src.utils_logger import get_logger
from src.forecast_area import get_rain_area
from src.forecast_area import save_rain_grid

logger = get_logger(__name__)


def run_forecast(testregen=None, testrandom=False):
    if testregen is None and not testrandom:
        logger.info("📡 Starte Vorhersage mit echten Wetterdaten für alle Testorte.")

    df = pd.read_csv(TESTORTE_CSV)
    results = []

    for _, row in df.iterrows():
        if testregen is not None:
            rain = testregen
            logger.info(f"🧪 Testregen: {rain} mm/h (fest vorgegeben)")
        elif testrandom:
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


def handle_forecast_command(testregen=None, testrandom=False, with_area=False):
    logger.info("📈 Starte Vorhersage-Modus")
    run_forecast(testregen=testregen, testrandom=testrandom)

    if with_area:
        logger.info("🌍 Berechne betroffene Regenfläche …")
        rain_threshold = testregen if testregen is not None else 5.0
        area_km2, hits, total, grid, rain_values = get_rain_area(min_rain_threshold=rain_threshold)

        logger.info(f"☔ Regenfläche ≥ {rain_threshold} mm/h: {area_km2:.1f} km² ({hits}/{total} Punkte)")

        save_rain_grid(
            grid,
            rain_values,
            threshold=rain_threshold,
            output_path="output/rain_grid.csv"
        )


def main():
    parser = argparse.ArgumentParser(description="HydroAlert Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: forecast
    forecast_parser = subparsers.add_parser("forecast", help="Starte die Regen-Vorhersage")
    forecast_parser.add_argument("--testregen", type=float, help="Simuliere festen Regenwert (in mm/h)")
    forecast_parser.add_argument("--testrandom", action="store_true", help="Simuliere zufälligen Regenwert")
    forecast_parser.add_argument("--with-area", action="store_true", help="Berechne zusätzlich die betroffene Regenfläche")

    # Subcommand: download-layers
    subparsers.add_parser("download-layers", help="Lade alle WMS-Layer für das PoC herunter")

    args = parser.parse_args()
    logger.debug(f"📊 CLI Argumente: {args}")

    if args.command == "forecast":
        handle_forecast_command(
            testregen=args.testregen,
            testrandom=args.testrandom,
            with_area=args.with_area
        )

    elif args.command == "download-layers":
        logger.info("🌐 Lade WMS-Layer herunter …")
        download_all_wms_layers()
        logger.info("✅ WMS-Layer wurden erfolgreich heruntergeladen.")


if __name__ == "__main__":
    main()
