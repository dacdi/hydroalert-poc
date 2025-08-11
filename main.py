import argparse
from logging import Logger

from src.utils.utils_logger import get_logger
from src.use_cases.download_layers import run_download_layers_use_case
from src.use_cases.forecast import run_forecast_use_case
from src.use_cases.evaluate import run_evaluate_use_case
from src.use_cases.generate_dummy import run_generate_dummy_use_case
from src.use_cases.telegram_bot import run_telegram_bot_use_case
from src.use_cases.generate_cache import run_generate_cache_use_case
from src.config.config import DEFAULT_LAYERS  # {full_name: short_name}

logger: Logger = get_logger()


def main() -> None:
    """HydroAlert CLI."""
    parser = argparse.ArgumentParser(description="HydroAlert Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # download-layers (lat/lon optional – je nach deiner Pipeline)
    layers_parser = subparsers.add_parser("download-layers", help="WMS-Layer herunterladen")
    layers_parser.add_argument("--lat", type=float, help="Geografische Breite (z. B. 49.45)")
    layers_parser.add_argument("--lon", type=float, help="Geografische Länge (z. B. 8.18)")

    # forecast (lat/lon optional – falls du Default-Handling hast; sonst required=True setzen)
    forecast_parser = subparsers.add_parser("forecast", help="24h Regenvorhersage")
    forecast_parser.add_argument("--lat", type=float, help="Geografische Breite (z. B. 49.45)")
    forecast_parser.add_argument("--lon", type=float, help="Geografische Länge (z. B. 8.18)")

    # evaluate (lat/lon jetzt verpflichtend)
    evaluate_parser = subparsers.add_parser(
        "evaluate",
        help="Analysiere bereitgestellte Regendaten auf SRI-Ereignisse"
    )
    evaluate_parser.add_argument("--lat", type=float, required=True, help="Geografische Breite")
    evaluate_parser.add_argument("--lon", type=float, required=True, help="Geografische Länge")
    # optional: explizite CSV-Datei übergeben
    evaluate_parser.add_argument("--csv", type=str, help="Pfad zur Regen-CSV (optional)")

    # generate-dummy (lat/lon verpflichtend)
    dummy_parser = subparsers.add_parser(
        "generate-dummy",
        help="Erzeuge Dummy-Regen-CSV für einen Ort"
    )
    dummy_parser.add_argument("--lat", type=float, required=True, help="Geografische Breite")
    dummy_parser.add_argument("--lon", type=float, required=True, help="Geografische Länge")
    dummy_parser.add_argument(
        "variant",
        choices=["SRI7", "SRI10", "SRI10_4h", "none"],
        help="Dummy-Variante"
    )
    dummy_parser.add_argument("--hours", type=int, default=24, help="Anzahl Stunden (Standard: 24)")

    # telegram
    subparsers.add_parser("telegram", help="Starte den Telegram-Bot")

    # generate-cache (lat/lon verpflichtend; neue Flag-Namen passend zum Service)
    cache_parser = subparsers.add_parser(
        "generate-cache",
        help="Erzeuge CSV+KML-Cache der überfluteten Straßen je SRI-Layer"
    )
    cache_parser.add_argument("--lat", type=float, required=True, help="Geografische Breite")
    cache_parser.add_argument("--lon", type=float, required=True, help="Geografische Länge")
    cache_parser.add_argument("--radius-m", dest="radius_m", type=float, default=1000.0,
                              help="Radius um (lat,lon) in m (Standard: 300)")
    cache_parser.add_argument("--sample-m", dest="sample_m", type=float, default=2.0,
                              help="Abstand zwischen Stichprobenpunkten in m (Standard: 5)")
    # Optional: nur bestimmte Layer rechnen (Shortnames aus DEFAULT_LAYERS)
    cache_parser.add_argument(
        "--layers",
        nargs="+",
        choices=list(DEFAULT_LAYERS.values()),
        help="Subset der SRI-Layer (Shortnames), z. B. Wassertiefe_SRI10_1h"
    )

    args = parser.parse_args()
    logger.info("▶️ Starte HydroAlert – Command: %s", args.command)
    logger.debug("📊 CLI Argumente: %s", vars(args))

    if args.command == "download-layers":
        run_download_layers_use_case(args)
    elif args.command == "forecast":
        run_forecast_use_case(args)
    elif args.command == "evaluate":
        run_evaluate_use_case(args)
    elif args.command == "generate-dummy":
        run_generate_dummy_use_case(args)
    elif args.command == "telegram":
        run_telegram_bot_use_case(args)
    elif args.command == "generate-cache":
        run_generate_cache_use_case(args)


if __name__ == "__main__":
    main()
