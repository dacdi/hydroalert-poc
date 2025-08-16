# src/io/rain_csv_store.py
import os
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

from src.utils.utils_logger import get_logger

logger = get_logger()

try:
    # Signatur: write_rain_forecasts_csv(path, hour_labels, rows)
    # rows: Iterable[RainForecast | Tuple[float, float, list[float]]]
    from src.io.csv_writer import write_rain_forecasts_csv as _write_csv  # type: ignore
except Exception as exc:  # pragma: no cover
    _write_csv = None
    logger.warning("csv_writer nicht verfügbar: %s", exc)


def _hourly_iso_series(start: datetime, hours: int) -> List[str]:
    # ISO ohne Sekunden: YYYY-MM-DDTHH:MM
    return [(start + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(hours)]


def save_rain_grid_csv(
    path: str,
    lat: float,
    lon: float,
    hourly_values: List[float],
    start_utc: datetime | None = None,
) -> Tuple[str, List[str]]:
    """
    Speichert eine Raster-CSV über den projektspezifischen csv_writer.

    Gibt (abspath, hour_labels) zurück.
    """
    logger.debug(
        "save_rain_grid_csv(start): path=%s lat=%s lon=%s n_values=%d",
        path, lat, lon, len(hourly_values)
    )
    os.makedirs(os.path.dirname(path), exist_ok=True)

    start = start_utc or datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    hour_labels = _hourly_iso_series(start, len(hourly_values))

    # Sicherheitscheck: Länge der Labels == Länge der Werte
    if len(hour_labels) != len(hourly_values):
        raise ValueError(
            f"Längen-Mismatch: hour_labels={len(hour_labels)} vs hourly_values={len(hourly_values)}"
        )

    abspath = os.path.abspath(path)

    if _write_csv is None:
        # Harte Abbruch, weil dein Projekt den Writer standardisiert nutzt
        raise RuntimeError("csv_writer.write_rain_forecasts_csv ist nicht verfügbar.")

    # Übergabe im erwarteten Format: [(lat, lon, [werte...])]
    rows = [(float(lat), float(lon), [float(v) for v in hourly_values])]
    _write_csv(abspath, hour_labels, rows)

    logger.info("💾 Dummy-Rain CSV gespeichert: %s", abspath)
    return abspath, hour_labels
