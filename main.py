import argparse
from logging import Logger

from src.utils.utils_logger import get_logger
from src.use_cases.download_layers import run_download_layers_use_case
from src.use_cases.forecast import run_forecast_use_case
from src.use_cases.evaluate import run_evaluate_use_case
from src.use_cases.dummy_generation import run_dummy_generation_use_case
from src.use_cases.telegram_bot import run_telegram_bot_use_case
from src.use_cases.generate_cache import run_generate_cache_use_case


logger: Logger = get_logger()


def main() -> None:
    """Run the HydroAlert command-line interface.

    Parses command-line arguments and dispatches subcommands to handle
    data downloads, forecasting, evaluation and other utilities.
    """
    parser = argparse.ArgumentParser(description="HydroAlert Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand 1: download-layers
    layers_parser = subparsers.add_parser("download-layers", help="Lade WMS Layer herunter")
    layers_parser.add_argument("--lat", type=float, help="Geografische Breite (z. B. 49.45)")
    layers_parser.add_argument("--lon", type=float, help="Geografische Länge (z. B. 8.18)")

    # Subcommand 2: forecast
    forecast_parser = subparsers.add_parser("forecast", help="24h Regenvorhersage")
    forecast_parser.add_argument("--lat", type=float, help="Geografische Breite (z. B. 49.45)")
    forecast_parser.add_argument("--lon", type=float, help="Geografische Länge (z. B. 8.18)")

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
        run_download_layers_use_case(args)

    elif args.command == "forecast":
        run_forecast_use_case(args)

    elif args.command == "evaluate":
        run_evaluate_use_case(args)

    elif args.command == "generate-dummy":
        run_dummy_generation_use_case(args)

    elif args.command == "telegram":
        run_telegram_bot_use_case(args)

    elif args.command == "generate-cache":
        run_generate_cache_use_case(args)

if __name__ == "__main__":
    main()
