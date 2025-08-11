# src/services/evaluation_service.py
import os
from datetime import datetime, timezone
from typing import Optional, Dict

from src.analysis.classify_rain_intensity import classify_rain_stage
from src.config.config import RAIN_THRESHOLDS
from src.domain.evaluation import EvaluationRecord
from src.io.evaluation_store import save_evaluation
from src.utils.utils_logger import get_logger
from src.utils.naming import cache_path_for_latlon, rain_grid_csv_name  # aus deiner naming.py

logger = get_logger()


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _validate_thresholds(th: Dict[str, float]) -> None:
    required = {"SRI7_THRESHOLD_mm_h", "SRI10_THRESHOLD_mm_h", "SRI10_4H_SUM_THRESHOLD_mm"}
    missing = required.difference(th.keys())
    if missing:
        raise KeyError(f"RAIN_THRESHOLDS fehlen Keys: {sorted(missing)}")


def evaluate_and_store_for_location(
    lat: float,
    lon: float,
    csv_path_override: Optional[str] = None,
) -> EvaluationRecord:
    """
    Führt die Regen-Klassifikation aus und speichert das Ergebnis als evaluation.json
    im Geo-Cache-Ordner (immer Überschreiben).
    """
    logger.debug(
        "evaluate_and_store_for_location(start): "
        f"lat={lat}, lon={lon}, csv_override={csv_path_override}"
    )

    _validate_thresholds(RAIN_THRESHOLDS)

    cache_dir = cache_path_for_latlon(lat, lon)
    csv_path = csv_path_override or os.path.join(cache_dir, rain_grid_csv_name(lat, lon))
    csv_path = os.path.abspath(csv_path)

    logger.debug(f"evaluate_and_store_for_location(paths): cache_dir={cache_dir}, csv={csv_path}")

    layer = classify_rain_stage(csv_path=csv_path, thresholds=RAIN_THRESHOLDS)
    logger.debug(f"evaluate_and_store_for_location(result): layer={layer}")

    record = EvaluationRecord(
        timestamp=_now_utc_iso(),
        layer=layer,
        lat=lat,
        lon=lon,
        source_csv=csv_path,
        thresholds={k: float(v) for k, v in RAIN_THRESHOLDS.items()},
    )

    save_evaluation(cache_dir, record)
    logger.info(f"✅ Empfohlener Layer: {record.layer}")
    return record
