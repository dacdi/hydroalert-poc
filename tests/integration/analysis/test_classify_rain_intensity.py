import pytest
import tempfile
import os
from src.analysis.classify_rain_intensity import classify_rain_stage

# Dummy-Header und 24h-Zeitpunkte
HEADER = ["lat", "lon"] + [f"hour_{i}" for i in range(24)]


def write_csv(path: str, rows: list[list[str]]) -> None:
    with open(path, "w", newline="") as f:
        f.write(",".join(HEADER) + "\n")
        for row in rows:
            f.write(",".join(str(x) for x in row) + "\n")


def test_classifies_sri10_correctly():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tmp:
        rows = [[49.0, 8.0] + [30] * 24 for _ in range(100)]  # 100 Punkte über SRI10
        write_csv(tmp.name, rows)
        result = classify_rain_stage(tmp.name)
        assert result == "Wassertiefe_SRI10_1h"
    os.remove(tmp.name)


def test_classifies_sri7_correctly():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tmp:
        rows = [[49.0, 8.0] + [20] + [0] * 23 for _ in range(100)]  # 100 Punkte über SRI7, aber unter SRI10_4h
        write_csv(tmp.name, rows)
        result = classify_rain_stage(tmp.name)
        assert result == "Wassertiefe_SRI7_1h"
    os.remove(tmp.name)


def test_classifies_schummerung_when_insufficient_rain():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tmp:
        rows = [[49.0, 8.0] + [5] * 24 for _ in range(100)]  # zu wenig Regen
        write_csv(tmp.name, rows)
        result = classify_rain_stage(tmp.name)
        assert result == "Schummerung"
    os.remove(tmp.name)


def test_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        classify_rain_stage("non_existent_file.csv")


def test_raises_if_csv_has_no_valid_data():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tmp:
        tmp.write(",".join(HEADER) + "\n")  # nur Header, keine Daten
        tmp_path = tmp.name
    with pytest.raises(ValueError, match="rainfall data.*CSV"):
        classify_rain_stage(tmp_path)
    os.remove(tmp_path)
