# src/domain/evaluation.py
from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass(frozen=True)
class EvaluationRecord:
    """Persistentes Schema für evaluation.json (keine I/O hier!)."""
    timestamp: str            # ISO 8601, z. B. 2025-08-11T18:42:00Z
    layer: str                # "Wassertiefe_SRI7_1h" | "Wassertiefe_SRI10_1h" | "Wassertiefe_SRI10_4h" | "none"
    lat: float
    lon: float
    source_csv: str           # absoluter Pfad zur Datengrundlage
    thresholds: Dict[str, float]  # dokumentierte Schwellen (aus config)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
