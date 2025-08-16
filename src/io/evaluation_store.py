# src/io/evaluation_store.py
import json
import os
from typing import Tuple

from src.domain.evaluation import EvaluationRecord
from src.utils.utils_logger import get_logger

logger = get_logger()

EVALUATION_FILENAME = "evaluation.json"


def evaluation_path(cache_dir: str) -> str:
    return os.path.join(cache_dir, EVALUATION_FILENAME)


def save_evaluation(cache_dir: str, record: EvaluationRecord) -> str:
    """Schreibt evaluation.json (immer überschreiben)."""
    logger.debug(f"save_evaluation(start): cache_dir={cache_dir}, record={record}")
    os.makedirs(cache_dir, exist_ok=True)
    path = evaluation_path(cache_dir)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record.to_dict(), f, ensure_ascii=False, indent=2)
    logger.info(f"💾 Evaluation gespeichert: {path}")
    return path


def load_evaluation(cache_dir: str) -> Tuple[EvaluationRecord, str]:
    """Reader (optional für spätere Nutzung)."""
    path = evaluation_path(cache_dir)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    rec = EvaluationRecord(**data)
    logger.debug(f"load_evaluation: loaded={rec}")
    return rec, path
