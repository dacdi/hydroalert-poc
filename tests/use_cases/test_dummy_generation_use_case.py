from argparse import Namespace
from unittest.mock import patch

from src.use_cases.dummy_generation_use_case import run_dummy_generation_use_case


@patch("src.use_cases.dummy_generation_use_case.generate_dummy_rain_data")
def test_dummy_generation_use_case_calls_generator(mock_generate):
    args = Namespace(variant="SRI7")

    run_dummy_generation_use_case(args)

    mock_generate.assert_called_once_with(variant="SRI7")
