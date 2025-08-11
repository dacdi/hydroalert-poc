# src/analysis/dummy_rain.py
from __future__ import annotations
from typing import List, Dict, Optional
from src.utils.utils_logger import get_logger

logger = get_logger()


def _series_with_peak(
    hours: int,
    peak_value: float,
    peak_hour: int,
) -> List[float]:
    logger.debug(
        "_series_with_peak(start): hours=%s, peak_value=%.3f, peak_hour=%s",
        hours, peak_value, peak_hour
    )
    if hours <= 0:
        logger.debug("_series_with_peak: hours<=0 -> return []")
        return []

    # Peak-Hour in gültigen Bereich clampen
    if peak_hour < 0 or peak_hour >= hours:
        old = peak_hour
        peak_hour = max(0, min(hours - 1, peak_hour))
        logger.debug("_series_with_peak: clamp peak_hour %s -> %s", old, peak_hour)

    vals = [0.0] * hours
    pv = float(max(0.0, peak_value))
    vals[peak_hour] = pv

    logger.debug(
        "_series_with_peak(done): nonzero=%d, max=%.3f@%d",
        sum(1 for v in vals if v > 0.0),
        max(vals) if vals else 0.0,
        peak_hour,
    )
    return vals


def _series_with_4h_window(
    hours: int,
    win_sum: float,
    start_hour: int,
) -> List[float]:
    logger.debug(
        "_series_with_4h_window(start): hours=%s, win_sum=%.3f, start_hour=%s",
        hours, win_sum, start_hour
    )
    if hours <= 0:
        logger.debug("_series_with_4h_window: hours<=0 -> return []")
        return []

    if start_hour < 0:
        logger.debug("_series_with_4h_window: start_hour<0 -> clamp auf 0")
        start_hour = 0

    end = min(start_hour + 4, hours)
    width = end - start_hour
    if width <= 0:
        logger.debug("_series_with_4h_window: width<=0 -> return zeros")
        return [0.0] * hours

    per_h = float(max(0.0, win_sum) / width)
    vals = [0.0] * hours
    for i in range(start_hour, end):
        vals[i] = per_h

    logger.debug(
        "_series_with_4h_window(done): window=[%d,%d) per_h=%.3f sum4h=%.3f",
        start_hour, end, per_h, sum(vals[start_hour:end])
    )
    return vals


def make_dummy_series(
    variant: str,
    thresholds: Dict[str, float],
    hours: int = 24,
    *,
    peak_hour: int = 6,
    window_start_hour: int = 8,
) -> List[float]:
    """
    Erzeugt eine 24h-Serie in mm/h, die die Klassifikationsregeln (Variante A) erfüllt.
    Varianten: "none", "SRI7", "SRI10", "SRI10_4h"

    Debug-Output zeigt: Schwellen, gewählte Peak-/Window-Parameter, resultierende Kennzahlen.
    """
    logger.debug(
        "make_dummy_series(start): variant=%s, hours=%s, peak_hour=%s, window_start=%s",
        variant, hours, peak_hour, window_start_hour
    )

    # Schwellen holen & validieren
    try:
        t7 = float(thresholds["SRI7_THRESHOLD_mm_h"])
        t10 = float(thresholds["SRI10_THRESHOLD_mm_h"])
        t10_4h = float(thresholds["SRI10_4H_SUM_THRESHOLD_mm"])
    except KeyError as e:
        logger.error("Threshold fehlt in config: %s | thresholds=%s", e, thresholds)
        raise

    logger.debug("Thresholds: SRI7=%.3f mm/h, SRI10=%.3f mm/h, SRI10_4h=%.3f mm",
                 t7, t10, t10_4h)

    if hours <= 0:
        logger.warning("hours<=0 (%s) -> gebe leere Serie zurück", hours)
        return []

    vnorm = variant.strip().upper()

    if vnorm == "NONE":
        vals = [0.0] * hours

    elif vnorm == "SRI7":
        # Peak knapp über SRI7, aber unter SRI10 halten (falls SRI10>SRI7)
        if t10 <= t7:
            logger.warning("Unplausible Schwellen (SRI10<=SRI7). Erzwinge Peak = SRI7+1.0")
            peak = t7 + 1.0
        else:
            lower = t7 + 0.5
            upper = t10 - 0.5
            peak = max(lower, min(upper, t7 + 1.0))
        logger.debug("SRI7: chosen peak=%.3f (target in (%.3f .. %.3f))", peak, t7, t10)
        vals = _series_with_peak(hours, peak_value=peak, peak_hour=peak_hour)

    elif vnorm == "SRI10":
        # Peak >= SRI10, aber nur 1h -> 4h-Summe bleibt < t10_4h (typischerweise)
        peak = t10 + 1.0
        logger.debug("SRI10: chosen peak=%.3f at hour=%d", peak, peak_hour)
        vals = _series_with_peak(hours, peak_value=peak, peak_hour=peak_hour)

    elif vnorm in {"SRI10_4H", "SRI10_4H_SUM", "SRI10_4H_TOTAL"}:
        win_sum = t10_4h + 2.0
        logger.debug("SRI10_4h: chosen win_sum=%.3f starting at hour=%d", win_sum, window_start_hour)
        vals = _series_with_4h_window(hours, win_sum=win_sum, start_hour=window_start_hour)

    else:
        logger.error("Unbekannte Dummy-Variante: %s", variant)
        raise ValueError(f"Unbekannte Dummy-Variante: {variant}")

    # Abschluss‑Metriken für Debug
    max_mm_h = max(vals) if vals else 0.0
    # 4h‑Fenster (einfaches max der gleitenden Summe)
    sum4_max = 0.0
    if vals:
        for i in range(len(vals) - 3):
            s = vals[i] + vals[i + 1] + vals[i + 2] + vals[i + 3]
            if s > sum4_max:
                sum4_max = s

    nonzero = sum(1 for v in vals if v > 0.0)
    logger.debug(
        "make_dummy_series(done): nonzero=%d, max_mm_h=%.3f, max_sum4h=%.3f, first10=%s",
        nonzero, max_mm_h, sum4_max, [round(v, 3) for v in vals[:10]]
    )
    return vals
