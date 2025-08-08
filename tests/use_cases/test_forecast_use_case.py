from argparse import Namespace
from unittest.mock import patch

import pytest

from src.use_cases import forecast_use_case


@patch("src.use_cases.forecast_use_case.RainGridForecaster")
def test_forecast_use_case_calls_forecaster(mock_forecaster):
    args = Namespace(lat=49.45, lon=8.18)
    instance = mock_forecaster.return_value

    forecast_use_case.run_forecast_use_case(args)

    mock_forecaster.assert_called_once_with(center_lat=49.45, center_lon=8.18)
    instance.save_full_rain_forecast_grid.assert_called_once_with()


def test_forecast_use_case_missing_coordinates():
    args = Namespace(lat=None, lon=None)
    with pytest.raises(SystemExit):
        forecast_use_case.run_forecast_use_case(args)


def test_prepare_location_if_needed_existing_cache(tmp_path):
    forecast_use_case.CACHE_DIR = str(tmp_path)
    lat, lon = 49.45, 8.18
    cache_dir = tmp_path / f"lat{lat}_lon{lon}"
    cache_dir.mkdir(parents=True)
    (cache_dir / "forecast_24h.csv").write_text("data")
    (cache_dir / "flutkarte.kml").write_text("data")

    with patch(
        "src.use_cases.forecast_use_case.save_forecast_grid_to_cache"
    ) as mock_forecast, patch(
        "src.use_cases.forecast_use_case.save_street_depths_to_cache"
    ) as mock_depths, patch(
        "src.use_cases.forecast_use_case.build_kml_for_location"
    ) as mock_kml:
        forecast_use_case.prepare_location_if_needed(lat, lon)

    mock_forecast.assert_not_called()
    mock_depths.assert_not_called()
    mock_kml.assert_not_called()


def test_prepare_location_if_needed_generates_when_missing(tmp_path):
    forecast_use_case.CACHE_DIR = str(tmp_path)
    lat, lon = 50.0, 8.2
    cache_dir = tmp_path / f"lat{lat}_lon{lon}"
    cache_dir.mkdir(parents=True)
    # Only one file exists
    (cache_dir / "forecast_24h.csv").write_text("data")

    with patch(
        "src.use_cases.forecast_use_case.save_forecast_grid_to_cache"
    ) as mock_forecast, patch(
        "src.use_cases.forecast_use_case.save_street_depths_to_cache"
    ) as mock_depths, patch(
        "src.use_cases.forecast_use_case.build_kml_for_location"
    ) as mock_kml:
        forecast_use_case.prepare_location_if_needed(lat, lon)

    mock_forecast.assert_called_once_with(lat, lon)
    mock_depths.assert_called_once_with(lat, lon)
    mock_kml.assert_called_once_with(lat, lon)
