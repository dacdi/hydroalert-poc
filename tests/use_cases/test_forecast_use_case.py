from argparse import Namespace
from unittest.mock import patch

import pytest

from src.use_cases.forecast_use_case import run_forecast_use_case


@patch("src.use_cases.forecast_use_case.RainGridForecaster")
def test_forecast_use_case_calls_forecaster(mock_forecaster):
    args = Namespace(lat=49.45, lon=8.18)
    instance = mock_forecaster.return_value

    run_forecast_use_case(args)

    mock_forecaster.assert_called_once_with(center_lat=49.45, center_lon=8.18)
    instance.save_full_rain_forecast_grid.assert_called_once_with()


def test_forecast_use_case_missing_coordinates():
    args = Namespace(lat=None, lon=None)
    with pytest.raises(SystemExit):
        run_forecast_use_case(args)
