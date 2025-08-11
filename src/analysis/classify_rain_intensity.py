# src/analysis/classify_rain_intensity.py
from typing import Dict, List
import re
from datetime import datetime

import pandas as pd
from src.utils.utils_logger import get_logger

logger = get_logger()

# ISO-ähnliche Zeitspalten erkennen: 2025-08-11T17:00
_TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$")


def _detect_time_columns(cols: List[str]) -> List[str]:
    time_cols = [c for c in cols if _TS_RE.match(c)]
    # chronologisch sortieren (falls CSV-Spaltenreihenfolge mal abweicht)
    time_cols.sort(key=lambda c: datetime.strptime(c, "%Y-%m-%dT%H:%M"))
    return time_cols


def _read_rain_series(csv_path: str) -> List[float]:
    """
    Liest die mm/h-Serie aus deiner Raster-CSV.
    Erwartetes Format:
      - Spalten: latitude, longitude, <24x ISO-Timestamps>
      - 1 Zeile (der Punkt)
    """
    logger.debug(f"_read_rain_series(start): csv_path={csv_path}")
    df = pd.read_csv(csv_path)

    if df.empty:
        logger.debug("_read_rain_series: CSV ist leer – gebe leere Serie zurück")
        return []

    cols = list(df.columns)
    time_cols = _detect_time_columns(cols)
    if not time_cols:
        raise KeyError(
            f"Keine Zeitspalten im ISO-Format gefunden. Spalten: {cols}"
        )

    # Nur die erste Zeile (dein Punkt); non-numeric→0.0
    s = pd.to_numeric(df.iloc[0][time_cols], errors="coerce").fillna(0.0)
    vals = s.astype(float).tolist()

    logger.debug(
        "_read_rain_series(done): n=%d, max=%.3f, sum=%.3f",
        len(vals), max(vals) if vals else 0.0, sum(vals) if vals else 0.0
    )
    return vals


def _max_rolling_sum(vals: List[float], window: int) -> float:
    """Maximale gleitende Summe über 'window' Stunden."""
    if window <= 0 or not vals:
        return 0.0
    if len(vals) <= window:
        return float(sum(vals))
    best = cur = float(sum(vals[:window]))
    for i in range(window, len(vals)):
        cur += vals[i] - vals[i - window]
        if cur > best:
            best = cur
    return float(best)


def classify_rain_stage(csv_path: str, thresholds: Dict[str, float]) -> str:
    """
    Feste Priorität (Variante A):
      1) Wassertiefe_SRI10_4h  (4h-Summe >= Schwelle)
      2) Wassertiefe_SRI10_1h  (max mm/h  >= Schwelle)
      3) Wassertiefe_SRI7_1h   (max mm/h  >= Schwelle)
      4) 'none'

    Erwartete thresholds-Keys:
      - "SRI7_THRESHOLD_mm_h"
      - "SRI10_THRESHOLD_mm_h"
      - "SRI10_4H_SUM_THRESHOLD_mm"
    """
    logger.debug("classify_rain_stage(start): csv_path=%s, thresholds=%s", csv_path, thresholds)

    vals = _read_rain_series(csv_path)
    max_mm_h = max(vals) if vals else 0.0
    sum4_mm = _max_rolling_sum(vals, window=4)

    logger.debug(
        "classify_rain_stage(metrics): max_mm_h=%.3f, sum4_mm=%.3f",
        max_mm_h, sum4_mm
    )

    if sum4_mm >= thresholds["SRI10_4H_SUM_THRESHOLD_mm"]:
        return "Wassertiefe_SRI10_4h"
    if max_mm_h >= thresholds["SRI10_THRESHOLD_mm_h"]:
        return "Wassertiefe_SRI10_1h"
    if max_mm_h >= thresholds["SRI7_THRESHOLD_mm_h"]:
        return "Wassertiefe_SRI7_1h"
    return "none"
