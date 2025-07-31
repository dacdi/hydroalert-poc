# tests/analysis/test_forecast_area.py

import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

import pytest
from unittest.mock import patch

from src.analysis.forecast_area import save_full_rain_forecast_grid


@pytest.fixture
def dummy_data() -> Dict:
    """Provides dummy forecast data with hourly precipitation and time values."""
    base_time = datetime.now().replace(minute=0, second=0, microsecond=0)
    times = [
        (base_time + timedelta(hours=i)).strftime("%Y-%m-%dT%H:00") for i in range(24)
    ]
    precipitation = [float(i) for i in range(24)]
    return {
        "hourly": {
            "time": times,
            "precipitation": precipitation,
        }
    }


@patch("src.analysis.forecast_area.fetch_forecast_data")
def test_save_full_grid_with_mock(mock_fetch, tmp_path: Path, dummy_data: Dict):
    """
    Tests whether the forecast grid is saved correctly using dummy weather data.
    """
    # Mock fetch_forecast_data to return our dummy_data for every grid point
    mock_fetch.return_value = dummy_data

    # Define output path inside pytest's temp directory
    output_file = tmp_path / "mock_rain_grid.csv"

    # Call the function under test
    save_full_rain_forecast_grid(
        output_path=str(output_file),
        center_lat=49.35,
        center_lon=8.15,
        radius_km=1,  # small grid for fast test
        step_km=1,
        delay=0  # skip sleep for speed
    )

    # Assertions
    assert output_file.exists()

    with open(output_file, newline="") as f:
        reader = list(csv.reader(f))

        # Check header
        expected_header = ["latitude", "longitude"] + dummy_data["hourly"]["time"][:24]
        assert reader[0] == expected_header

        # Check that we have at least one data row
        assert len(reader) > 1
        assert len(reader[1]) == 26  # 2 for lat/lon + 24 values
