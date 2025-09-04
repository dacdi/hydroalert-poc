# src/services/forecast_area_service.py
from __future__ import annotations
from typing import List, Tuple, Iterable
from datetime import datetime, timezone
import os

from src.utils.utils_logger import get_logger
from src.analysis.grid_ops import generate_hour_labels, generate_grid
from src.io.forecast_client import fetch_forecast_24h
from src.io.file_io import ensure_dir
from src.domain.grid_point import GridPoint
from src.domain.rain_forecast import RainForecast
from src.io.csv_writer import write_rain_forecasts_csv
from src.utils.naming import cache_path_for_latlon, rain_grid_csv_name

logger = get_logger()


class RainGridForecaster:
    """Service: erstellt ein Raster, holt 24h-Niederschlagsprognosen und speichert sie als CSV."""

    def _build_hour_labels(self) -> List[str]:
        now_utc = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        return generate_hour_labels(now_utc, hours=24)

    def _forecast_points(
            self, lat: float, lon: float, grid_size_m: float, step_m: float
    ) -> List[Tuple[float, float]]:
        half_extent_m = float(grid_size_m) / 2.0  # ✅ halbe Kantenlänge in METERN

        grid = generate_grid(
            center_lat=lat,
            center_lon=lon,
            half_extent_m=half_extent_m,  # ✅ jetzt korrekt benannt & dimensioniert
            step_m=step_m,  # ✅ Meter bleiben Meter
        )

        logger.debug(
            "🧩 Raster mit %d Punkten erzeugt (grid_size=%.1fm, half_extent=%.1fm, step=%.1fm).",
            len(grid), grid_size_m, half_extent_m, step_m
        )
        for lat_p, lon_p in grid[:50]:
            logger.debug("  %.6f, %.6f", lat_p, lon_p)
        if len(grid) > 50:
            logger.debug("… (%d weitere Punkte unterdrückt)", len(grid) - 50)
        return grid

    def _fetch_forecasts(
        self, points: Iterable[Tuple[float, float]]
    ) -> List[RainForecast]:
        """Holt Forecasts und wandelt dict-Rückgaben in RainForecast um."""
        out: List[RainForecast] = []
        for i, (plat, plon) in enumerate(points, start=1):
            try:
                fc = fetch_forecast_24h(plat, plon)

                # 🔍 Falls der Client ein dict zurückgibt (aktueller Stand)
                if isinstance(fc, dict) and "hourly" in fc:
                    precip = fc["hourly"].get("precipitation", [])
                    if precip and all(isinstance(v, (int, float)) for v in precip):
                        out.append(RainForecast(point=GridPoint(plat, plon), hourly_values=precip))
                    else:
                        logger.error(f"❌ Ungültige precipitation-Daten für {plat}, {plon}: {precip}")
                    continue

                # 🔍 Falls der Client schon RainForecast zurückgibt
                if isinstance(fc, RainForecast):
                    if all(isinstance(v, (int, float)) for v in fc.hourly_values):
                        out.append(fc)
                    else:
                        logger.error(f"❌ Ungültige hourly_values in {fc.point}: {fc.hourly_values}")
                else:
                    logger.error(f"❌ Unerwarteter Typ von fetch_forecast_24h: {type(fc)}")

            except Exception as exc:
                logger.exception("Fehler beim Forecast (%f, %f): %s", plat, plon, exc)

            if i % 10 == 0:
                logger.info("Progress: %d Punkte verarbeitet …", i)

        logger.info("📦 %d Forecasts geholt.", len(out))
        return out

    def save_full_rain_forecast_grid(
        self,
        lat: float,
        lon: float,
        grid_size_m: float,
        step_m: float,
    ) -> str:
        logger.info(
            "▶️ Starte 24h-Forecast-Raster (lat=%.6f, lon=%.6f, grid_size_m=%.1f, step_m=%.1f)",
            lat, lon, grid_size_m, step_m
        )

        hour_labels = self._build_hour_labels()
        logger.debug("⏱️ Hour-Labels (UTC): %s", hour_labels)

        grid_points = self._forecast_points(lat, lon, grid_size_m, step_m)
        forecasts = self._fetch_forecasts(grid_points)

        if not forecasts:
            raise RuntimeError("Keine Forecasts erhalten – Abbruch.")

        # ✅ Validierung & Float-Konvertierung vor dem Schreiben
        valid_forecasts: List[RainForecast] = []
        for f in forecasts:
            try:
                f.hourly_values = [float(v) for v in f.hourly_values]
                valid_forecasts.append(f)
            except (ValueError, TypeError) as e:
                logger.error(f"❌ Nicht-konvertierbare Werte in Forecast {f.point}: {f.hourly_values} ({e})")

        if not valid_forecasts:
            raise RuntimeError("Keine gültigen Forecasts nach Validierung.")

        # 📂 Zielpfad aus naming.py
        cache_dir = cache_path_for_latlon(lat, lon)
        ensure_dir(cache_dir)
        out_path = os.path.join(cache_dir, rain_grid_csv_name(lat, lon))

        abs_path = write_rain_forecasts_csv(out_path, hour_labels, valid_forecasts)
        logger.info("✅ Forecast-CSV gespeichert: %s", abs_path)
        return abs_path

