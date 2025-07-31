import argparse
from src.io.download_layers import download_all_wms_layers
from src.core.forecast_area import save_full_rain_forecast_grid
from src.utils.utils_logger import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="HydroAlert Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: forecast (nur noch für Flächenprognose)
    forecast_parser = subparsers.add_parser("forecast", help="Starte die 24h-Flächenvorhersage")
    forecast_parser.add_argument("--area-24h", action="store_true",
                                 help="Erstelle Rasterausgabe für die nächsten 24h Regen um Neustadt")

    # Subcommand: Karten herunterladen
    subparsers.add_parser("download-layers", help="Lade alle WMS-Layer für das PoC herunter")

    args = parser.parse_args()
    logger.debug(f"📊 CLI Argumente: {args}")

    if args.command == "forecast":
        if args.area_24h:
            logger.info("🌍 Starte 24h-Niederschlags-Rasteranalyse …")
            save_full_rain_forecast_grid()
            logger.info(f"✅ Rastervorhersage gespeichert.")
        else:
            logger.warning("⚠️ Kein gültiges Sub-Flag wie --area-24h angegeben. Nichts ausgeführt.")

    elif args.command == "download-layers":
        logger.info("🌐 Lade WMS-Layer herunter …")
        download_all_wms_layers()
        logger.info("✅ WMS-Layer wurden erfolgreich heruntergeladen.")


if __name__ == "__main__":
    main()
