# src/use_cases/forecast.py
from __future__ import annotations
from argparse import Namespace
from logging import Logger
from typing import Optional

from src.utils.utils_logger import get_logger
from src.services.forecast_area_service import RainGridForecaster
from src.config.config import GRID_SIZE_M, FORECAST_STEP_M

logger: Logger = get_logger()


def run_forecast_use_case(args: Namespace) -> None:
    """
    Use Case: 24h-Niederschlagsraster erzeugen und als CSV speichern.

    Erwartet:
        args.lat (float) - Breitengrad
        args.lon (float) - Längengrad

    Optional:
        args.grid_size_m (float) - Größe des Rasters in Metern (Default: config.GRID_SIZE_M)
        args.step_m (float) - Abstand zwischen Rasterpunkten in Metern (Default: config.FORECAST_STEP_M)
    """
    lat: float = args.lat
    lon: float = args.lon
    grid_size_m: float = getattr(args, "grid_size_m", GRID_SIZE_M)
    step_m: float = getattr(args, "step_m", FORECAST_STEP_M)

    logger.info("▶️ Forecast-Use-Case gestartet")
    logger.debug(
        "📍 Eingabeparameter: lat=%.6f, lon=%.6f, grid_size_m=%.1f, step_m=%.1f",
        lat, lon, grid_size_m, step_m
    )

    try:
        outpath: Optional[str] = RainGridForecaster().save_full_rain_forecast_grid(
            lat=lat,
            lon=lon,
            grid_size_m=grid_size_m,
            step_m=step_m,
        )

        if not outpath:
            logger.error("❌ Keine CSV-Datei erzeugt – Service gab None zurück.")
            raise RuntimeError("Forecast-Service hat keinen Ausgabepfad geliefert.")

        logger.info("✅ Forecast-Use-Case abgeschlossen – CSV gespeichert unter: %s", outpath)

    except Exception:
        logger.exception("❌ Forecast-Use-Case fehlgeschlagen")
        raise
