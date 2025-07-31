import argparse
from src.io.download_layers import download_all_wms_layers
from src.analysis.forecast_area import save_full_rain_forecast_grid
from src.utils.utils_logger import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="HydroAlert Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand 1: download-layers
    subparsers.add_parser("download-layers", help="Lade alle WMS-Layer für das PoC herunter")

    # Subcommand 2: forecast
    subparsers.add_parser("forecast", help="Starte die 24h-Flächenvorhersage mit echten Wetterdaten")

    args = parser.parse_args()
    logger.debug(f"📊 CLI Argumente: {args}")

    if args.command == "forecast":
        logger.info("🌍 Starte 24h-Niederschlags-Rasteranalyse …")
        save_full_rain_forecast_grid()
        logger.info("✅ Rastervorhersage abgeschlossen")

    elif args.command == "download-layers":
        logger.info("🌐 Lade WMS-Layer herunter …")
        download_all_wms_layers()
        logger.info("✅ WMS-Layer wurden erfolgreich heruntergeladen.")


if __name__ == "__main__":
    main()
