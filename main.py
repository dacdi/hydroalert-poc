import argparse
from logging import Logger

from src.io.download_layers import download_all_wms_layers
from src.utils.utils_logger import get_logger
from src.io.load_locations import get_default_location
from src.analysis.classify_rain_intensity import classify_rain_stage
from src.io.generate_dummy_data import generate_dummy_rain_data
from src.analysis.forecast_area import RainGridForecaster
from src.io.telegram_bot import run_bot
from src.io.flood_cache import generate_csv_cache


logger: Logger = get_logger()


def main() -> None:
    """Run the HydroAlert command-line interface.

    Parses command-line arguments and dispatches subcommands to handle
    data downloads, forecasting, evaluation and other utilities.
    """
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
    dummy_parser.add_argument("variant", choices=["SRI7", "SRI10", "SRI10_4h", "none", "flat"], help="Choose dummy rain intensity")

    # Subcommand 5: Telegram Bot
    subparsers.add_parser("telegram", help="Starte den Telegram-Bot")

    # Sucommand 6: CSV Cache mit den Überflutteten Straßen
    parser_cache = subparsers.add_parser(
        "generate-cache",
        help="Erzeuge CSV-Cache der überfluteten Straßen für alle Layer"
    )
    parser_cache.add_argument(
        "--radius",
        type=float,
        default=200.0,
        help="Radius in Metern um den Standardort (default: 200)"
    )
    parser_cache.add_argument(
        "--sample-distance",
        type=float,
        default=5.0,
        help="Abstand in Metern zwischen Stichprobenpunkten (default: 5)"
    )

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
        forecaster = RainGridForecaster(
            center_lat=lat,
            center_lon=lon
        )
        forecaster.save_full_rain_forecast_grid()
        logger.info("24h-Raster erfolgreich geladen")

    elif args.command == "evaluate":
        logger.info("🌍 Starte mit Analyse vorhandener Regendaten")
        result = classify_rain_stage()
        logger.info(f"✅ Empfohlener Layer: {result}")

    elif args.command == "generate-dummy":
        logger.info("🧪 Generating dummy rain data …")
        logger.debug(f"Using variant for rain intesnity: {args.variant}")
        generate_dummy_rain_data(variant=args.variant)

    elif args.command == "telegram":
        logger.info("📲 Starte Telegram-Bot …")
        run_bot()

    elif args.command == "generate-cache":
        logger.info("🗄 Generiere Flood-CSV-Cache …")
        generate_csv_cache(
            radius_m=args.radius,
            sample_distance_m=args.sample_distance
        )
        logger.info("✅ Cache-Erzeugung abgeschlossen.")

if __name__ == "__main__":
    main()
