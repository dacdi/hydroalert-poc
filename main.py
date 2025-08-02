import argparse

from src.io.download_layers import download_all_wms_layers
from src.analysis.forecast_area import save_full_rain_forecast_grid
from src.utils.utils_logger import get_logger
from src.io.load_locations import get_default_location
from src.analysis.classify_rain_intensity import classify_rain_stage
from src.io.generate_dummy_data import generate_dummy_rain_data

logger = get_logger()


def main():
    parser = argparse.ArgumentParser(description="HydroAlert Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand 1: download-layers
    subparsers.add_parser("download-layers", help="Lade alle WMS-Layer für das PoC herunter")

    # Subcommand 2: forecast
    subparsers.add_parser("forecast", help="Starte die 24h-Flächenvorhersage mit echten Wetterdaten")

    # Subcommand 3: evaluate
    subparsers.add_parser("evaluate", help="Analysiere die bereitgestellten Regendaten auf Hinweise zu SKI Regenereigniss")

    # Subcommand 4: generate-dummy
    dummy_parser = subparsers.add_parser("generate-dummy", help="Generate dummy rain data for testing")
    dummy_parser.add_argument("variant", choices=["SRI7", "SRI10"], help="Choose dummy rain intensity")

    args = parser.parse_args()
    logger.debug(f"📊 CLI Argumente: {args}")


    if args.command == "download-layers":
        logger.info("🌐 Lade WMS-Layer herunter …")
        download_all_wms_layers()
        logger.info("✅ WMS-Layer wurden erfolgreich heruntergeladen.")

    elif args.command == "forecast":
        logger.info("🌍 Starte 24h-Niederschlags-Rasteranalyse …")
        lat, lon = get_default_location()
        logger.debug(f"Using location – Latitude: {lat}, Longitude: {lon}")
        save_full_rain_forecast_grid(center_lat=lat, center_lon=lon)
        logger.info("✅ Rastervorhersage abgeschlossen")

    elif args.command == "evaluate":
        logger.info("🌍 Starte mit Analyse vorhandener Regendaten")
        result = classify_rain_stage()
        logger.info(f"✅ Empfohlener Layer: {result}")

    elif args.command == "generate-dummy":
        logger.info("🧪 Generating dummy rain data …")
        logger.debug(f"Using variant for rain intesnity: {args.variant}")
        generate_dummy_rain_data(variant=args.variant)


if __name__ == "__main__":
    main()
